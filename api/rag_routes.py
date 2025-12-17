from core.utils import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from RAG.rag_vector_llm import pdf_loader, spiltter, vector_stored, model
from langchain_chroma import Chroma
import os, re, time, logging, asyncio
from datetime import datetime
import RAG
from RAG.fetch_answer_database import fetch_frequent

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = "RAG/uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
greetings = ["hi", "hello", "hey", "hola"]

class RAGRequest(BaseModel):
    question: str
    session_id: str
    custom: int
    user_id: str

class RAGSessionID(BaseModel):
    session_id:str
    module:str



def date_time():
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    return datetime.strptime(now, "%d-%m-%Y %H:%M:%S")

def format_answer(answer: str):
    answer = answer.replace("**", "\\b")
    return re.sub(r'\\b(.*?)\\b', r'<strong>\1</strong>', answer)

@router.post("/rag_responses")
async def rag_response(question: RAGRequest, request: Request, background_task: BackgroundTasks):
    start = time.time()
    logger.info(f"Question: {question.question}")

    try:
        vt_store = Chroma(
            persist_directory=f"RAG/vector_store/{question.user_id}/chroma",
            embedding_function=embeddings,
            collection_name="My_collection"
        )

        if question.question.lower().strip() in greetings:
            return JSONResponse(content={"Answer": "Hello! How can I help you today?"})

        answer = await model(vt_store, question.question)
        formatted = format_answer(answer.content)
        duration = round(time.time() - start, 2)
        return JSONResponse(content={"Answer": formatted, "Time": f"{duration}s"})
    except Exception as e:
        logger.error(f"Error in rag_response: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    # finally:
        

@router.post("/create_vectors")
async def create_vectors(request:Request,module:str=Form(...)):
    """
    Endpoint to create vector store from a PDF.
    """
    logger.info(f"Request URL: {request.url} | Method: {request.method}\n")
    vt_store=""
    try:
        start=time.time()
        # Load and process the PDF
        pdf = pdf_loader(RAG.rag_vector_llm.file_path)
        split = spiltter(pdf)
        path=f"RAG/vector_store/{module}/chroma"
        vt_store = vector_stored(split, embeddings, path)
        return JSONResponse(content={"message": f"Vector Store Created Successfully for {module}","Time":f"{start-time.time()}secs"})
    except Exception as e:
        logger.error(f"Error in create_vectors: {e}")
        raise HTTPException(status_code=500, detail="Failed to create vector store")


@router.post("/most_frequent")
async def frequent_questions(user:RAGSessionID):
    data=fetch_frequent(user.session_id,user.module)
    if data !=None:
        new_data={
            "1":{"session":data[0][0],"question":data[0][1].capitalize(),"answer":data[0][2],"frequency":data[0][3]},
            "2":{"session":data[1][0],"question":data[1][1].capitalize(),"answer":data[1][2],"frequency":data[1][3]},
            "3":{"session":data[2][0],"question":data[2][1].capitalize(),"answer":data[2][2],"frequency":data[2][3]},
        } 
        return new_data
    return data