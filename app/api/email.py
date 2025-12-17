from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import json, logging
from core.function import append_to_excel
import random
router = APIRouter()
logger = logging.getLogger(__name__)

llm_chat = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm_chat, memory=memory)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(request_data: ChatRequest):
    try:
        # 🔹 Prompting AI to return JSON
        prompt_with_subject = (
            f"{request_data.message}\n\n"
            "Without any additional text output should be in the json format."
            "Write a little professional mail"
            "Do not provide any date in the email unless described in the message."
            "Please return a final valid JSON response with the following format:\n"

            "{\n"
            '  "email": {\n'
            '    "email_subject": "Your generated email subject",\n'
            '    "email_body": "Your generated email body"\n'
            "  }\n"
            "}"
        )


        response = conversation.predict(input=prompt_with_subject)

        response = response.strip().strip("```").replace("json\n", "").replace("```json", "").strip()


        try:
            response_json = json.loads(response)
            if "email" in response_json and "email_subject" in response_json["email"]:
                return response_json  # ✅ Return clean JSON
            else:
                raise ValueError("Missing required keys in JSON response")

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="AI returned an invalid JSON format. Check logs for details.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI returned an invalid JSON format. Check logs for details.")

    finally:
        prompt=    random.randint(700, 2000)
        output=     random.randint(700, 2000)
#        await append_to_excel("MAIL","Generate a email",request_data.message,    
#    (prompt + output),
#    prompt,
#    output,
#0,
#response
#)
