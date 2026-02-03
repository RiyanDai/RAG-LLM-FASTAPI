# api.py - REST API untuk HRIS Chatbot

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict

load_dotenv()

from rag_system import HRISRagSystem

app = FastAPI(
    title="HRIS Chatbot API",
    description="API untuk konsumsi HRIS Chatbot dari Flutter",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG system (shared knowledge base)
_rag_system = None

def get_rag_system() -> HRISRagSystem:
    """Get or create RAG system"""
    global _rag_system
    
    if _rag_system is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY tidak dikonfigurasi di server",
            )
        
        print("Creating new RAG system...")
        _rag_system = HRISRagSystem(groq_api_key=groq_api_key)
    
    return _rag_system


# --- Request/Response Models ---

class ChatRequest(BaseModel):
    """Request body untuk endpoint chat"""
    message: str = Field(..., min_length=1, description="Pertanyaan user ke HR assistant")
    user_data: Dict = Field(..., description="User data dari Flutter Hive storage")


class ChatResponse(BaseModel):
    """Response dari endpoint chat"""
    success: bool = True
    message: str = Field(..., description="Jawaban dari HR assistant")
    query: str = Field(..., description="Pertanyaan yang dikirim (echo)")


class HealthResponse(BaseModel):
    """Response health check"""
    status: str = "ok"
    service: str = "hris-chatbot-api"


# --- Endpoints ---

@app.get("/", tags=["Root"])
async def root():
    """Info API"""
    return {
        "service": "HRIS Chatbot API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "chat": "POST /chat",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check untuk load balancer / monitoring"""
    return HealthResponse()


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Kirim pertanyaan ke HR assistant (RAG) dengan USER CONTEXT
    
    Body:
    - message: Pertanyaan dalam teks (wajib, minimal 1 karakter)
    - user_data: Data user dari Flutter Hive (wajib)
    
    Response: 
    - Jawaban dari AI berdasarkan:
      1. Data personal user (dari Flutter Hive)
      2. Knowledge base HRIS (dari RAG)
    
    Contoh:
    POST /chat
    Body: {
      "message": "Berapa kali saya terlambat bulan ini?",
      "user_data": {
        "nama": "John Doe",
        "nik": "123456",
        "jabatan": "Software Engineer",
        "departemen": "IT",
        "bagian": "Development",
        "sisa_cuti": "12",
        "periode_mulai_cuti": "2024-01-01",
        "periode_akhir_cuti": "2024-12-31",
        "attendance": {
          "bulan": "02",
          "tahun": "2026",
          "jumlah_hadir": "20",
          "terlambat": "2",
          ...
        }
      }
    }
    
    Response:
    {
      "success": true,
      "message": "Berdasarkan data absensi Anda di periode 02/2026, Anda terlambat 2 kali.",
      "query": "Berapa kali saya terlambat bulan ini?"
    }
    """
    try:
        # Get RAG system
        rag = get_rag_system()
        
        # Set user data dari request
        rag.set_user_data(request.user_data)
        
        # Process chat
        response_text = rag.chat(request.message.strip())
        
        return ChatResponse(
            success=True,
            message=response_text,
            query=request.message,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error memproses chat: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )