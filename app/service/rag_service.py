import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GOOGLE_API_KEY)
        self.vector_store_path = settings.DATABASE_DIR
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GOOGLE_API_KEY, temperature=0.3)
        # Initialize vector store (load if exists, otherwise it will be created on ingestion)
        self.vector_store = Chroma(
            persist_directory=self.vector_store_path,
            embedding_function=self.embeddings
        )

    def ingest_documents(self, directory_path: str):
        """
        Ingests all PDF documents from the specified directory.
        """
        documents = []
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist.")
            return

        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded {filename}")

        if not documents:
            print("No documents found to ingest.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        # Add to vector store
        self.vector_store.add_documents(documents=splits)
        print(f"Ingested {len(splits)} chunks into ChromaDB.")

    def ask_question(self, question: str) -> str:
        """
        Retrieves relevant context and answers the question.
        """
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": question})
        return response["answer"]

# Global instance
rag_service = RAGService()
