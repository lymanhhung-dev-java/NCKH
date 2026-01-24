import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma

# Sửa lỗi ModuleNotFoundError: Trỏ trực tiếp vào đường dẫn mới nhất
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

class RAGService:
    def __init__(self):
        # Khởi tạo AI và Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            google_api_key=settings.GOOGLE_API_KEY, 
            temperature=0.3
        )
        # Khởi tạo Vector Store với tính năng lưu trữ vĩnh viễn
        self.vector_store = Chroma(
            persist_directory=settings.DATABASE_DIR,
            embedding_function=self.embeddings
        )

    def ingest_documents(self, directory_path: str):
        """Nhiệm vụ Tuần 2: Xử lý PDF và Metadata"""
        documents = []
        if not os.path.exists(directory_path):
            print(f"Lỗi: Thư mục {directory_path} không tồn tại.")
            return

        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                loader = PyPDFLoader(file_path)
                # loader.load() tự động gán metadata là tên file và số trang
                docs = loader.load()
                documents.extend(docs)
                print(f"✅ Đã nạp: {filename}")

        if not documents:
            print("❌ Không tìm thấy tài liệu nào.")
            return

        # Nhiệm vụ Tuần 2: Chunking khoa học
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""] # Ngắt câu thông minh
        )
        splits = text_splitter.split_documents(documents)
        
        # Nhiệm vụ Tuần 3: Đẩy vào Vector DB
        self.vector_store.add_documents(documents=splits)
        print(f"🚀 Đã số hóa {len(splits)} đoạn văn bản vào ChromaDB.")

    def ask_question(self, question: str) -> str:
        """Nhiệm vụ Tuần 4: Truy vấn thông minh"""
        # Retrieval: Lấy 5 đoạn liên quan nhất
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # System Prompt chuyên nghiệp cho trường học
        system_prompt = (
            "Bạn là trợ lý ảo hỗ trợ sinh viên dựa trên tài liệu nội bộ của nhà trường. "
            "Chỉ sử dụng các đoạn văn bản dưới đây để trả lời câu hỏi. "
            "Nếu thông tin không có trong tài liệu, hãy nói 'Tôi không biết'. "
            "Câu trả lời cần ngắn gọn, chính xác và lịch sự."
            "\n\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # Kết nối các mảnh ghép RAG
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": question})
        return response["answer"]

rag_service = RAGService()