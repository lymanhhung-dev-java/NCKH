"""
📚 EMBEDDING_SERVICE.PY
Chuyên trách: Chunking (cắt nhỏ văn bản) & Overlap configuration

Tách bạch trách nhiệm:
- rag_service.py: Xử lý RAG chain & truy vấn
- embedding_service.py: Xử lý chunking & overlap ✅ (NEW)
"""

from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class ChunkingService:
    """
    Service chuyên trách cắt nhỏ văn bản (Chunking) với Overlap tối ưu
    
    Cấu hình dựa trên test results:
    - chunk_size: 1000 ký tự (mức trung bình tối ưu cho tiếng Việt)
    - chunk_overlap: 180 ký tự (18% - giữ ngữ cảnh Điều/Khoản)
    - separators: ["\n\n", "\n", ". ", " ", ""] (ưu tiên: đoạn → dòng → câu → từ)
    """
    
    # Cấu hình mặc định (tối ưu)
    DEFAULT_CONFIG = {
        "CHUNK_SIZE": 1000,
        "CHUNK_OVERLAP_PERCENT": 0.18,  # 18% = 180 ký tự
        "SEPARATORS": ["\n\n", "\n", ". ", " ", ""]
    }
    
    def __init__(self, 
                 chunk_size: int = None,
                 chunk_overlap_percent: float = None,
                 separators: List[str] = None):
        """
        Khởi tạo ChunkingService
        
        Args:
            chunk_size: Độ dài mỗi chunk (ký tự). Mặc định: 1000
            chunk_overlap_percent: Tỷ lệ overlap (0-1). Mặc định: 0.18 (18%)
            separators: Danh sách dấu ngắt ưu tiên. Mặc định: ["\n\n", "\n", ". ", " ", ""]
        """
        self.chunk_size = chunk_size or self.DEFAULT_CONFIG["CHUNK_SIZE"]
        self.chunk_overlap_percent = chunk_overlap_percent or self.DEFAULT_CONFIG["CHUNK_OVERLAP_PERCENT"]
        self.separators = separators or self.DEFAULT_CONFIG["SEPARATORS"]
        
        # Tính chunk_overlap từ chunk_size và phần trăm
        self.chunk_overlap = int(self.chunk_size * self.chunk_overlap_percent)
        
        # Khởi tạo text splitter
        self.splitter = self._create_splitter()
        
        # Thống kê
        self.last_chunk_count = 0
        self.last_total_chars = 0
    
    def _create_splitter(self) -> RecursiveCharacterTextSplitter:
        """Tạo RecursiveCharacterTextSplitter với cấu hình hiện tại"""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Cắt nhỏ danh sách Document objects
        
        Args:
            documents: Danh sách Document từ PDF Loader
            
        Returns:
            Danh sách Document sau khi cắt nhỏ, giữ nguyên metadata
            
        Example:
            >>> from langchain_community.document_loaders import PyPDFLoader
            >>> loader = PyPDFLoader("file.pdf")
            >>> docs = loader.load()
            >>> chunker = ChunkingService()
            >>> chunks = chunker.split_documents(docs)
        """
        splits = self.splitter.split_documents(documents)
        self.last_chunk_count = len(splits)
        self.last_total_chars = sum(len(doc.page_content) for doc in splits)
        return splits
    
    def split_text(self, text: str) -> List[str]:
        """
        Cắt nhỏ text thô (string)
        
        Args:
            text: Nội dung text cần cắt
            
        Returns:
            Danh sách string sau khi cắt
            
        Example:
            >>> chunker = ChunkingService()
            >>> chunks = chunker.split_text("Nội dung văn bản...")
        """
        splits = self.splitter.split_text(text)
        self.last_chunk_count = len(splits)
        self.last_total_chars = sum(len(s) for s in splits)
        return splits
    
    def configure(self,
                  chunk_size: int = None,
                  chunk_overlap_percent: float = None,
                  separators: List[str] = None) -> None:
        """
        Cấu hình lại ChunkingService
        
        Args:
            chunk_size: Độ dài mỗi chunk (ký tự)
            chunk_overlap_percent: Tỷ lệ overlap (0-1)
            separators: Danh sách dấu ngắt ưu tiên
            
        Example:
            >>> chunker = ChunkingService()
            >>> chunker.configure(chunk_size=1200, chunk_overlap_percent=0.15)
        """
        if chunk_size is not None:
            self.chunk_size = chunk_size
        
        if chunk_overlap_percent is not None:
            self.chunk_overlap_percent = chunk_overlap_percent
        
        if separators is not None:
            self.separators = separators
        
        # Tính lại chunk_overlap
        self.chunk_overlap = int(self.chunk_size * self.chunk_overlap_percent)
        
        # Tạo lại splitter
        self.splitter = self._create_splitter()
    
    def get_statistics(self) -> Dict:
        """
        Lấy thống kê về lần cắt cuối cùng
        
        Returns:
            Dict chứa:
            - chunk_count: Số lượng chunks
            - chunk_size: Độ dài mỗi chunk
            - chunk_overlap: Độ dài overlap
            - overlap_percent: Tỷ lệ overlap (%)
            - total_chars: Tổng ký tự
            - avg_chunk_size: Kích thước chunk trung bình
            - separators: Danh sách separators
            
        Example:
            >>> chunker = ChunkingService()
            >>> chunks = chunker.split_text("...")
            >>> stats = chunker.get_statistics()
            >>> print(f"Tổng chunks: {stats['chunk_count']}")
        """
        avg_size = self.last_total_chars // self.last_chunk_count if self.last_chunk_count > 0 else 0
        
        return {
            "chunk_count": self.last_chunk_count,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "overlap_percent": f"{self.chunk_overlap_percent*100:.0f}%",
            "total_chars": self.last_total_chars,
            "avg_chunk_size": avg_size,
            "separators": self.separators,
            "config_status": "✅ Tối ưu cho tiếng Việt"
        }
    
    def print_statistics(self) -> None:
        """In ra thống kê đẹp hơn"""
        stats = self.get_statistics()
        
        print("=" * 80)
        print("📊 THỐNG KÊ CHUNKING")
        print("=" * 80)
        print(f"""
