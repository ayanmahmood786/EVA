import oracledb
import pandas as pd
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import pandas as pd
# FastAPI initialization
import logging
from fastapi import FastAPI, HTTPException, Request ,UploadFile, Form,File
from fastapi.responses import FileResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from core.function import append_to_excel


model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=1)
# llm = genai.GenerativeModel("gemini-2.0-flash",generation_config={"temperature":0.5})
#Loggers
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

# df=None

# # {
# # sql_query="SELECT * FROM Purchase_AI where  \"Company Code\"='05' "
# # #   "user": "makess",
# # #   "password": "makess",
# # #   "dsn": "192.168.5.68:1521/ghana"
# # # //   "question":"No of orders made in year 2022"
# # # }

# # connection = cx_Oracle.connect(user="ebizai", password="ebizai", dsn="192.168.5.190:1521/ORCL")
# # # Fetch data from the database and load into a pandas DataFrame
# # df = pd.read_sql(sql_query, con=connection)
# # logger.info(f"DataFrame Created succesfully {df.head(2)}")
# app=FastAPI()



# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Specify the allowed origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )



# '''----------------------------------------------  Function   -----------------------------------------'''

# # def data(sql_query,user,password,dsn):
# #     connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
# #     # Fetch data from the database and load into a pandas DataFrame
# #     df = pd.read_sql(sql_query, con=connection)
# #     return df

def excel_table(question,df):
    try:
        list1=[]
        for i in df.columns:
            list1.append(df[i].dtype)
        prompt = """You are an expert in Python and Pandas. Generate Python code based on the user's question: {question}, using the provided DataFrame named `external_df`.

    ### Guidelines:

    1. **DataFrame Context**:
    - Column names: {df}
    - Column data types: {datatype}
    - Sample data: {sample}
    - Null values per column: {null_values}
    - Fill all null values with an empty string (`''`) before performing any operations.

    2. **Code Output Requirements**:
    - The final output must be a Pandas DataFrame named `output_df`.
    - If the question is unrelated to the DataFrame columns, set `output_df = None`.
    - Do not create or modify sample data. Use only the provided `external_df`.

    3. **Import & Style Rules**:
    - Always include explicit imports (e.g., `import pandas as pd`, `import numpy as np`).
    - Avoid defining functions, classes, or unnecessary helpers.
    - Write concise, readable, and safe code blocks with brief comments explaining each logical step.

    4. **Data Handling & Safety**:
    - Replace NaN/None values with empty strings (`''`) before performing operations.
    - Convert numeric-like columns stored as objects into numeric dtype safely using:
        ```python
        external_df['column'] = pd.to_numeric(external_df['column'], errors='coerce').fillna(0)
        ```
    - This prevents errors such as:
        - `TypeError: Column 'X' has dtype object, cannot use method 'nlargest' with this dtype`
    - Before using `.nlargest()`, `.sort_values()`, or mathematical operations, ensure the column is numeric.
    - Convert columns to string only when necessary (e.g., for text concatenation or string matching).
    - Limit outputs to 100 rows using `.head(100)` for safety.
    - Use lowercase (`.str.lower()`) for case-insensitive matching.
    - Always ensure relevant identifiers are preserved in the output (e.g., “supplier” for top suppliers).

    5. **Logical Pandas Functions to Use (as applicable)**:
    - **Filtering & Selection**: `.loc[]`, `.iloc[]`, `.query()`
    - **String Operations**: `.str.lower()`, `.str.contains()`, `.str.strip()`, `.str.replace()`
    - **Aggregation & Grouping**: `.groupby()`, `.agg()`, `.sum()`, `.mean()`, `.count()`, `.nunique()`
    - **Sorting & Ranking**: `.sort_values()`, `.nlargest()`, `.nsmallest()`
    - **Merging & Joining**: `.merge()`, `.join()`, `.concat()`
    - **Null Handling**: `.fillna('')`, `.dropna()`
    - **Unique & Duplicates**: `.drop_duplicates()`, `.duplicated()`
    - **Conditional Logic**: `np.where()`, `.apply()`, or boolean indexing
    - **Column Operations**: `.assign()`, `.rename()`, `.astype()`
    - **Output Limiting**: `.head(100)` to ensure row-safety

    6. **Error Handling**:
    - Always guard against:
        - `TypeError: can only concatenate str (not "float") to str`
        - `TypeError: Column 'X' has dtype object, cannot use method 'nlargest' with this dtype`
        - Any log-style error messages such as:
        `2025-10-29 11:42:33,507 [ERROR] EVA - Error: Column 'X' has dtype object, cannot use method 'nlargest' with this dtype`

    7. **Output Format**:
    - Output **only valid Python code** — no markdown, explanations, or commentary.
    - Ensure the final line defines `output_df`.
    - The code must be directly executable as-is.

    ### Key Instructions:
    - Use only Pandas and built-in Python functions.
    - Do not assume or synthesize new data.
    - Always ensure `output_df` exists in the final code (even if set to `None`).

    # Your code starts below:
        """
        prompt = PromptTemplate(template=prompt
        , input_variables=["question","df","datatype","sample","null_values"])
        prompt_formatted_str = prompt.format(
            question=question,df=df.columns,datatype=list1,sample=df.sample(),null_values=df.isnull().sum()
        )
        prediction = model.invoke(prompt_formatted_str)
        # prediction =prediction.text
        prediction1=prediction.content.replace("```python","")
        prediction1=prediction.replace("```","")
        return prediction1
    except Exception as e:
        print(e)
    finally:
        append_to_excel("NLP Excel",question,prompt_formatted_str,prediction.usage_metadata["total_tokens"],prediction.usage_metadata["input_tokens"],prediction.usage_metadata["output_tokens"],0,"llm_results.xlsx",prediction1)

