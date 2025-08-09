"""
FastAPI backend for Client Health Chatbot
Similar structure to recipe-chatbot with support for client campaign analysis
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import litellm
from pydantic import BaseModel, Field

from .models import ClientAnalysisRequest, ClientAnalysisResponse, ConversationResponse
from .client_evaluator import ClientEvaluator
from .trace_manager import TraceManager
from .config import get_settings

# Global variables
trace_manager = None
client_evaluator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global trace_manager, client_evaluator
    
    settings = get_settings()
    
    # Initialize components
    trace_manager = TraceManager(settings.traces_directory)
    client_evaluator = ClientEvaluator(settings)
    
    # Configure LiteLLM
    if settings.model_name:
        litellm.model = settings.model_name
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
        
    print(f"🚀 Client Health Chatbot started with model: {settings.model_name}")
    
    yield
    
    # Cleanup
    if trace_manager:
        trace_manager.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Client Health Chatbot",
    description="AI-powered advertising campaign health analyzer",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main frontend page"""
    try:
        with open("frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Frontend not found</h1><p>Please ensure the frontend directory exists.</p>",
            status_code=404
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/analyze", response_model=ClientAnalysisResponse)
def analyze_client(request: ClientAnalysisRequest):
    """Analyze client campaign health"""
    global client_evaluator, trace_manager
    
    if not client_evaluator:
        raise HTTPException(status_code=500, detail="Client evaluator not initialized")
    
    try:
        # Create conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Trace user request if enabled
        if trace_manager and get_settings().trace_enabled:
            trace_manager.trace_user_request(
                conversation_id=conversation_id,
                company_name=request.company_name,
                client_info=request.dict()
            )
        
        # Perform analysis
        start_time = datetime.utcnow()
        evaluation = client_evaluator.evaluate_client(request)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create response
        response = ClientAnalysisResponse(
            conversation_id=conversation_id,
            category=evaluation.get("category", "might_need_attention"),
            confidence=int(evaluation.get("confidence", 50)),
            reasoning=evaluation.get("reasoning", "Analysis completed"),
            recommendations=evaluation.get("recommendations", []),
            risk_factors=evaluation.get("risk_factors", []),
            positive_indicators=evaluation.get("positive_indicators", []),
            budget_assessment=evaluation.get("budget_assessment", ""),
            performance_assessment=evaluation.get("performance_assessment", ""),
            client_satisfaction=evaluation.get("client_satisfaction", ""),
            processing_time=processing_time
        )
        
        # Trace bot response if enabled
        if trace_manager and get_settings().trace_enabled:
            trace_manager.trace_bot_response(
                conversation_id=conversation_id,
                evaluation_result=evaluation,
                processing_time=processing_time
            )
        
        return response
        
    except Exception as e:
        # Trace error if enabled
        if trace_manager and get_settings().trace_enabled:
            trace_manager.trace_error(
                conversation_id=conversation_id,
                error_message=str(e),
                error_type="analysis_error",
                context={"company_name": request.company_name}
            )
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/conversations", response_model=List[ConversationResponse])
async def get_conversations():
    """Get list of all conversations"""
    global trace_manager
    
    if not trace_manager or not get_settings().trace_enabled:
        return []
    
    try:
        conversations = trace_manager.list_all_conversations()
        return [
            ConversationResponse(
                conversation_id=conv["conversation_id"],
                timestamp=conv["timestamp"],
                company_name=conv.get("company_name", "Unknown"),
                category=conv.get("category", "unknown"),
                confidence=conv.get("confidence", 0)
            )
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get detailed conversation trace"""
    global trace_manager
    
    if not trace_manager or not get_settings().trace_enabled:
        raise HTTPException(status_code=404, detail="Tracing not enabled")
    
    try:
        conversation = trace_manager.get_conversation_details(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation trace"""
    global trace_manager
    
    if not trace_manager or not get_settings().trace_enabled:
        raise HTTPException(status_code=404, detail="Tracing not enabled")
    
    try:
        success = trace_manager.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    settings = get_settings()
    return {
        "model_name": settings.model_name,
        "trace_enabled": settings.trace_enabled,
        "health_categories": settings.health_categories
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