┌─────────────────────────┬─────────────────────────────────────────┐
│ Tổng chunks             │ {stats['chunk_count']:>3} chunks                            │
│ Kích thước chunk        │ {stats['chunk_size']:>4} ký tự (cấu hình)                │
│ Overlap                 │ {stats['chunk_overlap']:>4} ký tự ({stats['overlap_percent']})          │
│ Tổng ký tự              │ {stats['total_chars']:>6} ký tự                          │
│ Trung bình/chunk        │ {stats['avg_chunk_size']:>4} ký tự                            │
│ Separators              │ {str(stats['separators'])[:40]}       │
│ Trạng thái              │ {stats['config_status']}                      │
└─────────────────────────┴─────────────────────────────────────────┘
        """)
    
    def get_config_info(self) -> str:
        """Lấy thông tin cấu hình hiện tại dưới dạng string"""
        return f"""
Cấu hình ChunkingService:
- chunk_size: {self.chunk_size} ký tự
- chunk_overlap: {self.chunk_overlap} ký tự ({self.chunk_overlap_percent*100:.0f}%)
- separators: {self.separators}

Mục đích:
- Cắt nhỏ văn bản thành các đoạn có độ dài hợp lý
- Giữ ngữ cảnh Điều/Khoản không bị cắt quãng (overlap)
- Tối ưu cho tiếng Việt (separators ưu tiên)
        """


# ===== PRESET CONFIGURATIONS =====
class ChunkingPresets:
    """Các cấu hình được define sẵn cho các trường hợp khác nhau"""
    
    @staticmethod
    def vietnamese_optimized() -> ChunkingService:
        """Cấu hình tối ưu cho tiếng Việt (Khuyến nghị)"""
        return ChunkingService(
            chunk_size=1000,
            chunk_overlap_percent=0.18,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    @staticmethod
    def fast_retrieval() -> ChunkingService:
        """Cấu hình cho truy xuất nhanh (chunks ngắn)"""
        return ChunkingService(
            chunk_size=500,
            chunk_overlap_percent=0.15,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    @staticmethod
    def context_rich() -> ChunkingService:
        """Cấu hình giữ context tốt nhất (chunks dài)"""
        return ChunkingService(
            chunk_size=1500,
            chunk_overlap_percent=0.20,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    @staticmethod
    def balanced() -> ChunkingService:
        """Cấu hình cân bằng giữa tốc độ và context"""
        return ChunkingService(
            chunk_size=1000,
            chunk_overlap_percent=0.15,
            separators=["\n\n", "\n", ". ", " ", ""]
        )


if __name__ == "__main__":
    # Test ChunkingService
    print("=" * 80)
    print("🧪 TEST CHUNKING SERVICE")
    print("=" * 80)
    
    test_text = """ĐIỀU 1: GIỚI THIỆU

Khoản 1.1: Định nghĩa hệ thống
Hệ thống quản lý tài liệu là tập hợp các công cụ. Nó rất quan trọng.

Khoản 1.2: Mục đích
Mục đích là quản lý tài liệu hiệu quả. Đây là điều cơ bản.

ĐIỀU 2: YÊU CẦU KỸ THUẬT

Khoản 2.1: Cấu trúc dữ liệu
Dữ liệu phải được tổ chức. Cấu trúc là chìa khóa. Mỗi file có metadata.

Khoản 2.2: Bảo mật
Bảo mật dữ liệu là ưu tiên hàng đầu. Mã hóa là bắt buộc."""
    
    # Test 1: Cấu hình tối ưu (mặc định)
    print("\n1️⃣  TEST: Cấu hình tối ưu (Mặc định)")
    print("-" * 80)
    chunker = ChunkingService()
    chunks = chunker.split_text(test_text)
    print(f"✅ Cắt thành {len(chunks)} chunks")
    chunker.print_statistics()
    
    # Test 2: Sử dụng preset
    print("\n2️⃣  TEST: Sử dụng Preset - Fast Retrieval")
    print("-" * 80)
    chunker_fast = ChunkingPresets.fast_retrieval()
    chunks_fast = chunker_fast.split_text(test_text)
    print(f"✅ Cắt thành {len(chunks_fast)} chunks")
    chunker_fast.print_statistics()
    
    # Test 3: Cấu hình lại
    print("\n3️⃣  TEST: Cấu hình lại ChunkingService")
    print("-" * 80)
    chunker.configure(chunk_size=500, chunk_overlap_percent=0.15)
    chunks_reconfigure = chunker.split_text(test_text)
    print(f"✅ Cắt thành {len(chunks_reconfigure)} chunks (sau cấu hình lại)")
    chunker.print_statistics()
    
    print("\n" + "=" * 80)
    print("✅ TEST HOÀN TẤT!")
    print("=" * 80)
