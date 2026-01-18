import sys
import os

# Ensure the app module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.service.rag_service import rag_service

def main():
    data_dir = os.path.join(os.getcwd(), "data")
    print(f"Starting ingestion from {data_dir}...")
    rag_service.ingest_documents(data_dir)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
