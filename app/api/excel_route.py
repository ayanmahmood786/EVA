from core.utils import *
from models.nlp import excel_table, relevant_table
from io import BytesIO
from core.log import logger

'''------------------------------------ Classes ----------------------------------------------------'''

router = APIRouter()



@router.post("/excel")
async def excel_qa(file:UploadFile=File(...),question:str = Form(...)):
    try:
        time.sleep(3)
        logger.info(f"Question:{question}")
        content= await file.read()
        external_df=pd.read_excel(BytesIO(content))
        code=excel_table(question,external_df)
        logger.info(f"\n Code:{code}\n")
        local_vars={"external_df":external_df,"output_df":None}
        exec(code,{},local_vars)
        output_df=local_vars.get("output_df")
        if output_df is None:
            raise ValueError("output_df is None, unable to process.")
        logger.info("Output Generated Successfully")
        output_json = {"Dataframe": output_df.to_json(orient="records", date_format="iso"),"res":""}
        return output_json

    except Exception as e:
        import traceback
        print("trace",traceback.format_exc())
        logger.error("Error: %s", e)
        return { "Dataframe" : [],
        "issue": e,
        "res": None}
