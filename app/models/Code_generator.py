
from langchain.prompts import PromptTemplate
import asyncio





def format_history(history):
    lines = []
    for msg in history.messages:
        role = "User" if msg.type == "human" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


async def generate_pandas_code(question, df, sample_code, llm, history):
    try:
        list1 = [df[i].dtype for i in df.columns]
        prompt_template = """
    You are an expert in Python and Pandas. Generate Python code based on the user's question: {question}, using the given DataFrame `df`.



    conversation history:
    {conversation_history}



    ### Guidelines:

        **Do Not create a dummy DataFrame for any purpose.

    1. **DataFrame Details**:
    - Column names: {df}
    - Column datatypes: {datatype}
    - Sample data: {sample}
    2. The output must be a Pandas DataFrame named `output_df`. If no relevant columns match the question or not have converstaion related to that query. 
    3. Use explicit imports for all necessary libraries (e.g., `import pandas as pd`) to prevent errors.
    4. Do not create or assume sample data, alter the DataFrame, or include any functionality beyond answering the question.
    5. Include concise comments in your code for clarity.
    6. Use .contains() and .lower() function for finding string always rather than ==.
    7. Date is in DD-MM-YYYY.

    ### Key Points:
    - Do not produce a sample data or dataframe
    - Avoid Recursion 
    - Output only the Python code; no explanations, text, or examples.

    - No Need to write functions.
    - No need to write comments.
    - always use reset_index() and try to provide name columns with metrics for better understanding.






    Examples: (Use Code reference if sample question is matching.)

        Sample Question: {sample_question},

        Code: {sample_code}

    # Your code starts below:
    """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["question", "df", "datatype", "sample", "sample_code","sample_question","conversation_history"],
        )

        prompt_str = {
            "question": question,
            "df": df.columns,
            "datatype": list1,
            "sample": df.head(1),
            "sample_code": sample_code['Code'],
            "sample_question":sample_code['question'],
            "conversation_history":format_history(history)
        }

        chain = prompt | llm
        generated_code = await asyncio.wait_for(
                chain.ainvoke(prompt_str),
                timeout=60,
            )
            
        return generated_code.content
    except Exception as e:
        print(e)
        return None