from core.utils import *
import RAG
from models.pdf import process_pdf_background
from core.log import logger
from core.function import append_to_excel
from typing import List
import uuid
from langchain.chains.question_answering import load_qa_chain
# Developed by 21/8
# - Ayan Mahmood
import random
llm_pdf=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.5)



router= APIRouter()

TEMP_DIR = "dir/uploaded_pdfs"
os.makedirs(TEMP_DIR, exist_ok=True)

# Vector store directory
VECTOR_DIR = "dir/faiss_vectors"
os.makedirs(VECTOR_DIR, exist_ok=True)

class FileRequest(BaseModel):
    user_id: str
    question: str

def load_vector_store(user_id: str):
    """Load the FAISS vector store for a specific user."""
    vector_store_path = os.path.join(VECTOR_DIR, f"faiss_index_{user_id}")
    if not os.path.exists(vector_store_path):
        raise HTTPException(status_code=404, detail="No processed PDF found for this user")
    return FAISS.load_local(vector_store_path, RAG.rag_vector_llm.embeddings, allow_dangerous_deserialization=True)



@router.post("/upload/")
async def upload_pdfs(files: List[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
    """Upload and process multiple PDFs asynchronously."""
    user_id = str(uuid.uuid4())  # Unique session ID

    uploaded_files = []
    for file in files:
        logger.info(f"Received file: {file.filename}")

        # Save PDF to a temporary file
        temp_pdf_path = os.path.join(TEMP_DIR, f"{user_id}_{file.filename}")
        with open(temp_pdf_path, "wb") as temp_pdf:
            shutil.copyfileobj(file.file, temp_pdf)

        
        background_tasks.add_task(process_pdf_background, temp_pdf_path, user_id)

        uploaded_files.append(file.filename)

    return {
        "message": "Processing started!",
        "user_id": user_id,
        "files": uploaded_files
    }



@router.post("/query/")
async def ask_question(user_request: FileRequest):
    """Answer a question based on the user's uploaded PDFs."""
    try:
        logger.info(f"User Query: {user_request.question} | User ID: {user_request.user_id}")

        if len(user_request.question) < 10:
            return {"reply": "Please improvise your question"}

        vector_store = load_vector_store(user_request.user_id)

        # Perform similarity search
        docs = vector_store.similarity_search(user_request.question)

        # If no relevant documents found
        if not docs:
            return {"reply": "The answer is not available in the context."}

        # Construct prompt
        prompt_template = """
        Answer the question as detailed as possible from the provided context.
        If the answer is not in the provided context, or the user question is irrelevant or a greeting, just say:
        "The answer is not available in the context."

        Context: {context}
        Question: {question}

        Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(llm_pdf, chain_type="stuff", prompt=prompt)

        response = chain.invoke({"input_documents": docs, "question": user_request.question}, return_only_outputs=True)
        
        return {"reply": response["output_text"]}
    except Exception as e:
        logger.error("NLP PDF:",e)
    finally:
        prompt=    random.randint(700, 2000)
        output=     random.randint(700, 2000)
#        await append_to_excel("NLP PDF","",    
#    (prompt + output),
#    prompt,
#    output,
#0)
