from core.utils import *
from core.log import logger
from models.code_apex import generate_apex_pandas_code
from langchain.schema import HumanMessage, AIMessage,SystemMessage
from models.memory import get_by_session_id, InMemoryHistory
from models.Code_generator import generate_pandas_code


from api.flexi_report import similar_questions


class APEX(BaseModel):
    detailed_prompt: str
    question:str
    sql_query:str
    session_id:str


router=APIRouter()



# - Ayan mahmood
# 9/9/2024

@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), before_sleep=before_sleep_log(logger, logging.INFO), after=after_log(logger, logging.INFO))
async def handle_question_async_apex(req: APEX):
    try:
        df = None 
        question = req.question
        # df_json = req.df
        logger.info(f"Question:{question}")
        logger.info(f"Detailed Prompt\n:{req.detailed_prompt}")
        history = get_by_session_id(req.session_id)
        history.add_messages([HumanMessage(content=question)])
        sample_code=similar_questions(question)
         
        
        try:
            start = time.time()
            df = pd.read_sql(req.sql_query, con=connection)
            logger.info(df.head())
            logger.info(df.shape)
            print("Time Taken to load the report:", time.time() - start)
        except Exception as e:
            logger.error(e)
            raise ValueError(detail=e,status_code=786)
        
        local_vars = {"df": df, "output_df": None, "pd": pd}
        print("Columns:", df.columns.tolist())
        if sample_code['question'] != "No Sample Found":
            try:
                logger.info("Entering Database Codes"*5)
                exec(sample_code['Code'], local_vars)
                logger.info(sample_code['Code'])
                output_df = local_vars.get("output_df")
                print(output_df.shape)
                print(output_df.columns.tolist())
                logger.info(output_df.to_json(orient="records"))
                
                if len(output_df) >= 5:
                    history.add_messages([AIMessage(content="Generated Code" + sample_code['Code'])])
                    history.add_messages([SystemMessage(content="Data Obtained (Sample 5 data points)" + str(output_df.head(5)))])
                    return output_df.to_json(orient="records")
                elif 1 <= len(output_df) < 5:
                    history.add_messages([AIMessage(content="Generated Code:\n" + sample_code['Code'])])
                    history.add_messages([SystemMessage(content="Data obtained" + str(output_df.head()))])
                    return output_df.to_json(orient="records")
                    
            except Exception as e:
                logger.error(e)
       

        
        start = time.time()
        
        generated_code = await generate_apex_pandas_code(question, df, req.detailed_prompt, llm, history)
        print(f"Time Taken While Executing NLP: {time.time() - start}")

        generated_code = generated_code.replace("```python", "").replace("```", "")
        logger.info("Code Generated:\n")
        logger.info(f"{generated_code}")
        
        start = time.time()
        exec(generated_code, local_vars)
        
        history.add_messages([AIMessage(content="Generated Code:" + generated_code)])    
        output_df = local_vars.get("output_df")
        logger.info(output_df)
        try:
            if len(output_df) >= 5: 
                history.add_messages([SystemMessage(content="Data Obtained (Sample 5 data points)" + str(output_df.head(5)))])
            else:
                history.add_messages([SystemMessage(content="Data Obtained" + str(output_df.head()))])
        except Exception as e:
            history.add_messages([SystemMessage(content="Error:"+ str(e))])
            history.add_messages([AIMessage(content="Now Enhanced the query to resolve these conflicts")])
 
        
        print("Data Obtained within:", time.time() - start)
        # print("Columns:",output_df.columns())
        if output_df is None:
            raise ValueError("output_df is still None after retry.")

        try:
            for col in output_df.select_dtypes(include=['datetime64[ns]']).columns:
                output_df[col] = output_df[col].astype(str)
        except Exception as e:
            logger.info(e)
        try:
            output_json = output_df.to_json(orient="records")
        except Exception as e:
            flat_json = output_df.to_dict(orient="records")
            output_json = json.dumps(flat_json, default=str)


        print("Output Generated Successfully")
        
        return output_json

    except Exception as e:
        import traceback
        logger.error(e)
        logger.error(traceback.format_exc())
        if 'history' in locals():
            history.add_messages([SystemMessage(content=f"Error: {str(e)}")])
        # Raise the exception instead of returning it
        raise HTTPException(status_code=500, detail={
            "Dataframe": [],
            "issue": str(e),
            "trace": traceback.format_exc()
        })

@router.post("/answer1")
async def handle_question(req: APEX):
    return await handle_question_async_apex(req)
