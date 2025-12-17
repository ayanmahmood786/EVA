from fastapi import FastAPI,WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from api import (apex_report_route,autoprompt_route,email,excel_route,flexi_report,flexisuggestion_route,getbiinsight_route,graphroute,pdfroute,rag_routes,voicefilter_route)
import os
from core.config import GOOGLE_API_KEY
from core.function import clean_old_logs
import asyncio
from contextlib import asynccontextmanager

os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App starting up... running log cleanup")
    clean_old_logs()  # ✅ run your cleanup on startup
    yield  # app runs here
    print("🛑 App shutting down...")



app = FastAPI(title="EVA AI Backend",lifespan=lifespan)
app.add_middleware(GZipMiddleware)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(rag_routes.router, prefix="/api", tags=["RAG"])
app.include_router(pdfroute.router, prefix="/api", tags=["PDF"])
app.include_router(apex_report_route.router, prefix="/api", tags=["Apex Report"])
app.include_router(autoprompt_route.router, prefix="/api", tags=["AutoPrompt"])
app.include_router(email.router, prefix="/api", tags=["Email"])
app.include_router(excel_route.router, prefix="/api", tags=["Excel"])
app.include_router(flexi_report.router, prefix="/api", tags=["Flexi Suggestions"])
app.include_router(flexisuggestion_route.router, prefix="/api", tags=["Flexi Insight"])
app.include_router(getbiinsight_route.router, prefix="/api", tags=["Bi Insight"])
app.include_router(graphroute.router, prefix="/api", tags=["Graph"])
app.include_router(voicefilter_route.router, prefix="/api", tags=["Voice Filter"])
@app.get("/health")
async def health_check():
    return {"status": "Service is up"}




LOG_PATH = "logs/app.log"




    

@app.websocket("/api/ws/logs")
async def websocket_logs(ws: WebSocket, last_lines: int = 50):
    await ws.accept()
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[-last_lines:]:
            await ws.send_text(line)
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                await ws.send_text(line)
            else:
                await asyncio.sleep(1)



# 23/10/25 -Ayan Mahmood
# Restructuring

import pandas as pd
from datetime import datetime
@app.get("/api/cost")
async def costing():
    try:
        df = pd.read_excel("llm_results.xlsx")
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        today = datetime.now().date()
        today_df = df[df['Date'] == today]

        if today_df.empty:
            return {"message": "No records found for today"}

        return {
            "Date": str(today),
            "Previous Cost":float(df["Total Cost (USD)"].sum()),
            "Previous Total Tokens":float(df["Total Tokens"].sum()- today_df["Total Tokens"].sum()),
            "Total Cost (USD) For Today":float( today_df["Total Cost (USD)"].sum()),
            "Total Tokens": float(today_df["Total Tokens"].sum()),
            "No of Requests": len(today_df),
            "Overall":float(df["Total Tokens"].sum()),
            "Total Request": len(df)
        }
    except Exception as e:
        return {"Error":e}

@app.get("/api/download-excel")
async def download_excel():
    """
    Endpoint to download the Excel file (llm_results.xlsx)
    """
    file_path = "llm_results.xlsx"

    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "status_code":404,
            "content":{"error": "File not found. Please ensure llm_results.xlsx exists."}
        }

    # Use FileResponse for direct download
    return FileResponse(
        path=file_path,
        filename="llm_results.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
