from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from core.config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, EBIZ_USER, EBIZ_PASSWORD

# Pydantic
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Python standard libraries
import os
import shutil
import logging
import time
import json
import re
from datetime import datetime
import asyncio
import uuid
import warnings

# Data & ML
import pandas as pd
from io import BytesIO
from fuzzywuzzy import process
from rapidfuzz import fuzz
from fastapi import APIRouter, HTTPException, Request, Form, BackgroundTasks
# Oracle DB
import oracledb
from langchain_community.callbacks import get_openai_callback
# Langchain / AI
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings import HuggingFaceEmbeddings

# Tenacity for retries
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log, after_log
from core.config import GOOGLE_API_KEY


os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY



async def create_connection_ebizai():
    connection=oracledb.connect(user=EBIZ_USER,password=EBIZ_PASSWORD,dsn=ORACLE_DSN)
    return connection  
    
try:
  llm=GoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0.5)
  llm_chat=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0.5)
  connection=oracledb.connect(user=ORACLE_USER,password=ORACLE_PASSWORD,dsn=ORACLE_DSN)
  connection_voice=oracledb.connect(user=ORACLE_USER,password=ORACLE_PASSWORD,dsn=ORACLE_DSN)
  embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
  

    

except Exception as e:
  print(e)