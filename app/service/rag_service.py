import os
import time
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

class RAGService:
    def __init__(self):
        # Khởi tạo AI và Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
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
        """Nhiệm vụ Tuần 2 & 3: Xử lý PDF và Đẩy vào Vector DB (Đã fix lỗi 429)"""
        documents = []
        if not os.path.exists(directory_path):
            print(f"❌ Lỗi: Thư mục {directory_path} không tồn tại.")
            return

        # 1. Nạp file PDF
        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                    print(f"✅ Đã đọc: {filename}")
                except Exception as e:
                    print(f"❌ Lỗi file {filename}: {e}")

        if not documents:
            print("❌ Không tìm thấy tài liệu nào.")
            return

        # 2. Chunking khoa học
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        total_chunks = len(splits)
        print(f"📦 Tổng cộng: {total_chunks} đoạn văn bản.")

# 3. Nạp vào Vector DB theo chế độ "An Toàn Tuyệt Đối"
        batch_size = 1 
        print(f"🚀 Đang nạp từng bước (Cực chậm) để tránh bị chặn...")
        
        for i in range(0, total_chunks, batch_size):
            batch = splits[i:i + batch_size]
            try:
                self.vector_store.add_documents(documents=batch)
                print(f"   ➤ Đã nạp thành công: {i + 1}/{total_chunks}")
                time.sleep(10)  # Nghỉ 10 giây mỗi đoạn
            except Exception as e:
                print(f"⚠️ Đang đợi 60 giây do Google quá tải: {e}")
                time.sleep(60)
                self.vector_store.add_documents(documents=batch)

    def ask_question(self, question: str) -> str:
        """Nhiệm vụ Tuần 4: Truy vấn thông minh"""
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
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

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": question})
        return response["answer"]

rag_service = RAGService()