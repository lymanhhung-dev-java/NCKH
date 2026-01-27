import os
import time
import hashlib
import json
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.service.embedding_service import ChunkingPresets

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
        
        # Khởi tạo ChunkingService (tách bạch trách nhiệm)
        # Có thể sử dụng preset: ChunkingPresets.vietnamese_optimized() (mặc định)
        self.chunking_service = ChunkingPresets.vietnamese_optimized()
        
        # File ghi nhật ký những tài liệu đã nạp
        self.ingestion_log_file = "./database/ingestion_log.json"
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self):
        """Đảm bảo file log tồn tại"""
        log_dir = os.path.dirname(self.ingestion_log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        if not os.path.exists(self.ingestion_log_file):
            with open(self.ingestion_log_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Tính hash của file để kiểm tra trùng lặp"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _load_ingestion_log(self) -> dict:
        """Tải danh sách những file đã nạp"""
        try:
            with open(self.ingestion_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_ingestion_log(self, log_data: dict):
        """Lưu danh sách những file đã nạp"""
        with open(self.ingestion_log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def _is_document_already_ingested(self, file_path: str) -> bool:
        """Kiểm tra xem document đã được nạp chưa"""
        file_hash = self._calculate_file_hash(file_path)
        log_data = self._load_ingestion_log()
        return file_hash in log_data
    
    def _mark_document_as_ingested(self, file_path: str):
        """Đánh dấu document đã được nạp"""
        file_hash = self._calculate_file_hash(file_path)
        log_data = self._load_ingestion_log()
        
        filename = os.path.basename(file_path)
        log_data[file_hash] = {
            'filename': filename,
            'file_path': file_path,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'chunk_size': self.chunking_service.chunk_size,
            'chunk_overlap': self.chunking_service.chunk_overlap,
            'chunk_overlap_percent': f"{self.chunking_service.chunk_overlap_percent*100:.0f}%"
        }
        
        self._save_ingestion_log(log_data)

    def ingest_documents(self, directory_path: str):
        """
        Nạp PDF vào Vector Database với xử lý trùng lặp
        
        Cấu hình tối ưu (từ test results):
        - chunk_size: 1000 ký tự (mức trung bình tối ưu)
        - chunk_overlap: 180 ký tự (18% - giữ ngữ cảnh Điều/Khoản)
        - separators: ["\n\n", "\n", ". ", " ", ""] (ưu tiên đoạn → dòng → câu → từ)
        """
        documents = []
        skipped_files = 0
        
        if not os.path.exists(directory_path):
            print(f"❌ Lỗi: Thư mục {directory_path} không tồn tại.")
            return

        print("📥 Kiểm tra tài liệu trùng lặp...")
        
        # 1. Nạp file PDF (với kiểm tra trùng lặp)
        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory_path, filename)
                
                # Kiểm tra xem document đã được nạp chưa
                if self._is_document_already_ingested(file_path):
                    print(f"⏭️  Bỏ qua: {filename} (đã nạp rồi)")
                    skipped_files += 1
                    continue
                
                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    
                    # Cập nhật metadata
                    for doc in docs:
                        doc.metadata["source"] = filename
                    
                    documents.extend(docs)
                    
                    # Đánh dấu file đã nạp
                    self._mark_document_as_ingested(file_path)
                    print(f"✅ Đã đọc: {filename}")
                    
                except Exception as e:
                    print(f"❌ Lỗi file {filename}: {e}")
        
        if skipped_files > 0:
            print(f"\n📊 Tómlại: Bỏ qua {skipped_files} file đã nạp trước đó")

        if not documents:
            if skipped_files > 0:
                print("💡 Tất cả file đã được nạp rồi. Không có gì mới để xử lý.")
            else:
                print("❌ Không tìm thấy tài liệu nào.")
            return

        # 2. Chunking khoa học (sử dụng ChunkingService)
        print(f"\n✂️  Đang cắt nhỏ văn bản...")
        splits = self.chunking_service.split_documents(documents)
        total_chunks = len(splits)
        
        print(f"\n📦 Tổng cộng: {total_chunks} đoạn văn bản.")
        print(f"⚙️  Cấu hình Chunking:")
        print(f"   - chunk_size: {self.chunking_service.chunk_size} ký tự")
        print(f"   - chunk_overlap: {self.chunking_service.chunk_overlap} ký tự ({self.chunking_service.chunk_overlap_percent*100:.0f}%) - TỐI ƯU")
        print(f"   - separators: {self.chunking_service.separators}")
        print(f"   - Mục đích: Giữ ngữ cảnh Điều/Khoản không bị cắt quãng")

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