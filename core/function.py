import re
from concurrent.futures import ThreadPoolExecutor
import asyncio
from core.config import LOG_PATH as LOG_FILE
from datetime import datetime, timedelta
from core.utils import * 
from core.log import logger
import random



executor = ThreadPoolExecutor(max_workers=50)

def clean_response(result):
    result=result.replace("**","\\b")
    result = re.sub(r'\\b(.*?)\\b', r'<strong>\1</strong>', result)
    result=result.replace("```json","").replace("```","")
    result=result.replace("##","")
    return result

_excel_lock = asyncio.Lock()

async def append_to_excel(
    
    prompt: str,
    user_request:str,
    detailed_prompt:str,
    total_tokens: int,
    prompt_tokens: int,
    completion_tokens: int,
    cost: float,
    excel_file: str = "llm_results.xlsx",
    response:str="LLM is generating response"
):
    INPUT_COST_PER_MILLION = 0.10   # USD   
    OUTPUT_COST_PER_MILLION = 0.40  # USD
    cost = ((prompt_tokens / 1_000_000) * INPUT_COST_PER_MILLION) + \
       ((completion_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION)

    now= datetime.now()
    row = {
        "Date": now.strftime("%Y-%m-%d"),
        "Time": now.strftime("%H:%M:%S"),
        "Process": prompt,
        "Prompt":detailed_prompt,
        "User Request":user_request,
        "User ID": "demo",
        "Total Tokens": total_tokens,
        "Prompt Tokens": prompt_tokens,
        "Completion Tokens": completion_tokens,
        "Total Cost (USD)": cost,
        "Response":response
    }

    async with _excel_lock:  # ensures only one write at a time
        def _write_row():
            if os.path.exists(excel_file):
                try:
                    df = pd.read_excel(excel_file)
                    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                except Exception:
                    # If file is corrupted, start fresh
                    df = pd.DataFrame([row])
            else:
                df = pd.DataFrame([row])
            df.to_excel(excel_file, index=False)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _write_row)

def run_in_thread(func, *args):
    """Helper to run sync code in threadpool"""
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(executor, func, *args)

def format_answer(answer):
    answer=answer.replace("**","\\b")
    answer = re.sub(r'\\b(.*?)\\b', r'<strong>\1</strong>', answer)
    return answer


def clean_old_logs():
    try:
        with open(LOG_FILE, "r") as f:
            read = f.readlines()

        to_remove = []
        date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")

        for i in read:
            if i.startswith(date) and ("[WARNING]" in i or "[INFO]" in i):
                to_remove.append(i)

        cleaned = [line for line in read if line not in to_remove]

        with open(LOG_FILE, "w") as f:
            f.writelines(cleaned)

        print(f"🧹 Cleaned {len(to_remove)} old log lines from {LOG_FILE}")

    except FileNotFoundError:
        print(f"⚠️ Log file '{LOG_FILE}' not found — skipping cleanup.")
    except Exception as e:
        print(f"❌ Error during log cleanup: {e}")
        
        
        
