import langchain
import os
print(f"Version: {langchain.__version__}")
print(f"Path: {langchain.__file__}")
try:
    from langchain.chains import create_retrieval_chain
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
