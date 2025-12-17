from core.utils import *
from core.log import logger
import orjson
from rapidfuzz import fuzz
from langchain.schema import HumanMessage, AIMessage,SystemMessage
from models.memory import get_by_session_id, InMemoryHistory
from models.Code_generator import generate_pandas_code



llm_report = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.5)

class ReqNLP(BaseModel):
    df: str
    question:str
    sql_query:str
    session_id:str



router=APIRouter()

def similar_questions(q2):
    score = []
    with open(r"dir/Format.json", "r") as file:
        content = file.read()
        json_file = json.loads(content)

    quest_hist = list(json_file.keys())
    for i in quest_hist:
        similarity_score = fuzz.ratio(i.lower(), q2.lower())
        score.append({"question": i, "similarity": similarity_score})

    # Filter & sort scores (high → low)
    high_score = [s for s in score if s["similarity"] > 87]
    high_score_sorted = sorted(high_score, key=lambda x: x["similarity"], reverse=True)

    if high_score_sorted:
        best_match = high_score_sorted[0]["question"]
        return {
            "question": best_match,
            "Code": json_file[best_match]["Code"],
            "similarity": high_score_sorted[0]["similarity"]
        }
    else:
        return {
            "question": "No Sample Found",
            "Code": "No Sample Found",
            "similarity": 0
        }



# connection=oracledb.connect(user="makess",password="MAKESS",dsn="localhost:1575/orcl")
@retry(stop=stop_after_attempt(2), wait=wait_fixed(1), before_sleep=before_sleep_log(logger, logging.INFO), after=after_log(logger, logging.INFO))
async def handle_question_async(req: ReqNLP):
    try:
        df = None 
        question = req.question
        df_json = req.df
        logger.info(f"Question:{question}")
        history = get_by_session_id(req.session_id)
        history.add_messages([HumanMessage(content=question)])
        sample_code = similar_questions(question)
        
        if req.df != "None":
            df_dict = orjson.loads(df_json)
            df = pd.DataFrame(df_dict)
        else:
            try:
                start = time.time()
                df = pd.read_sql(req.sql_query, con=connection)
<<<<<<< HEAD
                logger.info(df.shape)
=======
                # logger.info("Data Size:", df.shape())
>>>>>>> ayan2
                print("Time Taken to load the report:", time.time() - start)
            except Exception as e:
                logger.error(e)
                raise
        
        local_vars = {"df": df, "output_df": None, "pd": pd}
        print("Columns:", df.columns.tolist())
        
        if sample_code['question'] != "No Sample Found":
            try:
                exec(sample_code['Code'], local_vars)
<<<<<<< HEAD
                logger.info(sample_code['Code'])
                output_df = local_vars.get("output_df")
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
        # Use await instead of asyncio.run() since we're already in async context
=======
>>>>>>> ayan2
        generated_code = await generate_pandas_code(question, df, sample_code, llm_report, history)
        print(f"Time Taken While Executing NLP: {time.time() - start}")

        generated_code = generated_code.replace("```python", "").replace("```", "")
<<<<<<< HEAD
        logger.info("Code Generated:\n")
        logger.info(f"{generated_code}")
=======
        logger.info("Code Generated:")
>>>>>>> ayan2
        
        start = time.time()
        exec(generated_code, local_vars)
        history.add_messages([AIMessage(content="Generated Code:" + generated_code)])    
        output_df = local_vars.get("output_df")
        try:
            if len(output_df) >= 5: 
                history.add_messages([SystemMessage(content="Data Obtained (Sample 5 data points)" + str(output_df.head(5)))])
            else:
                history.add_messages([SystemMessage(content="Data Obtained" + str(output_df.head()))])
        except Exception as e:
            history.add_messages([SystemMessage(content="Error:"+ str(e))])
            history.add_messages([AIMessage(content="Now I have to Enhance the query")])
            raise ValueError(e)    
        
        print("Data Obtained within:", time.time() - start)

        if output_df is None:
            raise ValueError("output_df is still None after retry.")

        try:
            for col in output_df.select_dtypes(include=['datetime64[ns]']).columns:
                output_df[col] = output_df[col].astype(str)
        except Exception as e:
            raise ValueError(e)

        output_json = output_df.to_json(orient="records")
<<<<<<< HEAD
        print("Output Generated Successfully")
=======
        logger.info("Output Generated Successfully")
>>>>>>> ayan2
        
        return output_json

    except Exception as e:
        import traceback
        logger.error(e)
        logger.error(traceback.format_exc())
        if 'history' in locals():
            history.add_messages([SystemMessage(content=f"Error: {str(e)}")])
        # Raise the exception instead of returning it
<<<<<<< HEAD
        raise HTTPException(status_code=404, detail={
=======
        raise HTTPException(status_code=500, detail={
>>>>>>> ayan2
            "Dataframe": [],
            "issue": str(e),
            "trace": traceback.format_exc()
        })

@router.post("/answer")
async def handle_question(req: ReqNLP):
    return await handle_question_async(req)
