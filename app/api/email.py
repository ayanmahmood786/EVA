from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import json, logging

router = APIRouter()
logger = logging.getLogger(__name__)

llm_chat = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm_chat, memory=memory)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        prompt = (
            f"{request.message}\n\nReturn a JSON email with 'email_subject' and 'email_body'."
        )
        response = conversation.predict(input=prompt)
        response = response.strip().replace("```json", "").replace("```", "")
        return json.loads(response)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Invalid JSON response from LLM")
