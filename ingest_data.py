from app.service.rag_service import rag_service
import os

if __name__ == "__main__":
    # Đường dẫn đến thư mục chứa các file PDF của trường
    data_path = "./data" 
    
    print("--- Bắt đầu quá trình nạp dữ liệu ---")
    rag_service.ingest_documents(data_path)
    print("--- Hoàn tất! Dữ liệu đã được lưu vào Database ---")