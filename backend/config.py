"""
Configuration management for Client Health Chatbot
"""

import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    model_name: str = "gpt-3.5-turbo"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.3
    
    # Tracing Configuration
    trace_enabled: bool = True
    traces_directory: str = "traces"
    max_trace_age_days: int = 30
    include_sensitive_data: bool = False
    
    # Health Categories
    health_categories: Dict[str, Dict[str, str]] = {
        "healthy": {
            "name": "Campaign Healthy",
            "icon": "🟢",
            "description": "Campaign is performing well, budget on track, client satisfied"
        },
        "might_need_attention": {
            "name": "Monitoring Needed",
            "icon": "🟡",
            "description": "Campaign shows some indicators that warrant closer monitoring or optimization"
        },
        "need_attention_positive": {
            "name": "Action Needed - Growth Opportunity",
            "icon": "🟠",
            "description": "Campaign needs attention but shows positive indicators for scaling or expansion"
        },
        "need_attention_negative": {
            "name": "Action Needed - Risk Management",
            "icon": "🔴",
            "description": "Campaign requires immediate attention due to budget, performance, or client satisfaction concerns"
        }
    }
    
    # Validation Rules
    validation_rules: Dict[str, Any] = {
        "company_name": {
            "required": True,
            "min_length": 1,
            "max_length": 100
        },
        "monthly_budget": {
            "required": True,
            "min_value": 0,
            "max_value": 10000000
        },
        "campaign_duration": {
            "required": True,
            "min_value": 1,
            "max_value": 60
        },
        "text_fields": {
            "max_length": 3000,
            "min_required_fields": 2
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

def validate_client_info(data: Dict[str, Any]) -> list[str]:
    """Validate client information and return list of errors"""
    errors = []
    settings = get_settings()
    rules = settings.validation_rules
    
    # Validate company name
    company_name = data.get("company_name", "")
    if not company_name or len(company_name.strip()) < rules["company_name"]["min_length"]:
        errors.append("Company name is required")
    elif len(company_name) > rules["company_name"]["max_length"]:
        errors.append(f"Company name must be less than {rules['company_name']['max_length']} characters")
    
    # Validate monthly budget
    monthly_budget = data.get("monthly_budget", 0)
    if monthly_budget < rules["monthly_budget"]["min_value"] or monthly_budget > rules["monthly_budget"]["max_value"]:
        errors.append(f"Monthly budget must be between ${rules['monthly_budget']['min_value']:,} and ${rules['monthly_budget']['max_value']:,}")
    
    # Validate campaign duration
    campaign_duration = data.get("campaign_duration_months", 0)
    if campaign_duration < rules["campaign_duration"]["min_value"] or campaign_duration > rules["campaign_duration"]["max_value"]:
        errors.append(f"Campaign duration must be between {rules['campaign_duration']['min_value']} and {rules['campaign_duration']['max_value']} months")
    
    # Validate text fields
    text_fields = {
        "campaign_objectives": data.get("campaign_objectives", ""),
        "current_performance_metrics": data.get("current_performance_metrics", ""),
        "budget_utilization": data.get("budget_utilization", ""),
        "client_reported_notes": data.get("client_reported_notes", ""),
        "recent_changes_or_concerns": data.get("recent_changes_or_concerns", "")
    }
    
    non_empty_fields = sum(1 for field in text_fields.values() if field.strip())
    if non_empty_fields < rules["text_fields"]["min_required_fields"]:
        errors.append("Please provide at least campaign objectives and performance metrics or client notes")
    
    # Check field lengths
    for field_name, field_value in text_fields.items():
        if len(field_value) > rules["text_fields"]["max_length"]:
            errors.append(f"{field_name.replace('_', ' ').title()} must be less than {rules['text_fields']['max_length']} characters")
    
    return errors
