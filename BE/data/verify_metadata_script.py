import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.service.rag_service import rag_service
from langchain_chroma import Chroma

def verify_metadata():
    print("--- Verifying Metadata in ChromaDB ---")
    
    # Access the vector store directly
    vector_store = rag_service.vector_store
    
    # Get a few documents
    results = vector_store.get(limit=5)
    
    if not results['ids']:
        print("No documents found in ChromaDB.")
        return

    print(f"Found {len(results['ids'])} documents.")
    
    for i, meta in enumerate(results['metadatas']):
        print(f"\nDocument {i+1} Metadata:")
        print(meta)
        
        # Check for expected keys
        if 'source' in meta:
            print("  [OK] 'source' found.")
        else:
            print("  [FAIL] 'source' MISSING.")
            
        if 'page' in meta:
            print("  [OK] 'page' found.")
        else:
            print("  [FAIL] 'page' MISSING.")

if __name__ == "__main__":
    verify_metadata()
