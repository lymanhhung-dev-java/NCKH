import os
import sys

# Ensure current directory is in sys.path
sys.path.append(os.getcwd())

from app.service.rag_service import rag_service
from app.core.config import settings

def main():
    print("=== STARTING SYSTEM VERIFICATION ===\n")

    # 1. Verify ChromaDB Persistence
    print("--- 1. Checking ChromaDB Persistence ---")
    db_dir = settings.DATABASE_DIR
    print(f"Database Directory: {db_dir}")
    if os.path.exists(db_dir) and os.listdir(db_dir):
        print(f"✅ Persistence Directory exists and is not empty. Contents: {os.listdir(db_dir)[:5]}...")
    else:
        print("❌ Persistence Directory NOT found or empty!")
    
    # 2. Verify Vector Store Content
    print("\n--- 2. Checking Vector Store Content ---")
    try:
        # chroma_db.get() returns a dict with 'ids', 'metadatas', 'documents', etc.
        data = rag_service.vector_store.get(limit=5)
        ids = data.get('ids', [])
        print(f"Total documents found in query (limit 5): {len(ids)}")
        
        if len(ids) == 0:
            print("⚠️ No documents in Vector Store. Have you run ingestion?")
        else:
            print(f"✅ Found {len(ids)} sample documents.")
            
            # 3. Verify Metadata
            print("\n--- 3. Verifying Metadata ---")
            metadatas = data.get('metadatas', [])
            for i, meta in enumerate(metadatas):
                print(f"\n[Doc {i+1} Metadata]: {meta}")
                
                # Check Source
                if "source" in meta:
                    print(f"  ✅ Source: {meta['source']}")
                else:
                    print(f"  ❌ Missing 'source' field!")
                
                # Check Page (PyPDFLoader usually adds this)
                if "page" in meta:
                    print(f"  ✅ Page: {meta['page']}")
                else:
                    print(f"  ⚠️ Missing 'page' field (Might vary by loader)")

    except Exception as e:
        print(f"❌ Error accessing Vector Store: {e}")

    # 4. Verify RAG Chain Retrieval (Simulation)
    print("\n--- 4. Testing RAG Retrieval ---")
    test_query = "hệ thống quản lý"
    print(f"Querying for: '{test_query}'")
    try:
        retriever = rag_service.vector_store.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(test_query)
        
        if docs:
            print(f"✅ Retrieved {len(docs)} documents.")
            for i, doc in enumerate(docs):
                print(f"  Result {i+1} Source: {doc.metadata.get('source', 'Unknown')}")
        else:
            print("⚠️ No documents retrieved.")
            
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")

    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    main()
