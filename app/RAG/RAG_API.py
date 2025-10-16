from fastapi import FastAPI, HTTPException,Request,Form,File,UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from datetime import datetime
import os.path
from rag_history import history
from rag_vector_llm import pdf_loader, spiltter, vector_stored, model
import rag_vector_llm
from fetch_answer_database import find_similarity,fetch_answer_for_question
from langchain_chroma import Chroma
import shutil
from fetch_answer_database import fetch_frequent
import re
# Logging setup
logging.basicConfig(filename="logs/new.log", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()


"""<--------------------------------------------------- VARIABLES --------------------------------------------->"""

sessions={"76"}

# vt_store = None
custom_pdf=None
UPLOAD_DIR="uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
if os.path.exists('chroma'):
    vt_store=Chroma(persist_directory=rag_vector_llm.PATH, embedding_function=rag_vector_llm.embeddings)
else:
    vt_store=None

greetings = ["hi", "hello", "hey", "hlo", "hola","how are you","hi how are you"]



"""<----------------------------------------------------- CORS ------------------------------------------------->"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

"""<-------------------------------------------------------- CLASSES ----------------------------------------->"""



class QuestionRequest(BaseModel):
    question: str
    session_id:str
    custom:int
    user_id:str

class SessionID(BaseModel):
    session_id:str
    module:str


"""<-------------------------------------------------------- FUNCTIONS --------------------------------------->"""

def date_time():
        date=datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        date = datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
        return date

def format_answer(answer):
    answer=answer.replace("**","\\b")
    answer = re.sub(r'\\b(.*?)\\b', r'<strong>\1</strong>', answer)
    return answer

def check_sqlite_db_exists(db_path):
    if os.path.isfile(db_path):
        print(f"Database exists at {db_path}")
        return True
    else:
        print(f"Database does not exist at {db_path}")
        return False

def custom_ans(user_id,question):
    start=time.time()
    if check_sqlite_db_exists(f"custom_chroma/{user_id}/chroma.sqlite3"):
        vt_store_custom=Chroma(persist_directory=f"custom_chroma/{user_id}",embedding_function=rag_vector_llm.embeddings,collection_name="My_collection")
    else: 
        return JSONResponse(content={"Error":"Please Upload Your custom_pdf"})
    answer=model(vt_store_custom,question)
    answer=format_answer(answer.content)
    return JSONResponse(content={"Answer": answer, "Time": f"{round(time.time()-start, 2)}"})

"""<-------------------------------------------------------- API ROUTES --------------------------------------->"""

@app.post("/create_vectors")
async def create_vectors(request:Request,module:str=Form(...)):
    """
    Endpoint to create vector store from a PDF.
    """
    logger.info(f"Request URL: {request.url} | Method: {request.method}\n")
    global vt_store
    try:
        start=time.time()
        # Load and process the PDF
        pdf = pdf_loader(rag_vector_llm.file_path)
        split = spiltter(pdf)
        path=f"vector_store/{module}/chroma"
        vt_store = vector_stored(split, rag_vector_llm.embeddings, path)
        return JSONResponse(content={"message": f"Vector Store Created Successfully for {module}","Time":f"{start-time.time()}secs"})
    except Exception as e:
        logger.error(f"Error in create_vectors: {e}")
        raise HTTPException(status_code=500, detail="Failed to create vector store")

@app.post("/rag_responses")
async def rag_response(question: QuestionRequest,request:Request):
    """
    Endpoint to get responses using RAG (Retrieval-Augmented Generation).
    """
    logger.info(f"Request URL: {request.url} | Method: {request.method}\n")
    global sessions
    logger.info(f"\n \nQuestion Received: {question.question}")
    start = time.time()
    if question.custom == 1:
        logger.info("Entering Custom File Module .......")
        return custom_ans(question.user_id,question.question)
    elif question.custom == 0:
        try:
            vt_store=Chroma(persist_directory=f"vector_store/{question.user_id}/chroma",embedding_function=rag_vector_llm.embeddings,collection_name="My_collection")
            logger.info(f"Database intialize for Module: {question.user_id}")
        except Exception as e:
            logger.error(f"Error While Database intialization for module:{question.user_id} ,\nError:{e}")
            return JSONResponse(content={"Error": "Vector store is not initialized. Call /create_vectors first."})

    if question.question.lower().strip() in greetings:
        greeting_response = "Hello! I'm EVA AI, developed by EVA AI Team to assist you. How can I help you today?"
        return JSONResponse(content={"Answer": greeting_response, "Time": f"{round(time.time()-start, 2)}"})
    if len(question.question)<=8:
        return JSONResponse(content={"Answer":"Please Enter A Valid Question Or provide more detail","Time":"0.00"})
    # if question.question:
    #     matched = find_similarity(question.question)  # Get similar questions
    #     logger.info(f"Matches Found In Database:{matched}")
    #     if matched != []:
    #         # Get the best match from the list
    #         best_match = matched[0][0]  # Extract the question from the tuple
    #         answer = fetch_answer_for_question(best_match) 
    #         logger.info(f"Answer Fetch:{answer[0]}")
    #         return JSONResponse(content={"Answer": answer[0], "Time": f"{round(time.time()-start, 2)}","Note":"This Response Is Generated Based On Your Previous History"})

    try:
        logger.info("Entering LLM Chain")
        answer = model(vt_store, question.question)  # Assuming this function works with the question
        logger.info("Answer Generated Sucessfully")
        answer = format_answer(answer.content)
        history((question.user_id).upper(),question.question, "1", answer, 1223, 122, "01", date_time())
        logger.info(f"Time Taken: {round(time.time()-start, 2)}")
        sessions.add(question.session_id)
        return JSONResponse(content={"Answer": answer, "Time": f"{round(time.time()-start, 2)}","Note": "LLM Generated Response"})

    except Exception as e:
        logger.error(f"Error in rag_response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@app.post("/most_frequent")
async def frequent_questions(user:SessionID):
    data=fetch_frequent(user.session_id,user.module)
    if data !=None:
        new_data={
            "1":{"session":data[0][0],"question":data[0][1].capitalize(),"answer":data[0][2],"frequency":data[0][3]},
            "2":{"session":data[1][0],"question":data[1][1].capitalize(),"answer":data[1][2],"frequency":data[1][3]},
            "3":{"session":data[2][0],"question":data[2][1].capitalize(),"answer":data[2][2],"frequency":data[2][3]},
        } 
        return new_data
    return data

@app.post("/custom_pdf")
async def upload_pdf(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    API for custom PDF processing with detailed logging and exception handling.
    """
    global custom_pdf
    logging.info(f"Received request to process custom PDF for user_id: {user_id}")
    
    # Check file type
    if file.content_type != "application/pdf":
        logging.error(f"Invalid file type: {file.content_type}. Only PDFs are allowed.")
        return JSONResponse(content={"message": "Only PDF Files are allowed."}, status_code=400)
    logging.info("File type validated as PDF.")

    # Save uploaded file
    upload_dir = f"./uploaded_files/{user_id}/"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, file.filename)
    logging.info(f"Upload directory created: {upload_dir}")

    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logging.info(f"File saved successfully at: {file_location}")
    except Exception as e:
        logging.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    try:
        logging.info(f"Starting PDF processing for file: {file_location}")
        custom_file_path = file_location
        custom_path = f"custom_chroma/{user_id}/"
        pdf = pdf_loader(custom_file_path)  # Custom function to load the PDF
        logging.info("PDF loaded successfully.")
        split = spiltter(pdf)  # Custom function to split PDF into chunks
        logging.info("PDF split into chunks successfully.")
        try:
            custom_pdf = vector_stored(split, rag_vector_llm.embeddings, custom_path)  # Custom function to store vectors
        except Exception as e:
            logger.info("Enter exception chain")
            custom_pdf = vector_stored(split, rag_vector_llm.embeddings, custom_path )  # Custom function to store vectors
            logging.info("Vector store created successfully.")
    except Exception as e:
        logging.error(f"Error during PDF processing: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")

    return JSONResponse(content={"message": "Custom Vector Created Successfully"}, status_code=201)