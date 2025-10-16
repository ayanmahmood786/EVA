from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from api import (apex_report_route,autoprompt_route,email,excel_route,flexi_report,flexisuggestion_route,getbiinsight_route,graphroute,pdfroute,rag_routes,voicefilter_route)
import os
from core.config import GOOGLE_API_KEY


os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY






app = FastAPI(title="EVA AI Backend")
app.add_middleware(GZipMiddleware)

# ✅ CORS
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
