from core.utils import *
from core.log import logger
from core.function import executor,format_answer
import time
from models.overall import handler,async_tb_table,qt_generation,final_insight


# Request Model
class BIINSIGHT(BaseModel):
    data: str
    question:str
    output:str


router=APIRouter()

def sync_bi_ds_ins(req: BIINSIGHT):
    """This is your original blocking code, moved into sync function."""
    global df
    try:
        df = pd.read_sql(req.data, con=connection)
        logger.info(req.data)
        if df.empty:
            raise HTTPException(status_code=500, detail="DataFrame is Empty")

        print(req.question)

        # Step 1: Generate Questions
        start_time = time.time()
        # qt_generation is async, so we need to run it in an event loop here
        questions_str = asyncio.run(qt_generation(req.question, req.output, df.head(5)))
        questions_str = questions_str.replace("```json", "").replace("```", "")
        print(questions_str)
        print(start_time - time.time())

        # Step 2: Generate Tables for Questions
        start_time = time.time()
        data_bundle = asyncio.run(handler(questions_str,df))
        logger.info(data_bundle)
        print(start_time - time.time())

        # Step 3: Final Insight
        start_time = time.time()
        insight = asyncio.run(final_insight(req.question, data_bundle))
        print(start_time - time.time())

        return {
            "insight": format_answer(insight.replace("```html", "").replace("```", ""))
        }

    except Exception as e:
        print(e)
        raise


@router.post("/get_bi_insight")
async def bi_ds_ins(req: BIINSIGHT):
    """Async wrapper that offloads heavy work into thread pool"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, sync_bi_ds_ins, req)