# def python_graph(dataframe):
#     temp_df=pd.DataFrame(json.loads(dataframe["Dataframe"]))
#     datatype=[]
#     uni=[]
#     for i in temp_df.columns:
#         datatype.append(temp_df[i].dtype)
#         uni.append(len(temp_df[i].unique()))
#     prompt = """
# You are a world-class Python graph generator specializing in creating visually appealing and insightful graphs using Matplotlib and Seaborn. 
# Your task is to generate the most appropriate graph based on the data provided. 
# plot for multiple columns if possible.
# Graphs : 1. Pie 2. Bar 3. Line 4.[kde,scatter,violin]
# Key guidelines:
# 1. Focus only on four graph generation—no need to write functions or additional logic outside of plotting. like a dashboard 2 graphs in a row and 2 more in the next row
# 2. Do not use any libraries other than Matplotlib and Seaborn.
# 3. Do not generate or assume any sample data. The data is provided in a dataframe called `temp_df`.
# 4. Use the dataframe `temp_df` directly without altering its data.
# 5. Base your graph design on the following data characteristics:
#    - Columns: {df}
#    - Datatypes of columns: {datatype}
#    - Sample data: {sample}
#    - Shape of the dataframe: {shape}
#    - No of unique values :{uni}
# 6. Do not modify, generate, or assume any additional data.
# 7. At the end use plt.tightlayout()
# 8. Write only the Python code—avoid comments, explanations, or any extra details.


# # Your code starts below:
# """
#     prompt=PromptTemplate(template=prompt,input_variables=["df","datatype","sample","shape","uni"])
#     prompt_formatted=prompt.format(df=temp_df,datatype=datatype,sample=temp_df.sample(),shape=df.shape,uni=uni)
#     response=model.invoke(prompt_formatted)
#     response=response.replace("```python","").replace("```","").replace("plt.show()","")
#     plt.clf()
#     exec(response)
#     plt.savefig("output.jpg")
#     return "output.jpg"
    
    
# def question_enhancer(question,e,data_columns):
#     prompt="""
#     Based on the given question :{question}
#     You are getting an error: {e}
#     Remeber if the output is coming to be None then there is problem in the question.
#     if you can't generate any relevant question based on the error then write a new question based on the given column names:{data_columns}
#     So enhance the question based on the error and provide a best question:
#     No need to write the explanation just provide a question.
#     Write some complex question.
#     Enhance the given question or suggest a new question.

#     Question:""

#     """
#     prompt=PromptTemplate(template=prompt,input_variables=["question","e","data_columns"])
#     prompt_formatted=prompt.format(question=question,e=e,data_columns=data_columns)
#     prediction=model.invoke(prompt_formatted)
#     return prediction

def relevant_table(question,df):
    list1=[]
    for i in df.columns:
        list1.append(df[i].dtype)

    prompt = """
You are an expert in Python and Pandas. Generate Python code based on the user's question: {question}, using the given DataFrame `df`.

### Guidelines:
1. **DataFrame Details**:
   - Column names: {df}
   - Column datatypes: {datatype}
   - Sample data: {sample}
2. The output must be a Pandas DataFrame named `output_df`. If no relevant columns match the question, set `output_df = None`.
3. Use explicit imports for all necessary libraries (e.g., `import pandas as pd`) to prevent errors.
4. Do not create or assume sample data, alter the DataFrame, or include any functionality beyond answering the question.
5. Include concise comments in your code for clarity.

### Key Points:
- Do not produce a sample data or dataframe
- Avoid Recursion 
- Output only the Python code; no explanations, text, or examples.
- If the question is unrelated to the DataFrame, return `None` for `output_df`.
- No Need to write functions
# Your code starts below:
"""

    prompt = PromptTemplate(template=prompt
    , input_variables=["question","df","datatype","sample"])
    prompt_formatted_str = prompt.format(
        question=question,df=df.columns,datatype=list1,sample=df.sample()
    )
    prediction = model.invoke(prompt_formatted_str)
    prediction =prediction
    prediction=prediction.replace("```python","")
    prediction=prediction.replace("```","")
    return prediction

# def convert_datetime_columns_to_str(df):
#     for col in df.columns:
#         # If the column is of datetime type, handle possible overflow errors
#         if df[col].dtype == "datetime64[ns]" or df[col].dtype == 'object':  # Include 'object' in case dates are strings
#             try:
#                 df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert to datetime, invalid values become NaT
#                 df[col] = df[col].astype(str)  # Convert datetime to string after handling invalid dates
#             except Exception as e:
#                 raise HTTPException(status_code=500, detail=f"Date conversion error: {str(e)}")
#     return df


'''-------------------------------------- API ---------------------------------'''


# @app.post("/questions")
# async def dataframe(query_request: QueryRequest):
#     try:
#         # Use the DataFrmae function to execute the SQL query and fetch data
#         df = data(query_request.sql_query, query_request.user, query_request.password, query_request.dsn)
#         question=query_request.question
#         code=relevant_table(question,df)
#         local_vars={"df":df,"output_df":None}
#         exec(code,{},local_vars)
#         output_df=local_vars.get("output_df")
#         output_json = {"Dataframe":output_df.to_json(orient="records", date_format="iso")}  # 'records' makes it list of dictionaries
#         return output_json
#     except Exception as e:
#         # Raise an HTTP exception with the error message
#         raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    

# @app.post("/input")
# async def creds(new_request:Creds):
#     global df  # Access the global df
#     try:
#         # Fetch the DataFrame
#         df = data(new_request.sql_query, new_request.user, new_request.password, new_request.dsn)
#         return {"message": "DataFrame stored successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


