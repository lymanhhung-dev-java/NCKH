"""
📋 HƯỚNG DẪN: CHUNK_OVERLAP & XỬ LÝ TRÙNG LẶP

Đã cập nhật app/service/rag_service.py với:
1. Cấu hình chunk_overlap tối ưu: 180 ký tự (18% của 1000)
2. Xử lý trùng lặp document dựa trên file hash
"""

print("=" * 100)
print("📋 HƯỚNG DẪN: CHUNK_OVERLAP & XỬ LÝ TRÙNG LẬP")
print("=" * 100)

print("""
✅ CẤU HÌNH ĐÃ CẬP NHẬT:

class RAGService:
    def __init__(self):
        # Cấu hình Chunk (Dựa trên test results)
        self.CHUNK_SIZE = 1000          # Mức trung bình tối ưu
        self.CHUNK_OVERLAP = 180        # 18% của 1000 = 180 ký tự
        self.SEPARATORS = [
            "\\n\\n",  # 1️⃣  Ưu tiên: Ngắt theo đoạn văn
            "\\n",     # 2️⃣  Sau đó: Ngắt theo dòng
            ". ",      # 3️⃣  Rồi: Ngắt theo câu (dấu chấm + khoảng)
            " ",       # 4️⃣  Cuối: Ngắt theo từ (khoảng trắng)
            ""         # 5️⃣  Cuối cùng: Ngắt từng ký tự
        ]

""")

print("=" * 100)
print("🎯 MỤC ĐÍCH CỦA CHUNK_OVERLAP = 180")
print("=" * 100)

print("""
┌─────────────────────────────────────────────────────────────────────────┐
│ VẤNĐỀ: Khi cắt text thành chunks, các thông tin quan trọng ở "mối nối"  │
│        có thể bị cắt quãng hoặc mất context.                            │
│                                                                         │
│ VÍ DỤ:                                                                  │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐      │
│  │ CHUNK 1 (Kết thúc)          │  │ CHUNK 2 (Bắt đầu)          │      │
│  │                             │  │                             │      │
│  │ ...Khoản 2.3: Yêu cầu bảo   │  │ ? Không biết là nội dung   │      │
│  │ mật dữ liệu quan trọng...   │  │ của Khoản nào!             │      │
│  │                             │  │                             │      │
│  └─────────────────────────────┘  └─────────────────────────────┘      │
│            ❌ Mất context             ❌ AI bị bối rối                   │
│                                                                         │
│ GIẢI PHÁP: Overlap = 180 ký tự (18%)                                   │
│                                                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐      │
│  │ CHUNK 1 (Kết thúc)          │  │ CHUNK 2 (Bắt đầu)          │      │
│  │                             │  │                             │      │
│  │ ...Khoản 2.3: Yêu cầu bảo   │  │ Khoản 2.3: Yêu cầu bảo      │      │
│  │ mật dữ liệu quan trọng...   │  │ mật dữ liệu quan trọng...   │      │
│  │ (180 ký tự lặp lại)         │  │ (Nội dung tiếp)            │      │
│  │                             │  │                             │      │
│  └─────────────────────────────┘  └─────────────────────────────┘      │
│      ✅ Giữ context                   ✅ AI hiểu được mối liên hệ      │
│      ✅ Thông tin lặp lại ở mối nối  ✅ Trả lời chính xác hơn         │
└─────────────────────────────────────────────────────────────────────────┘
""")

print("=" * 100)
print("🔐 XỬ LÝ TRÙNG LẬP DOCUMENT")
print("=" * 100)

