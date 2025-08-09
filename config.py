"""
Configuration file for the Client Health Assessment Chatbot
"""

import os
from typing import Dict, List

# API Configuration
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3

# Campaign Health Assessment Categories
HEALTH_CATEGORIES = {
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

# Input validation rules
VALIDATION_RULES = {
    "company_name": {
        "required": True,
        "min_length": 1,
        "max_length": 100
    },
    "monthly_budget": {
        "required": True,
        "min_value": 0,
        "max_value": 10000000  # $10M max budget
    },
    "campaign_duration": {
        "required": True,
        "min_value": 1,
        "max_value": 60  # 5 years max
    },
    "text_fields": {
        "max_length": 3000,
        "min_required_fields": 2  # At least two text fields must have content
    }
}

# Sample clients for testing
SAMPLE_CLIENTS = [
    {
        "company_name": "TechCorp Solutions",
        "account_manager": "Sarah Johnson",
        "monthly_budget": 50000,
        "campaign_duration_months": 6,
        "campaign_objectives": "Brand awareness and lead generation for new product launch",
        "current_performance_metrics": "CTR: 2.3%, CPA: $45, ROAS: 3.2x",
        "budget_utilization": "85% spend rate, on track for monthly goals",
        "client_reported_notes": "Happy with performance, seeing good quality leads",
        "recent_changes_or_concerns": "No major concerns, interested in expanding to new markets"
    },
    {
        "company_name": "RetailPlus Inc",
        "account_manager": "Mike Chen",
        "monthly_budget": 25000,
        "campaign_duration_months": 3,
        "campaign_objectives": "Drive holiday sales and increase market share",
        "current_performance_metrics": "CTR: 1.1%, CPA: $78, ROAS: 1.8x",
        "budget_utilization": "95% spend, burning through budget quickly",
        "client_reported_notes": "Concerned about high costs, not seeing expected ROI",
        "recent_changes_or_concerns": "Considering pausing campaign, competitor pressure increasing"
    }
]

# Security settings
SECURITY_SETTINGS = {
    "max_requests_per_minute": 10,
    "data_retention_hours": 0,  # Don't store data
    "log_client_data": False
}

# Trace settings
TRACE_SETTINGS = {
    "enabled": True,
    "traces_directory": "traces",
    "max_trace_age_days": 30,  # Keep traces for 30 days
    "max_traces_per_session": 1000,  # Limit events per session
    "auto_cleanup": True,  # Automatically clean up old traces
    "export_formats": ["json"],
    "include_sensitive_data": False,  # Don't trace sensitive client data by default
    "trace_errors": True,
    "trace_performance": True
}

def get_api_key() -> str:
    """Get API key from environment variables"""
    return os.getenv("OPENAI_API_KEY", "")

def validate_client_info(company_name: str, monthly_budget: float, campaign_duration: int, text_fields: Dict[str, str]) -> List[str]:
    """Validate advertising client information and return list of errors"""
    errors = []
    
    # Validate company name
    if not company_name or len(company_name.strip()) < VALIDATION_RULES["company_name"]["min_length"]:
        errors.append("Company name is required")
    elif len(company_name) > VALIDATION_RULES["company_name"]["max_length"]:
        errors.append(f"Company name must be less than {VALIDATION_RULES['company_name']['max_length']} characters")
    
    # Validate monthly budget
    if monthly_budget < VALIDATION_RULES["monthly_budget"]["min_value"] or monthly_budget > VALIDATION_RULES["monthly_budget"]["max_value"]:
        errors.append(f"Monthly budget must be between ${VALIDATION_RULES['monthly_budget']['min_value']:,} and ${VALIDATION_RULES['monthly_budget']['max_value']:,}")
    
    # Validate campaign duration
    if campaign_duration < VALIDATION_RULES["campaign_duration"]["min_value"] or campaign_duration > VALIDATION_RULES["campaign_duration"]["max_value"]:
        errors.append(f"Campaign duration must be between {VALIDATION_RULES['campaign_duration']['min_value']} and {VALIDATION_RULES['campaign_duration']['max_value']} months")
    
    # Validate text fields
    non_empty_fields = sum(1 for field in text_fields.values() if field.strip())
    if non_empty_fields < VALIDATION_RULES["text_fields"]["min_required_fields"]:
        errors.append("Please provide at least campaign objectives and performance metrics or client notes")
    
    # Check field lengths
    for field_name, field_value in text_fields.items():
        if len(field_value) > VALIDATION_RULES["text_fields"]["max_length"]:
            errors.append(f"{field_name.replace('_', ' ').title()} must be less than {VALIDATION_RULES['text_fields']['max_length']} characters")
    
    return errors