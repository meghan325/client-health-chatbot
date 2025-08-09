import os
import streamlit as st
import openai
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import re
from datetime import datetime
import time
import config
from trace import ConversationTracer

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
        self.tracer = ConversationTracer(config.TRACE_SETTINGS["traces_directory"]) if config.TRACE_SETTINGS["enabled"] else None
    
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
        start_time = time.time()
        request_event_id = None
        
        # Trace user request
        if self.tracer and config.TRACE_SETTINGS["enabled"]:
            client_data = {
                "company_name": client_info.company_name,
                "account_manager": client_info.account_manager,
                "monthly_budget": client_info.monthly_budget,
                "campaign_duration_months": client_info.campaign_duration_months
            }
            
            # Include non-sensitive data based on settings
            if config.TRACE_SETTINGS["include_sensitive_data"]:
                client_data.update({
                    "campaign_objectives": client_info.campaign_objectives,
                    "current_performance_metrics": client_info.current_performance_metrics,
                    "budget_utilization": client_info.budget_utilization,
                    "client_reported_notes": client_info.client_reported_notes,
                    "recent_changes_or_concerns": client_info.recent_changes_or_concerns
                })
            
            request_event_id = self.tracer.trace_user_request(
                company_name=client_info.company_name,
                client_info=client_data
            )
        
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
            
            # Trace bot response
            if self.tracer and config.TRACE_SETTINGS["enabled"] and request_event_id:
                self.tracer.trace_bot_response(
                    request_event_id=request_event_id,
                    evaluation_result=evaluation,
                    processing_time=processing_time if config.TRACE_SETTINGS["trace_performance"] else None,
                    metadata={
                        "openai_model": config.OPENAI_MODEL,
                        "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
                    }
                )
            
            return evaluation
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Error occurred during evaluation: {str(e)}"
            
            # Trace error
            if self.tracer and config.TRACE_SETTINGS["enabled"] and config.TRACE_SETTINGS["trace_errors"]:
                self.tracer.trace_error(
                    error_message=str(e),
                    error_type="evaluation_error",
                    context={
                        "company_name": client_info.company_name,
                        "processing_time": processing_time,
                        "openai_model": config.OPENAI_MODEL
                    }
                )
            
            st.error(f"Error during evaluation: {str(e)}")
            return {
                "category": "might_need_attention",
                "confidence": "0",
                "reasoning": error_message,
                "recommendations": ["Please try again or consult with account management team"],
                "risk_factors": ["System error"],
                "positive_indicators": [],
                "budget_assessment": "Analysis failed",
                "performance_assessment": "Analysis failed",
                "client_satisfaction": "Analysis failed"
            }

def show_trace_viewer():
    """Display trace viewing interface"""
    st.header("🔍 Conversation Traces")
    
    if not config.TRACE_SETTINGS["enabled"]:
        st.warning("Tracing is currently disabled. Enable it in configuration to view traces.")
        return
    
    tracer = ConversationTracer(config.TRACE_SETTINGS["traces_directory"])
    sessions = tracer.list_all_sessions()
    
    if not sessions:
        st.info("No conversation traces found yet. Start analyzing campaigns to create traces.")
        return
    
    # Session selector
    session_options = {
        f"Session {session['session_id'][:8]} - {session['start_time'][:19]} ({session['event_count']} events)": session['session_id']
        for session in sessions
    }
    
    selected_session_display = st.selectbox(
        "Select a conversation session to view:",
        list(session_options.keys())
    )
    
    if selected_session_display:
        session_id = session_options[selected_session_display]
        trace = tracer.load_trace(session_id)
        
        if trace:
            # Session summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Events", len(trace.events))
            with col2:
                user_requests = sum(1 for e in trace.events if e.event_type == "user_request")
                st.metric("User Requests", user_requests)
            with col3:
                bot_responses = sum(1 for e in trace.events if e.event_type == "bot_response")
                st.metric("Bot Responses", bot_responses)
            with col4:
                errors = sum(1 for e in trace.events if e.event_type == "error")
                st.metric("Errors", errors, delta_color="inverse")
            
            st.markdown("---")
            
            # Conversation history
            history = tracer.get_conversation_history(session_id)
            
            for item in history:
                timestamp = datetime.fromisoformat(item["timestamp"].replace('Z', '+00:00')).strftime("%H:%M:%S")
                
                if item["type"] == "user":
                    with st.container():
                        st.markdown(f"**👤 User Request** - {timestamp}")
                        st.markdown(f"**Company:** {item['company']}")
                        
                        with st.expander("View request details"):
                            st.json(item["content"])
                
                elif item["type"] == "bot":
                    with st.container():
                        st.markdown(f"**🤖 Bot Response** - {timestamp}")
                        
                        category_info = config.HEALTH_CATEGORIES.get(item["category"], {
                            "name": "Unknown",
                            "icon": "⚪"
                        })
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"{category_info['icon']} **{category_info['name']}**")
                        with col2:
                            st.markdown(f"**Confidence:** {item['confidence']}%")
                        
                        with st.expander("View full evaluation"):
                            st.json(item["content"])
                
                st.markdown("---")
            
            # Export options
            st.subheader("📥 Export Options")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("📄 Export JSON", key=f"export_{session_id}"):
                    export_data = tracer.export_trace(session_id, "json")
                    st.download_button(
                        label="Download Trace",
                        data=export_data,
                        file_name=f"trace_{session_id[:8]}.json",
                        mime="application/json",
                        key=f"download_{session_id}"
                    )
            
            with col2:
                if st.button("🗑️ Delete Trace", key=f"delete_{session_id}"):
                    if tracer.delete_trace(session_id):
                        st.success("Trace deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete trace")

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AdTech Campaign Health Analyzer",
        page_icon="📺",
        layout="wide"
    )
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page:", ["Campaign Analyzer", "Trace Viewer"])
    
    if page == "Trace Viewer":
        show_trace_viewer()
        return
    
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
    
    # Show current session info if tracing is enabled
    if config.TRACE_SETTINGS["enabled"]:
        st.sidebar.header("🔍 Current Session")
        tracer = ConversationTracer(config.TRACE_SETTINGS["traces_directory"])
        session_id = tracer.get_session_id()
        
        st.sidebar.info(f"**Session ID**: {session_id[:8]}...")
        
        # Show session statistics
        trace = tracer.load_trace(session_id)
        if trace and trace.events:
            requests = sum(1 for e in trace.events if e.event_type == "user_request")
            responses = sum(1 for e in trace.events if e.event_type == "bot_response")
            st.sidebar.metric("Requests this session", requests)
            st.sidebar.metric("Responses this session", responses)
        
        if st.sidebar.button("🔄 Start New Session"):
            tracer.end_session()
            tracer.create_new_session()
            st.rerun()
    
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