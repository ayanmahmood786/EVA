from time import time  # Import the time module correctly
import os
import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
import logging
<<<<<<< HEAD
=======
from core.function import append_to_excel
>>>>>>> ayan2

# API Key Configuration
os.environ['API_KEY'] = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=os.environ["API_KEY"])

# Logging Configuration
logging.basicConfig(filename="logs/auto_prompt.log", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model
model = genai.GenerativeModel("gemini-2.0-flash", generation_config={"temperature": 0.80})

# Global variables
total_tokens = None
output_tokens =None
prompt_tokens=None
elapsed_time = None  # Renaming 'times' to 'elapsed_time' to avoid conflict

<<<<<<< HEAD
def suggestions(question, previous_question):
=======
async def suggestions(question, previous_question):
>>>>>>> ayan2
    global total_tokens,output_tokens,prompt_tokens
    global elapsed_time  # Using 'elapsed_time' instead of 'times'
    

    prompt="""
    Previous Conversation Question CONTEXT (if relevant): {previous_question}.
    If the user question is not relevant to the context just answer the user question and not provide any additional details.
    And if user asks for any alternative supplier provide the details.
    **Objective**:
    - Provide a clear, data-focused answer to the question: "{question}", focusing on insights that support strategic decision-making.

    **Answer Requirements**:
    1. **Tone & Audience**:
    - Write in a professional tone, presenting insights with clarity and precision.
    - Tailor insights for a business audience, focusing on strategic implications.

    2. **Key Insights**:
    - **Structure**: Use bullet points to present each main insight clearly.
    - While Providing Numbers use "billions","millions" etc.
    - **Patterns & Comparisons**: Identify and describe notable trends or patterns (e.g., "highest sales month," "year-over-year increase of X%","any relevant ratio","Financial Impact","Operational Efficiency","Predictive Analysis","Benchmarking","Variance Analysis").
    - **Actionable Recommendations**: Offer recommendations that can guide business actions based on identified trends and data patterns.
    - **Technical Analysis**(If Relevant): Based on the provided data give some numerical analysis like average, total etc. Provide exact figures.

    3. **Follow-Up Exploration**:
    - Create 3 follow-up questions having 12-15 words related to the user current question: {question} and answer.
    - Do not write the follow up in answer.
    **Final Output Format**:
    Provide the answer in JSON format, as shown below:
    Avoid this error while writing the response: Error Encounted In API:Invalid \escape: line 3 column 332 (char 334)
    {{
    "Answer_to_user_question": "<Detailed answer>",
    "Auto_prompt": {{
        "Question_1": "Follow-up question similar type of user question based on the data",
        "Question_2": "Another question exploring a different expect based on the data",
        "Question_3": "Final question exploring new idea based on the data."
    }}
    }}
    """

    try:
        # Format the prompt with input variables
        prompt = PromptTemplate(template=prompt, input_variables=["question", "previous_question"])
        prompt_formatted_str = prompt.format(question=question, previous_question=previous_question)

        # Start timing
        start_time = time()  # Correct usage of time.time()

        # Generate content from the model
        prediction = model.generate_content(prompt_formatted_str)

        # End timing
        end_time = time()

        # Store token and elapsed time
        total_tokens = prediction.usage_metadata.total_token_count
        output_tokens=prediction.usage_metadata.prompt_token_count
        prompt_tokens=prediction.usage_metadata.candidates_token_count
        elapsed_time = round(end_time - start_time, 2)


        # Log the output and information
        logger.info(f"Predicted text: {prediction.text}")
        logger.info(f"Tokens Used: {prediction.usage_metadata}")
        logger.info(f"Time Taken For Response: {elapsed_time} secs")

        return prediction.text

    except ValueError as e:
        logger.error(f"Error parsing JSON: {e}")
        print(status_code=500, detail="Error generating response from AI")
<<<<<<< HEAD

=======
    finally:
        await append_to_excel("Autoprompt",question,prompt_formatted_str,total_tokens,prompt_tokens,output_tokens,0,"llm_results.xlsx",prediction.text)
>>>>>>> ayan2

