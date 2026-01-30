"""
📚 HƯỚNG DẪN: EMBEDDING_SERVICE.PY

Đã tách riêng phần Chunking & Embedding vào embedding_service.py
Giúp tách bạch trách nhiệm (Separation of Concerns)
"""

import json

print("=" * 100)
print("📚 HƯỚNG DẪN: EMBEDDING_SERVICE.PY - Tách bạch Chunking & Embedding")
print("=" * 100)

guide = """
🎯 ĐIỀU GỲ ĐƯỢC THAY ĐỔI:

TRƯỚC:
├── rag_service.py (Quản lý: RAG chain + Chunking + Embeddings)
└── ❌ Quá nhiều trách nhiệm trong 1 file

SAU:
├── rag_service.py (Chỉ: RAG chain & truy vấn) ✅
└── embedding_service.py (Chỉ: Chunking & Overlap) ✅
                         Embeddings (về sau)

================================================================================
📝 FILE CẤU TRÚC:
================================================================================

app/service/
├── __init__.py
├── rag_service.py ✅ (Cập nhật: sử dụng ChunkingService)
├── embedding_service.py ✅ (NEW)
│   ├── ChunkingService (Lớp chính)
│   └── ChunkingPresets (Cấu hình presets)
└── embedding_log.json (Log những documents đã nạp)

================================================================================
🚀 CÁCH SỬ DỤNG:
================================================================================

1️⃣  SỬ DỤNG PRESET (Khuyến nghị):
    
    from app.service.embedding_service import ChunkingPresets
    
    # Cấu hình tối ưu cho tiếng Việt (mặc định)
    chunker = ChunkingPresets.vietnamese_optimized()
    
    # Hoặc các preset khác:
    chunker_fast = ChunkingPresets.fast_retrieval()        # Chunks ngắn
    chunker_context = ChunkingPresets.context_rich()       # Chunks dài
    chunker_balanced = ChunkingPresets.balanced()          # Cân bằng

2️⃣  SỬ DỤNG TRỰC TIẾP:
    
    from app.service.embedding_service import ChunkingService
    
    # Cấu hình tối ưu mặc định
    chunker = ChunkingService()
    
    # Hoặc tùy chỉnh
    chunker = ChunkingService(
        chunk_size=1000,
        chunk_overlap_percent=0.18,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

3️⃣  CẮT DOCUMENTS:
    
    from langchain_community.document_loaders import PyPDFLoader
    
    loader = PyPDFLoader("file.pdf")
    docs = loader.load()
    
    chunker = ChunkingService()
    chunks = chunker.split_documents(docs)  # Cắt Document objects
    
4️⃣  CẮT TEXT THỎ:
    
    text = "Nội dung văn bản..."
    chunker = ChunkingService()
    chunks = chunker.split_text(text)  # Cắt string

5️⃣  CẤU HÌNH LẠI:
    
    chunker = ChunkingService()
    chunker.configure(chunk_size=1500, chunk_overlap_percent=0.20)
    chunks = chunker.split_text("...")

6️⃣  LẤY THỐNG KÊ:
    
    chunker = ChunkingService()
    chunks = chunker.split_text("...")
    
    # In thống kê đẹp
    chunker.print_statistics()
    
    # Hoặc lấy dict
    stats = chunker.get_statistics()
    print(f"Tổng chunks: {stats['chunk_count']}")

================================================================================
📊 BẢNG PRESETS:
================================================================================

Preset                  chunk_size  overlap   overlap%  Mục đích
────────────────────────────────────────────────────────────────────────────
vietnamese_optimized()      1000      180      18%     ⭐ Khuyến nghị
fast_retrieval()            500       75       15%     Truy xuất nhanh
context_rich()              1500      300      20%     Giữ context tốt
balanced()                  1000      150      15%     Cân bằng

================================================================================
🔧 CẤU HÌNH CHI TIẾT:
================================================================================

ChunkingService(
    chunk_size: int = 1000              # Độ dài mỗi chunk (ký tự)
    chunk_overlap_percent: float = 0.18 # Tỷ lệ overlap (0-1)
    separators: List[str] = [           # Dấu ngắt ưu tiên
        "\\n\\n",  # 1. Ngắt theo đoạn (TỐT NHẤT)
        "\\n",     # 2. Ngắt theo dòng
        ". ",      # 3. Ngắt theo câu
        " ",       # 4. Ngắt theo từ
        ""         # 5. Ngắt từng ký tự (CUỐI CÙNG)
    ]
)

================================================================================
✅ PHƯƠNG THỨC CHÍNH:
================================================================================

split_documents(docs: List[Document]) -> List[Document]
    Cắt Document objects từ PDF Loader
    Giữ nguyên metadata

split_text(text: str) -> List[str]
    Cắt text thô (string)
    Trả về danh sách string

configure(chunk_size, chunk_overlap_percent, separators)
    Cấu hình lại ChunkingService
    Tạo lại splitter

get_statistics() -> Dict
    Lấy thống kê lần cắt cuối
    Includes: chunk_count, avg_size, etc.

print_statistics()
    In thống kê dưới dạng bảng đẹp
    Dùng cho debug

get_config_info() -> str
    Lấy thông tin cấu hình hiện tại

================================================================================
💡 LỢI ÍCH CỦA TÁCH BẠCH:
================================================================================

1. ✅ SỬA ĐỔI DỄ DÀNG
   - Thay đổi chunking không ảnh hưởng RAG chain
   - Thêm loại splitter mới không cần sửa rag_service.py

2. ✅ TÍCH HỢP LẠI
   - Có thể sử dụng ChunkingService ở các service khác
   - Reusable cho các project khác

3. ✅ TEST DỄ DÀNG
   - Test chunking riêng biệt không cần setup RAG
   - File test_overlap_integrity.py chỉ test embedding_service

4. ✅ MAINTENANCE
   - Code sạch sẽ, dễ đọc
   - Trách nhiệm rõ ràng (Single Responsibility)
   - Dễ debug khi có vấn đề

================================================================================
🔗 INTEGRATION VỚI RAG_SERVICE:
================================================================================

# Trong rag_service.py
from app.service.embedding_service import ChunkingPresets

class RAGService:
    def __init__(self):
        # ...
        # Khởi tạo ChunkingService
        self.chunking_service = ChunkingPresets.vietnamese_optimized()
    
    def ingest_documents(self, directory_path):
        # ...
        # Sử dụng chunking service
        splits = self.chunking_service.split_documents(documents)

================================================================================
🧪 TEST:
================================================================================

Chạy test embedding_service:
    $ python app/service/embedding_service.py

Output:
    ✅ TEST: Cấu hình tối ưu (Mặc định)
    ✅ TEST: Sử dụng Preset - Fast Retrieval
    ✅ TEST: Cấu hình lại ChunkingService

================================================================================
📋 TIẾP THEO:
================================================================================

1. Thêm EmbeddingService (chuyên trách tạo embeddings)
2. Thêm RetrievalService (chuyên trách truy xuất)
3. Refactor rag_service.py để chỉ quản lý RAG chain

Kết quả:
    embedding_service.py → Chunking + Embedding
    retrieval_service.py → Retrieval + Search
    rag_service.py → RAG Chain + Orchestration
"""

print(guide)

print("\n" + "=" * 100)
print("✅ HƯỚNG DẪN HOÀN TẤT!")
print("=" * 100)
