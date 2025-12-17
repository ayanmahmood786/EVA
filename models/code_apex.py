
from langchain.prompts import PromptTemplate
import asyncio
import api
from core.utils import *
from core.log import logger
from core.function import append_to_excel





def format_history(history):
    lines = []
    for msg in history.messages:
        role = "User" if msg.type == "human" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines[-10:])


async def generate_apex_pandas_code(question, df, detailed_prompt, llm, history):
    try:
        list1 = [df[i].dtype for i in df.columns]
        prompt_template = """
    You are an expert in Python and Pandas. Generate Python code based on the user's question, using the given DataFrame `df`.
    


    ### Guidelines:

    **Do Not create a dummy DataFrame for any purpose.

    1. **DataFrame Details**:
    - Column names: {df} use always these names while generating the code.
    - Column datatypes: {datatype}
    - Sample data present in the table: {sample}
    - Null values in each column: {null}


    2. The output must be a Pandas DataFrame named `output_df`. If no relevant columns match the question or not have converstaion related to that query. 
    3. Use explicit imports for all necessary libraries (e.g., `import pandas as pd`) to prevent errors.
    4. Do not create or assume sample data, alter the DataFrame, or include any functionality beyond answering the question.
    5. Include concise comments in your code for clarity.
    6. Use str.contains() and str.lower() function for finding string always rather than ==.
    7. Date is in DD-MM-YYYY.
    8. Always write the full code.
    9. Always merge everything into a single output_df.
    10. fill numerical null values columns with fillna(0).
    11. Always filter the data with top 10 and bottom 10 in each section.

    ### Key Points:
    - Do not produce a sample data or dataframe
    - Avoid Recursion 
    - Output only the Python code; no explanations, text, or examples.
    - No Need to write functions.
    - always use reset_index() and try to provide name columns with metrics for better understanding.
    - **Output Structure**:
        - Organize results in a logical, hierarchical structure
        - Include both detailed and summary-level information
        - Provide clear labeling and section headers
        - Ensure proper formatting and rounding of numeric values
        - Maintain consistent column ordering and naming conventions


    Detailed Instruction to generate the code:
        {detailed_prompt}


    conversation history:
        {conversation_history}

    Question:
    {question}

    sample code format:
    final_output = {{
        'Product Summary': product_classification.to_dict(orient='records'),
        'Warehouse Summary': warehouse_summary.to_dict(orient='records'),
        'Warehouse Wise Product Dead Stock': warehouse_wise_products.to_dict(orient='records'),
        'Highest/Lowest Warehouse per Product': output_df_transfer.to_dict(orient='records')
    }}

    # --- Summary counts ---
    total_products = dead_stock['PRODUCT_NAME'].nunique()
    total_qty = dead_stock['Total Dead Stock'].sum()
    total_val = dead_stock['Total Dead Stock Value'].sum()

    summary_df = pd.DataFrame([{{
        'Section': 'Summary',
        'Total Products': total_products,
        'Total Dead Stock Qty': total_qty,
        'Total Dead Stock Value': total_val
    }}])

    # Combine summary with other sections
    frames = [summary_df]
    for section, data in final_output.items():
        df_section = pd.DataFrame(data)
        df_section.insert(0, 'Section', section)
        frames.append(df_section)

    output_df = pd.concat(frames, ignore_index=True)

    # Your code starts below:
    """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["question", "df", "datatype", "sample", "detailed_prompt","conversation_history","null"],
        )

        prompt_str = {
            "question": question,
            "df": df.columns,
            "datatype": list1,
            "sample": df.head(1),
            "detailed_prompt":detailed_prompt,
            "conversation_history":format_history(history),
            "null":df.isnull().sum()
        }
        prompt_formatted_str = ""
        chain = prompt | llm 

        generated_code = await asyncio.wait_for(
                    chain.ainvoke(prompt_str),
                    timeout=1200,
                )

        return {
        "code":generated_code.content,
        "input_tokens":generated_code.usage_metadata["input_tokens"],
        "output_tokens":generated_code.usage_metadata["output_tokens"],
        "total_tokens":generated_code.usage_metadata["total_tokens"]
        }
    except Exception as e:
        logger.error(e)
        return None
#    finally:
#        await append_to_excel("FLEXI-Report Framework Data Sorting",question,prompt_str,generated_code.usage_metadata["total_tokens"],generated_code.usage_metadata["input_tokens"],generated_code.usage_metadata["output_tokens"],0)