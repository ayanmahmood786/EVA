from core.utils import *
from core.log import logger
from core.function import executor,format_answer,insert_into_tables
import time
from models.overall import handler,async_tb_table,qt_generation,final_insight


# Request Model
class BIINSIGHT(BaseModel):
    data: str
    question:str
    output:str





class BIINSIGHTHISTORY(BaseModel):
    report_name:str
    chat_id:str
    user_id:str
    data: str
    question:str



router=APIRouter()

def sync_read_df(query: str) -> pd.DataFrame:
    try:
        df = pd.read_sql(query, con=connection)
        if df.empty:
            raise HTTPException(status_code=500, detail="DataFrame is empty")
        return df
    except Exception as e:
        logger.error(f"DB read failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_bi_insight")
async def get_bi_insight(req: BIINSIGHT):
    try:

        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(executor, sync_read_df, req.data)

        questions_json = await qt_generation(req.question, req.output, df.head(5))

        data_bundle = await handler(questions_json["result"], df)

        insight_result = await final_insight(req.question, data_bundle["result"])
        content_html = insight_result["result"].replace("```html", "").replace("```", "")

        return {
            "insight": format_answer(content_html),
            "questions": questions_json,
            "data_bundle": data_bundle
        }

    except Exception as e:
        logger.error(f"BI Insight pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/get_bi_insight_history")
async def get_bi_insight_history(req: BIINSIGHTHISTORY):
    try:
        output=None
        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(executor, sync_read_df, req.data)

        questions_json = await qt_generation(req.question, output , df.head(5))

        data_bundle = await handler(questions_json["result"], df)

        insight_result = await final_insight(req.question, data_bundle["result"])
        content_html = insight_result["result"].replace("```html", "").replace("```", "")

        total_input_tokens = (
            questions_json["input_tokens"]
            + data_bundle["input_tokens"]
            + insight_result["input_tokens"]
        )
        
        total_output_tokens = (
            questions_json["output_tokens"]
            + data_bundle["output_tokens"]
            + insight_result["output_tokens"]
        )
        
        total_tokens = (
            questions_json["total_tokens"]
            + data_bundle["total_tokens"]
            + insight_result["total_tokens"]
        )



        return {
            "insight": format_answer(content_html),
            "questions": questions_json,
            "data_bundle": data_bundle
        }

    except Exception as e:
        logger.error(f"BI Insight pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await insert_into_tables(mst_track_tokens_data={
    "VC_CHAT_ID": req.chat_id,
    "DT_DATETIME": datetime.utcnow(),  
    "VC_USER_REQUEST": "Overall",
    "VC_PROCESS_NAME": "Overall process",

    "NU_INPUT_TOKENS": total_input_tokens,
    "NU_OUTPUT_TOKENS": total_output_tokens,
    "NU_TOTAL_TOKENS": total_tokens,

    "NU_INPUT_TOKEN_COST": 0,
    "NU_OUTPUT_TOKEN_CODE": 0,
    "NU_TOTAL_COST": 0,
    "VC_USER_NAME": req.user_id
},
        mst_report_history_data={
        
        "VC_USER_NAME":req.user_id,
        "VC_CHAT_ID": req.chat_id,
        "VC_USER_REQUEST": "Overall",
        "CL_PD_QUERY": "",
        "VC_CHAT_NAME": f"{req.report_name}_{req.chat_id}",
        "CL_SQL_QUERY": req.data,
        "CL_RESPONSE": format_answer(content_html),
        "VC_REPORT_ID": req.report_name,
        "BL_GRAPH": b"\x89PNG..."  # example binary image bytes}

        })