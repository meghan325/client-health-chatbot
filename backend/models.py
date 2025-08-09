"""
Pydantic models for API requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ClientAnalysisRequest(BaseModel):
    """Request model for client campaign analysis"""
    company_name: str = Field(..., min_length=1, max_length=100, description="Company name")
    account_manager: str = Field(..., description="Account manager name")
    monthly_budget: float = Field(..., ge=0, le=10000000, description="Monthly budget in USD")
    campaign_duration_months: int = Field(..., ge=1, le=60, description="Campaign duration in months")
    campaign_objectives: str = Field(..., description="Campaign objectives and goals")
    current_performance_metrics: str = Field(..., description="Current performance metrics (CTR, CPA, ROAS, etc.)")
    budget_utilization: str = Field(..., description="Budget utilization information")
    client_reported_notes: str = Field(..., description="Client feedback and notes")
    recent_changes_or_concerns: str = Field(..., description="Recent changes or concerns")

class ClientAnalysisResponse(BaseModel):
    """Response model for client campaign analysis"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    category: str = Field(..., description="Health category classification")
    confidence: int = Field(..., ge=0, le=100, description="Confidence percentage")
    reasoning: str = Field(..., description="Detailed analysis reasoning")
    recommendations: List[str] = Field(default=[], description="Action recommendations")
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    positive_indicators: List[str] = Field(default=[], description="Positive indicators and opportunities")
    budget_assessment: str = Field(default="", description="Budget efficiency analysis")
    performance_assessment: str = Field(default="", description="Performance metrics evaluation")
    client_satisfaction: str = Field(default="", description="Client relationship assessment")
    processing_time: float = Field(..., description="Processing time in seconds")

class ConversationResponse(BaseModel):
    """Response model for conversation list"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    timestamp: str = Field(..., description="Conversation timestamp")
    company_name: str = Field(..., description="Company name analyzed")
    category: str = Field(..., description="Assigned health category")
    confidence: int = Field(..., description="Analysis confidence")

class HealthCategory(BaseModel):
    """Model for health category definition"""
    name: str = Field(..., description="Category display name")
    icon: str = Field(..., description="Category icon")
    description: str = Field(..., description="Category description")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