async def insert_into_tables(
    mst_track_tokens_data=None,
    mst_report_history_data=None
):
    """
    Inserts data into MST_TRACK_TOKENS and MST_REPORT_HISTORY tables.
    
    Parameters
    ----------
    dsn : str
        Oracle DSN string (host:port/service_name)
    user : str
        Oracle username
    password : str
        Oracle password
    mst_track_tokens_data : dict
        Dictionary with keys matching columns of MST_TRACK_TOKENS
    mst_report_history_data : dict
        Dictionary with keys matching columns of MST_REPORT_HISTORY
        
        
        
    """
    
    
    chatname= await get_chat_name(mst_report_history_data.get("VC_CHAT_ID"),mst_report_history_data.get("VC_REPORT_NAME"),mst_report_history_data.get("VC_USER_NAME"))
    if chatname and (mst_report_history_data["VC_CHAT_ID"] not in chatname):
        mst_report_history_data["VC_CHAT_NAME"]=chatname
    print(mst_report_history_data["VC_CHAT_NAME"])
    
    
    
    connection = await create_connection_ebizai()
    cursor = connection.cursor()
    # ---------------------------
    # Insert into MST_TRACK_TOKENS
    # ---------------------------
    if mst_track_tokens_data:
        query1 = """
            INSERT INTO MST_TRACK_TOKENS
            (
                VC_CHAT_ID,
                DT_DATETIME,
                VC_USER_REQUEST,
                VC_PROCESS_NAME,
                NU_INPUT_TOKENS,
                NU_OUTPUT_TOKENS,
                NU_TOTAL_TOKENS,
                NU_TOTAL_COST,
                NU_INPUT_TOKEN_COST,
                NU_OUTPUT_TOKEN_CODE,
                VC_USER_NAME
            )
            VALUES (:chat_id, :dt_datetime, :user_request, :process_name,
                    :in_tokens, :out_tokens, :total_tokens, :total_cost,
                    :input_cost, :output_cost, :user_name)
        """

        cursor.execute(query1, {
            "chat_id": mst_track_tokens_data.get("VC_CHAT_ID"),
            "dt_datetime": mst_track_tokens_data.get("DT_DATETIME", datetime.now()),
            "user_request": mst_track_tokens_data.get("VC_USER_REQUEST"),
            "process_name": mst_track_tokens_data.get("VC_PROCESS_NAME"),
            "in_tokens": mst_track_tokens_data.get("NU_INPUT_TOKENS"),
            "out_tokens": mst_track_tokens_data.get("NU_OUTPUT_TOKENS"),
            "total_tokens": mst_track_tokens_data.get("NU_TOTAL_TOKENS"),
            "total_cost": mst_track_tokens_data.get("NU_TOTAL_COST"),
            "input_cost": mst_track_tokens_data.get("NU_INPUT_TOKEN_COST"),
            "output_cost": mst_track_tokens_data.get("NU_OUTPUT_TOKEN_CODE"),
            "user_name": mst_track_tokens_data.get("VC_USER_NAME"),
        })

    # ---------------------------
    # Insert into MST_REPORT_HISTORY
    # ---------------------------
    if mst_report_history_data:
        query2 = """
            INSERT INTO MST_REPORT_HISTORY
            (
                VC_USER_NAME,
                VC_CHAT_ID,
                DT_CHAT_DATE,
                VC_USER_REQUEST,
                CL_PD_QUERY,
                VC_CHAT_NAME,
                DT_QUERY_TIME,
                CL_SQL_QUERY,
                CL_RESPONSE,
                DT_RESPONSE_TIME,
                VC_REPORT_NAME,
                BL_GRAPH
            )
            VALUES (
            :user_name,:chat_id, :chat_date, :user_request, :pd_query, :chat_name,
                    :query_time, :sql_query, :response, :response_time,
                    :report_id, :graph_blob
                    )
        """

        cursor.execute(query2, {
            "user_name":mst_report_history_data.get("VC_USER_NAME"),
            "chat_id": mst_report_history_data.get("VC_CHAT_ID"),
            "chat_date": mst_report_history_data.get("DT_CHAT_DATE", datetime.now()),
            "user_request": mst_report_history_data.get("VC_USER_REQUEST"),
            "pd_query": mst_report_history_data.get("CL_PD_QUERY"),
            "chat_name": mst_report_history_data.get("VC_CHAT_NAME"),
            "query_time": mst_report_history_data.get("DT_QUERY_TIME", datetime.now()),
            "sql_query": mst_report_history_data.get("CL_SQL_QUERY"),
            "response": mst_report_history_data.get("CL_RESPONSE"),
            "response_time": mst_report_history_data.get("DT_RESPONSE_TIME", datetime.now()),
            "report_id": mst_report_history_data.get("VC_REPORT_ID"),
            "graph_blob": mst_report_history_data.get("BL_GRAPH"),  # should be bytes
        })

    connection.commit()
    cursor.close()
    connection.close()

    print("Data uploaded successfully!")
    
