from core.utils import *
from core.log import logger
from langchain.prompts import PromptTemplate
import pandas as pd
from langchain.chains import LLMChain
from langchain_google_genai import GoogleGenerativeAI
import asyncio
import os
<<<<<<< HEAD
os.environ['GOOGLE_API_KEY']=os.getenv("GOOGLE_API_KEY")

import api
llm_overall=GoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
=======
from core.function import append_to_excel

os.environ['GOOGLE_API_KEY']=os.getenv("GOOGLE_API_KEY")

import api
llm_chat=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.5)
>>>>>>> ayan2
import json


async def qt_generation(question,output,df: pd.DataFrame) -> str:
    template = """
  You are given a dataset with the following information:

User Question: {question}  
Columns: {name}  
datatype column:{type}
Sample Data: {sample}  

Task: Generate 5 simple analytical follow-up questions for broad data exploration and within 4 seconds.
Guidelines:  
- Keep questions basic, aggregated, and insight-oriented.  
- Use the provided column names in the questions.  
- Ensure questions are answerable with simple pandas operations (groupby, sum, mean, sort_values, value_counts).  
- Focus on overall patterns, totals, averages, rankings, and trends.  
- Avoid complex, overly technical, or niche analysis.  

Example: "What are the top 5 `ITEM_NAME` by total `LINE_VALUE`?"  

Output format (JSON only):  
{{
  "Questions": ["Q1", "Q2", "Q3", "Q4", "Q5"]
}}
"""
    prompt = PromptTemplate(template=template, input_variables=["name", "type", "sample","question"])
<<<<<<< HEAD
    chain =LLMChain(prompt=prompt,llm=llm_overall)
    result = await chain.ainvoke({
        "name": df.columns.tolist(),
        "type": df.dtypes.astype(str).tolist(),
        "sample": df.head(1).to_json(orient="records"),
        "question":question,
    })
    return result['text']
=======
    prompt_formatted_str = prompt.format(            name=df.columns.tolist(),
        type= df.dtypes.astype(str).tolist(),
            sample= df.head(1).to_json(orient="records"),
            question=question,)

    chain =prompt | llm_chat
    with get_openai_callback() as cb:
            
        result = await chain.ainvoke({
            "name": df.columns.tolist(),
            "type": df.dtypes.astype(str).tolist(),
            "sample": df.head(1).to_json(orient="records"),
            "question":question,
        })

        await append_to_excel("Overall QT Generation",question,prompt_formatted_str,result.usage_metadata["total_tokens"],result.usage_metadata["input_tokens"],result.usage_metadata["output_tokens"],0,"llm_results.xlsx",result.content)

        return {
        "result":result.content.replace("```json","").replace("```",""),
        "input_tokens":result.usage_metadata["input_tokens"],
        "output_tokens":result.usage_metadata["output_tokens"],
        "total_tokens":result.usage_metadata["total_tokens"]
        }
>>>>>>> ayan2


# ===============================
# 🔹 Generate Python Code from Question (async)
# ===============================
async def async_tb_table(question: str, df: pd.DataFrame) -> str:
    column_dtypes = df.dtypes.astype(str).to_dict()

    prompt = """
You are an expert in Python and Pandas. Generate Python code based on the user's question: {question}, using the given DataFrame df.
import all necessary libraries ex: import pandas as pd.
always sort the value from high to low.
### Guidelines:

always use df=df.copy()
1. DataFrame details:
   - Column names: {df}
   - Column datatypes: {datatype}
   - Sample data: {sample}
2. Output must be a Pandas DataFrame named `output_df`.
3. No irrelevant imports, no sample data creation.
4. Date format is (DD-MM-YYYY) in string.
5. Do NOT define any functions.
6. use .contains() and .lower() in built function.
7. Dont write comments in code. 
8. Write Optimized code which will work fast.
9. Always use .reset_index()


# Your code starts below:

    """
    formatted_prompt = PromptTemplate(
        template=prompt,
        input_variables=["question", "df", "datatype", "sample"]
    ).format(
        question=question,
        df=df.columns.tolist(),
        datatype=column_dtypes,
        sample=df.sample(min(3, len(df))).to_dict(orient="records")
    )
<<<<<<< HEAD

    result = await asyncio.to_thread(llm_overall.invoke, formatted_prompt)
    code = result.replace("```python", "").replace("```", "")
    logger.info(f"{question}:{code}")
    return code
=======
    with get_openai_callback() as cb:
        result = await llm_chat.ainvoke(formatted_prompt)
        
        await append_to_excel("Overall Data Code Generation",question,formatted_prompt,result.usage_metadata["total_tokens"],result.usage_metadata["input_tokens"],result.usage_metadata["output_tokens"],0,"llm_results.xlsx",result.content)

        code = result.content.replace("```python", "").replace("```", "")
        # logger.info(f"{question}:{code}")
        return {"code":code,        "input_tokens":result.usage_metadata["input_tokens"],
        "output_tokens":result.usage_metadata["output_tokens"],
        "total_tokens":result.usage_metadata["total_tokens"]}
