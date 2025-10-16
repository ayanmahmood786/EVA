from core.utils import *
from core.log import logger
from typing import Dict, Any
from models.insight_suggest import insightsuggestions



class ResponseModel(BaseModel):
    result: Dict[str, Any]


class QuestionRequestFlexi(BaseModel):
    question: str
    session: str
    data :str
    instructions: Optional[str] = ""


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
        
        # Generate with LangGraph
        start=time.time()
        result = insightsuggestions(
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



@router.post("/flexi-suggestions/", response_model=ResponseModel)
async def generate_suggestions(request: QuestionRequestFlexi):
    return await generate_suggestions_endpoint(request)

