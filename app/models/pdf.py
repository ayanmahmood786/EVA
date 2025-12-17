import os
import api
from PyPDF2 import PdfReader
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import RAG.rag_vector_llm
from core.log import logger
from core.config import VECTOR_DIR
from core.utils import embeddings
# Temporary directory for storing PDFs





# ✅ Function to extract text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:

    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def split_text_into_chunks(text: str) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=80000, chunk_overlap=1000)
    return text_splitter.split_text(text)


def create_vector_store(text_chunks: List[str], user_id: str):

    user_vector_store_path = os.path.join(VECTOR_DIR, f"faiss_index_{user_id}")

    new_vectors = FAISS.from_texts(text_chunks, embedding=RAG.rag_vector_llm.embeddings)


    if os.path.exists(user_vector_store_path):
        existing_vectors = FAISS.load_local(user_vector_store_path, embeddings, allow_dangerous_deserialization=True)
        existing_vectors.merge_from(new_vectors)
        existing_vectors.save_local(user_vector_store_path)
    else:
        new_vectors.save_local(user_vector_store_path)



def process_pdf_background(pdf_path: str, user_id: str):

    try:
        logger.info(f"Processing PDF: {pdf_path}")
        text = extract_text_from_pdf(pdf_path)
        text_chunks = split_text_into_chunks(text)
        create_vector_store(text_chunks, user_id)  # Merges embeddings
    finally:
        os.remove(pdf_path)  # Cleanup temporary PDF file
