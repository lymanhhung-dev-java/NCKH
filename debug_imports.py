import sys
import os

print(f"Python executable: {sys.executable}")
try:
    import langchain
    print(f"Langchain version: {langchain.__version__}")
    print(f"Langchain file: {langchain.__file__}")
except ImportError:
    print("Langchain not found")

try:
    from langchain.chains import create_retrieval_chain
    print("from langchain.chains import create_retrieval_chain SUCCESS")
except ImportError as e:
    print(f"from langchain.chains import create_retrieval_chain FAILED: {e}")

try:
    from langchain.chains import retrieval
    print("from langchain.chains import retrieval SUCCESS")
except ImportError as e:
    print(f"from langchain.chains import retrieval FAILED: {e}")
