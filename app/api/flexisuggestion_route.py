from core.utils import *
from core.log import logger
from typing import Dict, Any
from models.insight_suggest import insightsuggestions
<<<<<<< HEAD

=======
from core.function import update_history_flexi
>>>>>>> ayan2


class ResponseModel(BaseModel):
    result: Dict[str, Any]


class QuestionRequestFlexi(BaseModel):
    question: str
    session: str
    data :str
    instructions: Optional[str] = ""


<<<<<<< HEAD
=======


class QuestionRequestFlexiHistory(BaseModel):
    report_name:str
    chat_id:str
    user_id:str
    question: str
    session: str
    data :str
    instructions: Optional[str] = ""


>>>>>>> ayan2
router=APIRouter()

flexi_dict={}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def generate_suggestions_endpoint(request: QuestionRequestFlexi):
    global flexi_dict
    
    try:

        previous_question = ""
        if request.session in flexi_dict and flexi_dict[request.session]:
            last_entry = flexi_dict[request.session][-1]
            previous_question = last_entry.get("question", "") if isinstance(last_entry, dict) else last_entry
        
<<<<<<< HEAD
        # Generate with LangGraph
        start=time.time()
        result = insightsuggestions(
=======
        start=time.time()
        result = await insightsuggestions(
>>>>>>> ayan2
            question=request.question,
            previous_question=previous_question,
            data=request.data,
            Instructions=request.instructions
        )

        print("Flexi-time:",time.time()-start)
        
        context_entry = {"question": request.question, "data": request.data}
        if request.session in flexi_dict:
            flexi_dict[request.session].append(context_entry)
            flexi_dict[request.session] = flexi_dict[request.session][-3:]
        else:
            flexi_dict[request.session] = [context_entry]        
        return ResponseModel(result=result)
        
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



<<<<<<< HEAD
=======
async def generate_suggestions_endpoint_history(request: QuestionRequestFlexiHistory):
    global flexi_dict
    
    try:

        previous_question = ""
        if request.session in flexi_dict and flexi_dict[request.session]:
            last_entry = flexi_dict[request.session][-1]
            previous_question = last_entry.get("question", "") if isinstance(last_entry, dict) else last_entry
        
        # Generate with LangGraph
        start=time.time()
        result = await insightsuggestions(
            question=request.question,
            previous_question=previous_question,
            data=request.data,
            Instructions=request.instructions
        )

        print("Flexi-time:",time.time()-start)
        
        context_entry = {"question": request.question, "data": request.data}
        if request.session in flexi_dict:
            flexi_dict[request.session].append(context_entry)
            flexi_dict[request.session] = flexi_dict[request.session][-3:]
        else:
            flexi_dict[request.session] = [context_entry]        
        return ResponseModel(result=result)
        
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        await update_history_flexi(data={
        "VC_USER_NAME":request.user_id,
        "VC_CHAT_ID": request.chat_id,
        "VC_USER_REQUEST": request.question,
        "VC_CHAT_NAME": f"{request.report_name}_{request.chat_id}",
        "CL_RESPONSE": json.dumps(result),
        "VC_REPORT_NAME": request.report_name,
        },
        token={
        "VC_USER_NAME": request.user_id,
        "VC_CHAT_ID": request.chat_id,
        "VC_PROCESS_NAME": "FLEXI",
        "VC_USER_REQUEST": request.question,
        "NU_INPUT_TOKENS": result["Token_Usage"]["input_tokens"],
        "NU_OUTPUT_TOKENS": result["Token_Usage"]["output_tokens"],
        "NU_TOTAL_TOKENS": result["Token_Usage"]["total_tokens"]
    }
        
        
        )


>>>>>>> ayan2
@router.post("/flexi-suggestions/", response_model=ResponseModel)
async def generate_suggestions(request: QuestionRequestFlexi):
    return await generate_suggestions_endpoint(request)

<<<<<<< HEAD
=======
@router.post("/flexi-suggestions-history/", response_model=ResponseModel)
async def generate_suggestions(request: QuestionRequestFlexiHistory):
    return await generate_suggestions_endpoint_history(request)



>>>>>>> ayan2
