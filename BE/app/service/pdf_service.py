import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

class PDFProcessor:
    def __init__(self, data_folder="data/"):
        """
        [Checklist] Khởi tạo Class PDFProcessor: Tách biệt logic xử lý file.
        """
        self.data_folder = Path(data_folder)
        # [Checklist] Khởi tạo hai danh sách để ghi log trạng thái
        self.success_files = []
        self.failed_files = []
        self.all_docs = []

    def process_all_pdfs(self):
        """
        [Checklist] Quét thư mục tự động và lọc file .pdf
        """
        if not self.data_folder.exists():
            print(f"❌ Thư mục '{self.data_folder}' không tồn tại.")
            return []

        # Chỉ lọc ra các file có đuôi .pdf
        pdf_files = list(self.data_folder.glob("*.pdf"))

        if not pdf_files:
            print(f"⚠️ Không tìm thấy file PDF nào trong '{self.data_folder}'.")
            return []

        print(f"🔄 Bắt đầu quét {len(pdf_files)} file PDF...")

        for pdf_path in pdf_files:
            # [Checklist] Cấu hình xử lý lỗi (Error Handling) cho mỗi file
            try:
                # Gọi hàm nội bộ để load file
                pages = self._load_single_pdf(pdf_path)
                
                if pages:
                    self.all_docs.extend(pages)
                    self.success_files.append(pdf_path.name)
                    print(f"✅ Đã đọc thành công: {pdf_path.name}")
                
            except Exception as e:
                # Nếu một file bị lỗi, bỏ qua và tiếp tục nạp file tiếp theo
                self.failed_files.append({
                    "file": pdf_path.name,
                    "reason": str(e)
                })
                print(f"❌ Lỗi tại file {pdf_path.name}: {str(e)}")

        # [Checklist] In bảng thống kê chi tiết sau khi quét xong
        self._print_final_report()
        return self.all_docs

    def _load_single_pdf(self, file_path):
        """
        Logic trích xuất dữ liệu bằng thư viện PyPDFLoader.
        """
        if os.path.getsize(file_path) == 0:
            raise Exception("File trống (0 KB)")

        loader = PyPDFLoader(str(file_path))
        return loader.load()

    def _print_final_report(self):
        """
        [Checklist] Hệ thống Ghi log: In bảng thống kê tổng số file.
        """
        print("\n" + "="*50)
        print("📊 BÁO CÁO HOÀN TẤT NẠP DỮ LIỆU")
        print("="*50)
        print(f"✔️ Thành công: {len(self.success_files)} file")
        print(f"✖️ Thất bại:   {len(self.failed_files)} file")
        print(f"📦 Tổng cộng:  {len(self.all_docs)} đoạn văn bản đã sẵn sàng.")
        print("-" * 50)

        if self.failed_files:
            print("Chi tiết lỗi:")
            for item in self.failed_files:
                print(f"  - {item['file']}: {item['reason']}")
        
        if self.success_files:
            print(f"Danh sách file oki: {', '.join(self.success_files)}")
        print("="*50 + "\n")

if __name__ == "__main__":
    # Test nhanh tại chỗ
    processor = PDFProcessor()
    processor.process_all_pdfs()