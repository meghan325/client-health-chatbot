"""
Client Campaign Evaluator using LiteLLM for multi-provider support
"""

import json
import re
import time
from typing import Dict, Any
import litellm
from .models import ClientAnalysisRequest
from .config import Settings

class ClientEvaluator:
    """Main class for evaluating advertising campaign health status"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.health_categories = settings.health_categories
    
    def create_evaluation_prompt(self, client_info: ClientAnalysisRequest) -> str:
        """Create a structured prompt for LLM evaluation of advertising campaigns"""
        prompt = f"""
You are an AdTech campaign analysis AI assistant. Please analyze the following advertising client's campaign information and provide a campaign health evaluation.

Campaign Information:
- Company Name: {client_info.company_name}
- Account Manager: {client_info.account_manager}
- Monthly Budget: ${client_info.monthly_budget:,.2f}
- Campaign Duration: {client_info.campaign_duration_months} months
- Campaign Objectives: {client_info.campaign_objectives}
- Current Performance Metrics: {client_info.current_performance_metrics}
- Budget Utilization: {client_info.budget_utilization}
- Client Reported Notes: {client_info.client_reported_notes}
- Recent Changes/Concerns: {client_info.recent_changes_or_concerns}

Please evaluate this advertising campaign and categorize it into one of these four categories:

1. "healthy" - Campaign is performing well, budget on track, client satisfied
2. "might_need_attention" - Campaign shows indicators that warrant closer monitoring or optimization
3. "need_attention_positive" - Campaign needs attention but shows positive indicators for scaling or expansion
4. "need_attention_negative" - Campaign requires immediate attention due to budget, performance, or client satisfaction concerns

Consider these key factors in your analysis:
- Budget efficiency and utilization
- Performance metrics (CTR, CPA, ROAS, etc.)
- Client satisfaction and feedback
- Campaign objectives alignment
- Market conditions and competitive factors
- Account management relationship

Provide your response in the following JSON format:
{{
    "category": "one of the four categories above",
    "confidence": "percentage (0-100)",
    "reasoning": "detailed explanation of your campaign assessment",
    "recommendations": ["specific", "actionable", "campaign", "recommendations"],
    "risk_factors": ["identified", "campaign", "risk", "factors"],
    "positive_indicators": ["campaign", "strengths", "and", "opportunities"],
    "budget_assessment": "analysis of budget efficiency and utilization",
    "performance_assessment": "evaluation of key performance metrics",
    "client_satisfaction": "assessment of client relationship and satisfaction"
}}

IMPORTANT: Base your assessment on advertising campaign best practices and the provided information. Focus on campaign performance, budget efficiency, and client satisfaction.
"""
        return prompt
    
    def evaluate_client(self, client_info: ClientAnalysisRequest) -> Dict[str, Any]:
        """Send client information to LLM for evaluation"""
        start_time = time.time()
        
        try:
            prompt = self.create_evaluation_prompt(client_info)
            
            # Use litellm for multi-provider support
            response = litellm.completion(
                model=self.settings.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert AdTech campaign analyst. Provide structured, professional campaign health evaluations based on advertising performance data, budget utilization, and client feedback."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                evaluation = {
                    "category": "might_need_attention",
                    "confidence": "50",
                    "reasoning": content,
                    "recommendations": ["Please review campaign data and consult with account management team"],
                    "risk_factors": ["Unable to parse detailed assessment"],
                    "positive_indicators": [],
                    "budget_assessment": "Analysis incomplete",
                    "performance_assessment": "Analysis incomplete", 
                    "client_satisfaction": "Analysis incomplete"
                }
            
            # Ensure confidence is a number
            if isinstance(evaluation.get("confidence"), str):
                try:
                    evaluation["confidence"] = int(evaluation["confidence"])
                except (ValueError, TypeError):
                    evaluation["confidence"] = 50
            
            # Validate category
            valid_categories = list(self.health_categories.keys())
            if evaluation.get("category") not in valid_categories:
                evaluation["category"] = "might_need_attention"
            
            return evaluation
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Error occurred during evaluation: {str(e)}"
            
            # Return error evaluation
            return {
                "category": "might_need_attention",
                "confidence": 0,
                "reasoning": error_message,
                "recommendations": ["Please try again or consult with account management team"],
                "risk_factors": ["System error"],
                "positive_indicators": [],
                "budget_assessment": "Analysis failed",
                "performance_assessment": "Analysis failed",
                "client_satisfaction": "Analysis failed"
            }
