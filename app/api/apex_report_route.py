from core.utils import *
from core.log import logger
from models.code_apex import generate_apex_pandas_code
from langchain.schema import HumanMessage, AIMessage,SystemMessage
from models.memory import get_by_session_id, InMemoryHistory
from models.Code_generator import generate_pandas_code
<<<<<<< HEAD

=======
from core.function import insert_into_tables
>>>>>>> ayan2

from api.flexi_report import similar_questions


class APEX(BaseModel):
    detailed_prompt: str
    question:str
    sql_query:str
    session_id:str

<<<<<<< HEAD
=======
class APEXHISTORY(BaseModel):
    report_name:str
    chat_id:str
    user_id:str
    detailed_prompt: str
    question:str
    sql_query:str
    session_id:str
>>>>>>> ayan2

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
<<<<<<< HEAD
        logger.info(f"Detailed Prompt\n:{req.detailed_prompt}")
=======
>>>>>>> ayan2
        history = get_by_session_id(req.session_id)
        history.add_messages([HumanMessage(content=question)])
        sample_code=similar_questions(question)
         
        
        try:
            start = time.time()
            df = pd.read_sql(req.sql_query, con=connection)
<<<<<<< HEAD
            logger.info(df.head())
            logger.info(df.shape)
=======
            logger.info(f"Data Size:{len(df)}")
>>>>>>> ayan2
            print("Time Taken to load the report:", time.time() - start)
        except Exception as e:
            logger.error(e)
            raise ValueError(detail=e,status_code=786)
        
        local_vars = {"df": df, "output_df": None, "pd": pd}
<<<<<<< HEAD
        print("Columns:", df.columns.tolist())
=======
>>>>>>> ayan2
        if sample_code['question'] != "No Sample Found":
            try:
                logger.info("Entering Database Codes"*5)
                exec(sample_code['Code'], local_vars)
<<<<<<< HEAD
                logger.info(sample_code['Code'])
                output_df = local_vars.get("output_df")
                print(output_df.shape)
                print(output_df.columns.tolist())
                logger.info(output_df.to_json(orient="records"))
                
=======
                output_df = local_vars.get("output_df")

>>>>>>> ayan2
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
        
<<<<<<< HEAD
        generated_code = await generate_apex_pandas_code(question, df, req.detailed_prompt, llm, history)
=======
        generated_code = await generate_apex_pandas_code(question, df, req.detailed_prompt, llm_chat, history)
>>>>>>> ayan2
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
<<<<<<< HEAD
=======





@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), before_sleep=before_sleep_log(logger, logging.INFO), after=after_log(logger, logging.INFO))
async def handle_question_async_apex_history(req: APEXHISTORY):
    generated_code=""
    try:
        
        df = None 
        question = req.question
        # df_json = req.df
        logger.info(f"Question:{question}")
        history = get_by_session_id(req.session_id)
        history.add_messages([HumanMessage(content=question)])
        sample_code=similar_questions(question)
         
        
        try:
            start = time.time()
            df = pd.read_sql(req.sql_query, con=connection)
            logger.info(f"Data Size:{len(df)}")
            print("Time Taken to load the report:", time.time() - start)
        except Exception as e:
            logger.error(e)
            raise ValueError(detail=e,status_code=786)
        
        local_vars = {"df": df, "output_df": None, "pd": pd}
#        if sample_code['question'] != "No Sample Found":
#            try:
#                logger.info("Entering Database Codes"*5)
#                exec(sample_code['Code'], local_vars)
#                output_df = local_vars.get("output_df")
#
#                if len(output_df) >= 5:
#                    history.add_messages([AIMessage(content="Generated Code" + sample_code['Code'])])
#                    history.add_messages([SystemMessage(content="Data Obtained (Sample 5 data points)" + str(output_df.head(5)))])
#                    return output_df.to_json(orient="records")
#                elif 1 <= len(output_df) < 5:
#                    history.add_messages([AIMessage(content="Generated Code:\n" + sample_code['Code'])])
#                    history.add_messages([SystemMessage(content="Data obtained" + str(output_df.head()))])
#                    return output_df.to_json(orient="records")
#                    
#            except Exception as e:
#                logger.error(e)
#       

        
        start = time.time()
        
        generated_code = await generate_apex_pandas_code(question, df, req.detailed_prompt, llm_chat, history)
        print(f"Time Taken While Executing NLP: {time.time() - start}")

        input_tokens=generated_code["input_tokens"]
        output_tokens=generated_code["output_tokens"]
        total=generated_code["total_tokens"]


        generated_code = generated_code["code"].replace("```python", "").replace("```", "")
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
        await insert_into_tables(
            mst_track_tokens_data={
        "VC_USER_NAME": req.user_id,
        "VC_CHAT_ID": req.chat_id,
        "VC_REPORT_ID": req.report_name,
        "NU_INPUT_TOKENS": input_tokens,
        "NU_OUTPUT_TOKENS": output_tokens,
        "NU_TOTAL_TOKENS": total,
        "VC_PROCESS_NAME": "FLEXI",
        "VC_USER_REQUEST": req.question
    },
        
        
        
        
        mst_report_history_data={
        "VC_USER_NAME":req.user_id,
        "VC_CHAT_ID": req.chat_id,
        "VC_USER_REQUEST": req.question,
        "CL_PD_QUERY": generated_code,
        "VC_CHAT_NAME": f"{req.report_name}_{req.chat_id}",
        "CL_SQL_QUERY": req.sql_query,
        "CL_RESPONSE": "",
        "VC_REPORT_ID": req.report_name,
        "BL_GRAPH": "",

        })
        
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



@router.post("/answer_history")
async def handle_question(req: APEXHISTORY):
    return await handle_question_async_apex_history(req)
>>>>>>> ayan2