print("""
✅ CÁCH HOẠT động:

1. LẦN ĐẦU TIÊN NẠP FILE:
   - Tính SHA-256 hash của file PDF
   - Lưu hash vào ./database/ingestion_log.json
   - Nạp document vào Vector Store
   
   Example ingestion_log.json:
   {
     "a1b2c3d4...": {
       "filename": "quy_dinh_1.pdf",
       "file_path": "./data/quy_dinh_1.pdf",
       "timestamp": "2026-01-27 10:30:45",
       "chunk_size": 1000,
       "chunk_overlap": 180
     }
   }

2. LẦN CHẠY LẠI SCRIPT:
   - Tính hash của file mới
   - So sánh với hash trong log
   - Nếu KHÁC → Nạp vào (file mới hoặc có sửa)
   - Nếu GIỐNG → Bỏ qua (đã nạp rồi)

3. LỢI ÍCH:
   ✅ Không nạp trùng cùng file nhiều lần
   ✅ Tự động phát hiện file đã sửa đổi
   ✅ Giảm nhiễu dữ liệu trong Vector Store
   ✅ Tiết kiệm thời gian và tài nguyên
""")

print("=" * 100)
print("📝 CÓ THỂ XEM LẠI FILE LOG:")
print("=" * 100)

print("""
Sau khi chạy python ingest_data.py, kiểm tra:
   cat ./database/ingestion_log.json
   
hoặc trong Python:
   import json
   with open('./database/ingestion_log.json', 'r') as f:
       log = json.load(f)
       print(json.dumps(log, ensure_ascii=False, indent=2))
""")

print("=" * 100)
print("🧪 KIỂM TRA HOẠT ĐỘNG:")
print("=" * 100)

print("""
BƯỚC 1: Chạy lần 1
   $ python ingest_data.py
   
   Output:
   ✅ Đã đọc: quy_dinh_1.pdf
   ✅ Đã đọc: quy_dinh_2.pdf
   ...

BƯỚC 2: Chạy lần 2 (cùng file)
   $ python ingest_data.py
   
   Output:
   ⏭️  Bỏ qua: quy_dinh_1.pdf (đã nạp rồi)
   ⏭️  Bỏ qua: quy_dinh_2.pdf (đã nạp rồi)
   💡 Tất cả file đã được nạp rồi. Không có gì mới để xử lý.

BƯỚC 3: Thêm file mới vào /data
   $ python ingest_data.py
   
   Output:
   ⏭️  Bỏ qua: quy_dinh_1.pdf (đã nạp rồi)
   ✅ Đã đọc: quy_dinh_3.pdf (file mới)
   ...
""")

print("=" * 100)
print("📊 BẢNG TÓMLẠI CẤU HÌNH")
print("=" * 100)

summary = """
┌──────────────────┬────────────┬─────────────────────────────────────────┐
│ Thông số         │ Giá trị    │ Giải thích                              │
├──────────────────┼────────────┼─────────────────────────────────────────┤
│ chunk_size       │ 1000       │ Độ dài mỗi đoạn văn bản (ký tự)        │
│ chunk_overlap    │ 180        │ Phần lặp lại giữa các chunks (18%)      │
│ separators[0]    │ \\n\\n       │ Ưu tiên cắt tại đoạn văn (tốt nhất)    │
│ separators[1]    │ \\n        │ Cắt tại dòng mới (thứ 2)                │
│ separators[2]    │ \". \"      │ Cắt tại câu (dấu chấm + khoảng)        │
│ separators[3]    │ \" \"      │ Cắt tại khoảng trắng (giữa từ)         │
│ separators[4]    │ \"\"        │ Cắt từng ký tự (cuối cùng)             │
│ duplicate check   │ SHA-256    │ Kiểm tra file hash để tránh trùng      │
│ log file          │ .json      │ Lưu danh sách file đã nạp              │
└──────────────────┴────────────┴─────────────────────────────────────────┘
"""
print(summary)

print("""
✅ KẾT LUẬN:
   Cấu hình này đảm bảo:
   1. ✅ Ngữ cảnh không bị cắt quãng (overlap = 180)
   2. ✅ Không nạp trùng file (kiểm tra hash)
   3. ✅ Tích hợp tự động (RecursiveCharacterTextSplitter)
   4. ✅ Tối ưu cho tiếng Việt (separators)
""")

print("=" * 100)
