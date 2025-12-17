from core.utils import *
from core.log import logger
from core.function import clean_response

from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log, after_log
from fuzzywuzzy import process
from models.auto_prompt import suggestions


"""<-------------------------------------------- Global Variables ----------------------------------------------->"""


greetings = ["hi", "hello", "hey", "hlo", "hola","how are you","hi how are you",'',""," "]
context_dict={}






"""<-------------------------------------------- Classes ------------------------------------------------------------>"""

class QuestionRequest(BaseModel):
    question: str
    session: str

router=APIRouter()



@router.post("/generate-suggestions/")
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), before_sleep=before_sleep_log(logger, logging.INFO), after=after_log(logger, logging.INFO))
async def generate_suggestion(question_request: QuestionRequest):
    global context_list
    
    logger.info(f"Session ID:,{question_request.session}")
    logger.info(f"Question:,{question_request.question}")
    session=question_request.session

    for i in greetings:
        if len(question_request.question)<15:
            if any(greet in question_request.question.lower() for greet in greetings):
                greeting_response = "Hello! I'm EVA Your AI Copilot , developed by ESS AI Team to assist you. How can I help you today?"
                return JSONResponse(content={"result":{"Answer_to_user_question": greeting_response, "Auto_prompt": {
                }}
            })

    try:
        if question_request.session in context_dict:
            logger.info("Old Session Continued")
            result = await suggestions(question_request.question, previous_question=str(context_dict[session]))
            logger.info("Response Generated From LLM Successfully")
            context_dict[session].append(question_request.question)  
            qa_data = json.loads(clean_response(result))
        else:

            context_dict[session] = [question_request.question]
            logger.info("New Session Detected And Added")
            result = await suggestions(question_request.question, previous_question=str(context_dict[session]))
            logger.info("Response Generated From LLM Successfully")
            qa_data = json.loads(clean_response(result))

        return {
        "result": qa_data,
    }
    except Exception as e:
        logger.error(f"Error Encounted In API:{e}")
        raise HTTPException(status_code=500, detail=str(e))
