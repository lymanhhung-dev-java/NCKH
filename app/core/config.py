import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_DIR = "./database/chroma_db"

settings = Settings()