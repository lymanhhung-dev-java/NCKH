from app.service.rag_service import rag_service
import sys

# Force output to utf-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

print("--- KIỂM TRA DỮ LIỆU TỒN TẠI SAU KHI KHỞI ĐỘNG LẠI ---")

try:
    # Truy vấn trực tiếp Vector Store để kiểm tra dữ liệu (không cần LLM)
    query = "Nội dung chính"
    print(f"❓ Truy vấn Vector Store: {query}")
    
    results = rag_service.vector_store.similarity_search(query, k=1)
    
    if results:
        print(f"✅ THÀNH CÔNG: Tìm thấy {len(results)} kết quả từ ChromaDB.")
        for doc in results:
            print(f"   📄 Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"   📝 Content snippet: {doc.page_content[:100]}...")
    else:
        print("⚠️ CẢNH BÁO: Không tìm thấy dữ liệu trong ChromaDB.")

except Exception as e:
    print(f"❌ LỖI: {e}")