async def update_history_flexi(data=None,token=None):
  try:
    connection = await create_connection_ebizai()
    cursor = connection.cursor()
    
    
    if data is not None:
      chatname= await get_chat_name(data.get("VC_CHAT_ID"),data.get("VC_REPORT_NAME"),data.get("VC_USER_NAME"))
      print(chatname)
      if chatname and (data["VC_CHAT_ID"] not in chatname):
        data["VC_CHAT_NAME"]=chatname
        print(data["VC_CHAT_NAME"])
      else:
        try:
          response = await llm.ainvoke(
    f"""
Based on the following user questions, generate a short descriptive
chat title (max 5 words). Just 5 words only.
Without any instruction or extra words.

{data.get('VC_USER_REQUEST')}
"""
)
          print(response)
          data["VC_CHAT_NAME"]=response
        except Exception as e:
          print("Error generating Chat_name:",e)
          
        

        
        
        
      
      update_query = """
            UPDATE MST_REPORT_HISTORY
            SET 
                CL_RESPONSE = :response ,
                VC_CHAT_NAME = :chat_name
            WHERE VC_CHAT_ID = :chat_id
              AND DBMS_LOB.SUBSTR(VC_USER_REQUEST, 4000) = :question
              AND VC_REPORT_NAME = :report_name
              AND VC_USER_NAME = :user_name
              AND TRUNC(DT_CHAT_DATE) = TRUNC(:chat_date)
        """
      
      cursor.execute(update_query, {
            "response": data.get("CL_RESPONSE"),
            "chat_id": data.get("VC_CHAT_ID"),
            "question": data.get("VC_USER_REQUEST"),
            "report_name": data.get("VC_REPORT_NAME"),
            "chat_date": data.get("DT_CHAT_DATE", datetime.now()),
            "user_name":data.get("VC_USER_NAME"),
            "chat_name": data.get("VC_CHAT_NAME")
        })
      cursor.execute("""
      
      UPDATE MST_REPORT_HISTORY
      SET VC_CHAT_NAME = :new_request
      WHERE VC_CHAT_ID = :chat_id
        AND VC_REPORT_NAME = :report_name
        AND VC_USER_NAME = :user_name
        AND VC_USER_REQUEST = 'Overall'
  
  """,
     {
      "new_request": data.get("VC_CHAT_NAME"),
      "chat_id": data.get("VC_CHAT_ID"),
      "report_name": data.get("VC_REPORT_NAME"),
      "user_name": data.get("VC_USER_NAME")
      }
      )
        


    if token is not None:
            token_update_query = """
                UPDATE MST_TRACK_TOKENS
                SET
                    NU_INPUT_TOKENS  = NVL(NU_INPUT_TOKENS, 0)  + :input_tokens,
                    NU_OUTPUT_TOKENS = NVL(NU_OUTPUT_TOKENS, 0) + :output_tokens,
                    NU_TOTAL_TOKENS  = NVL(NU_TOTAL_TOKENS, 0)  + :total_tokens
                WHERE VC_PROCESS_NAME = :process_name
                  AND DBMS_LOB.SUBSTR(VC_USER_REQUEST, 4000) = :user_request
                  AND VC_CHAT_ID = :chat_id
                  AND VC_USER_NAME = :user_name
            """

            cursor.execute(token_update_query, {
                "input_tokens": token.get("NU_INPUT_TOKENS", 0),
                "output_tokens": token.get("NU_OUTPUT_TOKENS", 0),
                "total_tokens": token.get("NU_TOTAL_TOKENS", 0),
                "process_name": token.get("VC_PROCESS_NAME"),
                "user_request": token.get("VC_USER_REQUEST"),
                "chat_id": token.get("VC_CHAT_ID"),
                "user_name": token.get("VC_USER_NAME")
            })
            
            
    connection.commit()
    cursor.close()
    connection.close()
    logger.info("Data Updated Successfully")
    
      
    
    
    
  except Exception as e:
    logger.error(e)
    



async def get_chat_name(chat_id, report_name, user_name):
    connection = await create_connection_ebizai()
    cursor = connection.cursor()

    query = """
        SELECT VC_CHAT_NAME
        FROM MST_REPORT_HISTORY
        WHERE VC_CHAT_ID = :chat_id
          AND VC_REPORT_NAME = :report_name
          AND VC_USER_NAME = :user_name
          AND VC_CHAT_NAME IS NOT NULL
          AND VC_USER_REQUEST <> 'Overall'
        FETCH FIRST 1 ROWS ONLY
    """

    cursor.execute(query, {
        "chat_id": chat_id,
        "report_name": report_name,
        "user_name": user_name
    })

    row = cursor.fetchone()
    cursor.close()
    connection.close()

    return row[0] if row else None