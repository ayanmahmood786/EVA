from langchain_google_genai import ChatGoogleGenerativeAI
from fuzzywuzzy import fuzz
from langchain_core.prompts import PromptTemplate
import json
import os

os.environ['GOOGLE_API_KEY']=os.getenv('GOOGLE_API_KEY')


def get_best_match(input_text, list_commands):
    matches = []
    for name in list_commands:
        similarity_score = fuzz.ratio(name.lower(), input_text.lower())
        if similarity_score >= 60:
            matches.append((name, similarity_score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

# Step 2: Intent prediction using LLM
def predict_intent(text, list_commands1):  
    model= ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.75)

    best_matches = get_best_match(text, list_commands1)
    prompt = """
    Based on the given text: {text}
    Your task is to find the best matching command from the following list: {list_commands1}

    You need to:
    1. Identify the best matching command from the list.
    2. Verify the best match further.
    3. Return the response in the specified JSON format and only the name.

    If no suitable command is found, return None or an empty string.
    Dont provide any additional text.
    Final Response Should be a JSON:
    {{
        "Intent": ""
    }}
    """
    temp = PromptTemplate(template=prompt, input_variables=["text", "list_commands1"])
    prompt_format = temp.format(text=text, list_commands1=best_matches)
    response = model.predict(prompt_format)
    response = response.replace("```json", "").replace("```", "")
    return json.loads(response)
