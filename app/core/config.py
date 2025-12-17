import os
from dotenv import load_dotenv




load_dotenv(dotenv_path=".env")

# ✅ Now access environment variables
APP_NAME = os.getenv("APP_NAME", "EVA-AI")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EBIZ_USER=os.getenv("EBIZ_USER")
EBIZ_PASSWORD=os.getenv('EBIZ_PASS')
VECTOR_DIR="dir/faiss_vectors"
LOG_PATH = "logs/app.log"

VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "RAG/vector_store")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "RAG/uploaded_files")