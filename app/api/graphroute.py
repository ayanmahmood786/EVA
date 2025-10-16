from core.utils import * 
from core.log import logger
from models.default_graph import save_default_blank
from models.graph import graph

import uuid



router=APIRouter()


class ReqNLP(BaseModel):
    df: str
    question:str
    sql_query:str
    session_id:str



@router.post("/graph")
@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
async def graph_generator(req:ReqNLP):
    try:
        session_id=req.session_id
        df_json = req.df
        if os.path.exists(f"output{session_id}.jpg"):
            os.remove(f"output{session_id}.jpg")
        df_dict = json.loads(df_json)
        df = pd.DataFrame(df_dict)
        start = time.time()
        code = await graph(df,llm)
        logger.info("Graph code:")
        logger.info(code)
        print(f"Time Taken While Executing GRAPH: {time.time() - start}") 
        generated_code = code.replace("```python", "").replace("```", "").replace("output.jpg",f"output{session_id}.jpg")
        local_vars = {"df": df, "output_df": None}
        exec(generated_code, local_vars)
        file_path = f"output{session_id}.jpg"  
        return FileResponse(path=file_path, media_type="image/jpg", filename="output.jpg")


    except Exception as e:
        import traceback
        save_default_blank(session_id)
        print(f"issue: {str(e)},trace: {traceback.format_exc()}")
        return JSONResponse(content={
        "Dataframe": [],
        "issue": str(e),
        "trace": traceback.format_exc()
    })

