from app.service.pdf_service import PDFProcessor
import os

if __name__ == "__main__":
    data_path = "./data" 
    print("--- ĐANG KIỂM TRA HỆ THỐNG ĐỌC FILE ---")
    
    # Khởi tạo bộ quét file
    processor = PDFProcessor(data_folder=data_path)
    
    # Chạy quét và lấy dữ liệu
    documents = processor.process_all_pdfs() 
    
    if documents:
        print(f"✅ THÀNH CÔNG: Đã đọc được {len(documents)} trang từ các file PDF.")
    else:
        print("❌ THẤT BẠI: Không có dữ liệu nào được trích xuất.")