>>>>>>> ayan2


# ===============================
# 🔹 Handler to execute all questions concurrently
# ===============================
async def handler(questions_json: str,df) -> dict:
    questions = json.loads(questions_json)["Questions"]
    code_tasks = [async_tb_table(q, df) for q in questions]
    code_results = await asyncio.gather(*code_tasks)
<<<<<<< HEAD

    result_data = {}
    for question, code in zip(questions, code_results):
        local_vars = {"df": df, "output_df": None}
        try:
            exec(code, local_vars)
            result_data[question] = local_vars["output_df"].to_json(orient='records')
        except Exception as e:
            result_data[question] = f"Execution Error: {str(e)}"
    return result_data
=======
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    result_data = {}
    for question, code in zip(questions, code_results):
        codes = code["code"]
        input_tokens += code["input_tokens"]
        output_tokens += code["output_tokens"]
        total_tokens += code["total_tokens"]
        local_vars = {"df": df, "output_df": None}
        try:
            exec(codes, local_vars)
            result_data[question] = local_vars["output_df"].to_json(orient='records')
        except Exception as e:
            result_data[question] = f"Execution Error: {str(e)}"
    return {"result": result_data,                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens}
>>>>>>> ayan2

# deploped 10 sept 

async def final_insight(prompt,ans_bundle):
    template = """
Analyze the provided data to extract critical business insights. Write optimized code

Module:
{prompt}

Instructions:
- No need to provide table
- Use small font size 14px.
- Follow these rules:
    - Use subpoints.
    - Bold key figures (e.g., **52 million**, **72%**, etc.) with navy color. No need to mention currency symbol.
    - Use emojis (📊, 💡, 🚨, etc.) to enhance visual communication
    - Max 3 examples per topic
    - Avoid paragraphs, use bullets
    - Ignore nulls, gaps, limitations
    - Provide short points.
    - Dont write any css.
    - Provide all the content into html code with css only.
---


You are a front-end UI expert. Generate a modern, responsive HTML dashboard using **Tailwind CSS**, **Google Fonts (Poppins)**, and **Material Icons**. Follow these design and layout rules:

<<<<<<< HEAD
=======
Link css using :  <!-- ✅ Tailwind CSS CDN (with forms + container-queries plugins) -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>



>>>>>>> ayan2
1. **Use Tailwind CSS via CDN** (`https://cdn.tailwindcss.com?plugins=forms,container-queries`).
2. **Use Poppins font** via Google Fonts and apply it to the body.
3. Use a **gradient header** (`from-indigo-500 to-pink-500`) with only a **title** with rounded corners and font size 25px.
4. Use **rounded cards** with **shadow**, **hover animation**, and **padding**. Cards should be in a vertical `grid gap-8` layout.
5. Each card should:
    - Have a **left icon box** using a soft accent background (`purple-100`, `pink-100`, etc.).
    - Include a **section heading** and very short description with column used (e.g. Distribution by Value , Tax included Tax, Total quantity). Do not use underscore use nautral language like qunatity , total quantity.
    - Contain a **highlighted result or insight**, such as a large number or tag.
    - Card padding should be only **10px** .
    - Use points.

6. Ensure responsive spacing (`p-4 md:p-8`) and clean, readable text hierarchy (`text-xl`, `text-2xl`, `font-semibold`, etc.).
7. Use utility classes for **colors**, **rounded corners**, **flex layout**, **spacing**, and **typography**. No external CSS or JS.
8. Include relevant **Material Icons** for each section (like `insights`, `lightbulb`, etc.).
9. Keep the design minimal and modern with **subtle interactivity** (`hover:shadow-2xl`, `hover:-translate-y-1`, etc.).
10.Cards should be in 2 columns write only key figures.
11. Set the Margin between the cards to 10px.
12. Write optimized and fast code without comments.
Output a full HTML file with `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` sections.


#### 📥 Input:
Data for Analysis:
{data}


    """
    prompt = PromptTemplate(template=template, input_variables=['data','prompt'])
<<<<<<< HEAD
    chain = prompt | llm_overall
    return chain.invoke({"data": ans_bundle,'prompt':prompt})
=======
    prompt_formatted_str = prompt.format(data=ans_bundle,prompt=prompt)

    chain = prompt | llm_chat
    with get_openai_callback() as cb:
        result=await chain.ainvoke({"data": ans_bundle,'prompt':prompt})
        await append_to_excel("Overall Final Insight ","",prompt_formatted_str,result.usage_metadata["total_tokens"],result.usage_metadata["input_tokens"],result.usage_metadata["output_tokens"],0,"llm_results.xlsx",result.content)
          
        return {"result":result.content,
        "input_tokens":result.usage_metadata["input_tokens"],
        "output_tokens":result.usage_metadata["output_tokens"],
        "total_tokens":result.usage_metadata["total_tokens"]
        }
>>>>>>> ayan2
