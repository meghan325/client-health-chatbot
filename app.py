import os
import streamlit as st
import openai
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import re
from datetime import datetime
import config

# Configuration
openai.api_key = config.get_api_key()

@dataclass
class ClientInfo:
    """Data class to structure advertising client campaign information"""
    company_name: str
    account_manager: str
    monthly_budget: float
    campaign_duration_months: int
    campaign_objectives: str
    current_performance_metrics: str
    budget_utilization: str
    client_reported_notes: str
    recent_changes_or_concerns: str

class CampaignEvaluator:
    """Main class for evaluating advertising campaign health status"""
    
    def __init__(self):
        self.evaluation_categories = config.HEALTH_CATEGORIES
    
    def create_evaluation_prompt(self, client_info: ClientInfo) -> str:
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
    
    def evaluate_client(self, client_info: ClientInfo) -> Dict:
        """Send client information to LLM for evaluation"""
        try:
            prompt = self.create_evaluation_prompt(client_info)
            
            response = openai.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert AdTech campaign analyst. Provide structured, professional campaign health evaluations based on advertising performance data, budget utilization, and client feedback."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.OPENAI_MAX_TOKENS,
                temperature=config.OPENAI_TEMPERATURE
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                return evaluation
            else:
                # Fallback if JSON parsing fails
                return {
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
                
        except Exception as e:
            st.error(f"Error during evaluation: {str(e)}")
            return {
                "category": "might_need_attention",
                "confidence": "0",
                "reasoning": f"Error occurred during evaluation: {str(e)}",
                "recommendations": ["Please try again or consult with account management team"],
                "risk_factors": ["System error"],
                "positive_indicators": [],
                "budget_assessment": "Analysis failed",
                "performance_assessment": "Analysis failed",
                "client_satisfaction": "Analysis failed"
            }

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AdTech Campaign Health Analyzer",
        page_icon="📺",
        layout="wide"
    )
    
    st.title("📺 AdTech Campaign Health Analyzer")
    st.markdown("---")
    
    # API Key input
    if not config.get_api_key():
        st.warning("Please set your OpenAI API key as an environment variable or enter it below:")
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            openai.api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            st.stop()
    
    st.sidebar.header("ℹ️ About")
    st.sidebar.info(
        "This analyzer evaluates TV advertising campaign health and provides assessments in four categories:\n\n"
        "• **🟢 Campaign Healthy**: Performing well, on track\n"
        "• **🟡 Monitoring Needed**: Optimization opportunities\n"
        "• **🟠 Growth Opportunity**: Positive indicators for scaling\n"
        "• **🔴 Risk Management**: Immediate attention required\n\n"
        "📊 **Analysis includes**: Budget efficiency, performance metrics, client satisfaction, and campaign objectives alignment."
    )
    
    # Create two columns for input and results
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📊 Campaign Information")
        
        # Input form
        with st.form("campaign_info_form"):
            company_name = st.text_input("Company Name", placeholder="Enter advertiser company name")
            account_manager = st.text_input("Account Manager", placeholder="Enter account manager name")
            
            col_budget, col_duration = st.columns(2)
            with col_budget:
                monthly_budget = st.number_input("Monthly Budget ($)", min_value=0.0, max_value=10000000.0, value=50000.0, format="%.2f")
            with col_duration:
                campaign_duration = st.number_input("Campaign Duration (months)", min_value=1, max_value=60, value=6)
            
            campaign_objectives = st.text_area(
                "Campaign Objectives",
                placeholder="What are the main goals of this TV advertising campaign?",
                height=100
            )
            
            current_performance = st.text_area(
                "Current Performance Metrics",
                placeholder="CTR, CPA, ROAS, impressions, conversions, etc...",
                height=100
            )
            
            budget_utilization = st.text_area(
                "Budget Utilization",
                placeholder="Spend rate, pacing, remaining budget, etc...",
                height=80
            )
            
            client_notes = st.text_area(
                "Client Reported Notes",
                placeholder="Client feedback, satisfaction, concerns, requests...",
                height=100
            )
            
            recent_changes = st.text_area(
                "Recent Changes or Concerns",
                placeholder="Any recent changes in strategy, market conditions, or client concerns...",
                height=80
            )
            
            submit_button = st.form_submit_button("📈 Analyze Campaign Health", use_container_width=True)
    
    with col2:
        st.header("📈 Campaign Health Assessment")
        
        if submit_button:
            # Validate input using config validation
            text_fields = {
                "campaign_objectives": campaign_objectives,
                "current_performance_metrics": current_performance,
                "budget_utilization": budget_utilization,
                "client_reported_notes": client_notes,
                "recent_changes_or_concerns": recent_changes
            }
            
            validation_errors = config.validate_client_info(company_name, monthly_budget, campaign_duration, text_fields)
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # Create client info object
                client_info = ClientInfo(
                    company_name=company_name,
                    account_manager=account_manager,
                    monthly_budget=monthly_budget,
                    campaign_duration_months=campaign_duration,
                    campaign_objectives=campaign_objectives,
                    current_performance_metrics=current_performance,
                    budget_utilization=budget_utilization,
                    client_reported_notes=client_notes,
                    recent_changes_or_concerns=recent_changes
                )
                
                # Show loading spinner
                with st.spinner("Analyzing campaign performance..."):
                    evaluator = CampaignEvaluator()
                    evaluation = evaluator.evaluate_client(client_info)
                
                # Display results
                st.success("Analysis Complete!")
                
                # Category with color coding
                category = evaluation.get("category", "unknown")
                category_info = config.HEALTH_CATEGORIES.get(category, {
                    "name": "Unknown",
                    "icon": "⚪",
                    "description": "Unable to categorize"
                })
                
                st.markdown(f"### {category_info['icon']} **Campaign Status**")
                st.markdown(f"**{category_info['name']}**")
                st.markdown(f"*{category_info['description']}*")
                
                # Confidence level
                confidence = evaluation.get("confidence", "Unknown")
                st.markdown(f"**Confidence Level:** {confidence}%")
                
                # Main assessment sections
                st.markdown("### 🎯 **Campaign Analysis**")
                st.write(evaluation.get("reasoning", "No analysis provided"))
                
                # Budget assessment
                budget_assessment = evaluation.get("budget_assessment", "")
                if budget_assessment:
                    st.markdown("### 💰 **Budget Assessment**")
                    st.write(budget_assessment)
                
                # Performance assessment
                performance_assessment = evaluation.get("performance_assessment", "")
                if performance_assessment:
                    st.markdown("### 📊 **Performance Assessment**")
                    st.write(performance_assessment)
                
                # Client satisfaction
                client_satisfaction = evaluation.get("client_satisfaction", "")
                if client_satisfaction:
                    st.markdown("### 😊 **Client Satisfaction**")
                    st.write(client_satisfaction)
                
                # Recommendations
                recommendations = evaluation.get("recommendations", [])
                if recommendations:
                    st.markdown("### 💡 **Action Items**")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                
                # Risk factors
                risk_factors = evaluation.get("risk_factors", [])
                if risk_factors:
                    st.markdown("### ⚠️ **Risk Factors**")
                    for factor in risk_factors:
                        st.write(f"• {factor}")
                
                # Positive indicators
                positive_indicators = evaluation.get("positive_indicators", [])
                if positive_indicators:
                    st.markdown("### ✅ **Opportunities & Strengths**")
                    for indicator in positive_indicators:
                        st.write(f"• {indicator}")
                
                # Export option
                st.markdown("---")
                if st.button("📄 Export Campaign Report"):
                    report = {
                        "campaign_info": {
                            "company_name": client_info.company_name,
                            "account_manager": client_info.account_manager,
                            "monthly_budget": client_info.monthly_budget,
                            "campaign_duration_months": client_info.campaign_duration_months,
                            "assessment_date": datetime.now().isoformat()
                        },
                        "evaluation": evaluation
                    }
                    st.download_button(
                        label="Download Campaign Assessment",
                        data=json.dumps(report, indent=2),
                        file_name=f"{company_name.replace(' ', '_')}_campaign_assessment.json",
                        mime="application/json"
                    )

if __name__ == "__main__":
    main()