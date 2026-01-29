from app.service.rag_service import rag_service
import os

if __name__ == "__main__":
    data_path = "./data" 
    print("--- ĐANG KIỂM TRA HỆ THỐNG ĐỌC FILE VÀ LƯU VÀO CHROMADB ---")
    
    # Chạy quét và nạp dữ liệu vào ChromaDB
    # Hàm này đã bao gồm logic: đọc PDF -> check trùng -> chunking -> vector store
    rag_service.ingest_documents(directory_path=data_path)
    
    print("\n--- HOÀN TẤT QUÁ TRÌNH ---")