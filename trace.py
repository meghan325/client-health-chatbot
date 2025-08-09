"""
Conversation Tracing Module for Client Health Chatbot
This module provides comprehensive tracing capabilities for all user interactions and bot responses.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import streamlit as st

@dataclass
class TraceEvent:
    """Individual trace event (user message or bot response)"""
    event_id: str
    session_id: str
    timestamp: str
    event_type: str  # 'user_request' or 'bot_response'
    content: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class ConversationTrace:
    """Complete conversation trace for a session"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    user_info: Dict[str, Any]
    events: List[TraceEvent]
    summary: Dict[str, Any]

class ConversationTracer:
    """Main class for managing conversation traces"""
    
    def __init__(self, traces_dir: str = "traces"):
        self.traces_dir = traces_dir
        self.ensure_traces_directory()
        
    def ensure_traces_directory(self):
        """Create traces directory if it doesn't exist"""
        if not os.path.exists(self.traces_dir):
            os.makedirs(self.traces_dir)
            
    def get_session_id(self) -> str:
        """Get or create session ID for current Streamlit session"""
        if 'trace_session_id' not in st.session_state:
            st.session_state.trace_session_id = str(uuid.uuid4())
        return st.session_state.trace_session_id
    
    def create_new_session(self, user_info: Dict[str, Any] = None) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        st.session_state.trace_session_id = session_id
        
        # Initialize session trace
        trace = ConversationTrace(
            session_id=session_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            end_time=None,
            user_info=user_info or {},
            events=[],
            summary={}
        )
        
        self.save_trace(trace)
        return session_id
    
    def trace_user_request(self, 
                          company_name: str,
                          client_info: Dict[str, Any],
                          metadata: Dict[str, Any] = None) -> str:
        """Trace a user request for campaign analysis"""
        session_id = self.get_session_id()
        event_id = str(uuid.uuid4())
        
        content = {
            "company_name": company_name,
            "client_info": client_info,
            "request_type": "campaign_analysis"
        }
        
        event = TraceEvent(
            event_id=event_id,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="user_request",
            content=content,
            metadata=metadata or {}
        )
        
        self.add_event_to_trace(session_id, event)
        return event_id
    
    def trace_bot_response(self,
                          request_event_id: str,
                          evaluation_result: Dict[str, Any],
                          processing_time: float = None,
                          metadata: Dict[str, Any] = None) -> str:
        """Trace a bot response with evaluation results"""
        session_id = self.get_session_id()
        event_id = str(uuid.uuid4())
        
        content = {
            "request_event_id": request_event_id,
            "evaluation": evaluation_result,
            "response_type": "campaign_evaluation"
        }
        
        trace_metadata = metadata or {}
        if processing_time is not None:
            trace_metadata["processing_time_seconds"] = processing_time
            
        event = TraceEvent(
            event_id=event_id,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="bot_response",
            content=content,
            metadata=trace_metadata
        )
        
        self.add_event_to_trace(session_id, event)
        return event_id
    
    def trace_error(self,
                   error_message: str,
                   error_type: str,
                   context: Dict[str, Any] = None) -> str:
        """Trace an error event"""
        session_id = self.get_session_id()
        event_id = str(uuid.uuid4())
        
        content = {
            "error_message": error_message,
            "error_type": error_type,
            "context": context or {}
        }
        
        event = TraceEvent(
            event_id=event_id,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="error",
            content=content,
            metadata={}
        )
        
        self.add_event_to_trace(session_id, event)
        return event_id
    
    def add_event_to_trace(self, session_id: str, event: TraceEvent):
        """Add an event to an existing trace"""
        trace = self.load_trace(session_id)
        if trace:
            trace.events.append(event)
            self.save_trace(trace)
    
    def get_trace_filename(self, session_id: str) -> str:
        """Get the filename for a trace session"""
        return os.path.join(self.traces_dir, f"trace_{session_id}.json")
    
    def save_trace(self, trace: ConversationTrace):
        """Save trace to file"""
        filename = self.get_trace_filename(trace.session_id)
        with open(filename, 'w') as f:
            json.dump(asdict(trace), f, indent=2, default=str)
    
    def load_trace(self, session_id: str) -> Optional[ConversationTrace]:
        """Load trace from file"""
        filename = self.get_trace_filename(session_id)
        if not os.path.exists(filename):
            return None
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Convert events back to TraceEvent objects
            events = [TraceEvent(**event) for event in data.get('events', [])]
            data['events'] = events
            
            return ConversationTrace(**data)
        except Exception as e:
            print(f"Error loading trace {session_id}: {e}")
            return None
    
    def end_session(self, session_id: str = None, summary: Dict[str, Any] = None):
        """End a conversation session"""
        if session_id is None:
            session_id = self.get_session_id()
            
        trace = self.load_trace(session_id)
        if trace:
            trace.end_time = datetime.now(timezone.utc).isoformat()
            trace.summary = summary or self.generate_session_summary(trace)
            self.save_trace(trace)
    
    def generate_session_summary(self, trace: ConversationTrace) -> Dict[str, Any]:
        """Generate automatic summary of conversation session"""
        user_requests = [e for e in trace.events if e.event_type == "user_request"]
        bot_responses = [e for e in trace.events if e.event_type == "bot_response"]
        errors = [e for e in trace.events if e.event_type == "error"]
        
        companies_analyzed = list(set(
            event.content.get("company_name", "Unknown") 
            for event in user_requests
        ))
        
        categories_assigned = []
        for response in bot_responses:
            evaluation = response.content.get("evaluation", {})
            category = evaluation.get("category")
            if category:
                categories_assigned.append(category)
        
        total_processing_time = sum(
            response.metadata.get("processing_time_seconds", 0)
            for response in bot_responses
        )
        
        return {
            "total_requests": len(user_requests),
            "total_responses": len(bot_responses),
            "total_errors": len(errors),
            "companies_analyzed": companies_analyzed,
            "categories_assigned": categories_assigned,
            "total_processing_time": total_processing_time,
            "session_duration_minutes": self.calculate_session_duration(trace),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_session_duration(self, trace: ConversationTrace) -> float:
        """Calculate session duration in minutes"""
        if not trace.events:
            return 0
            
        start_time = datetime.fromisoformat(trace.start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(trace.end_time.replace('Z', '+00:00')) if trace.end_time else datetime.now(timezone.utc)
        
        duration = end_time - start_time
        return duration.total_seconds() / 60
    
    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """List all available trace sessions"""
        sessions = []
        
        if not os.path.exists(self.traces_dir):
            return sessions
            
        for filename in os.listdir(self.traces_dir):
            if filename.startswith("trace_") and filename.endswith(".json"):
                session_id = filename.replace("trace_", "").replace(".json", "")
                trace = self.load_trace(session_id)
                
                if trace:
                    sessions.append({
                        "session_id": session_id,
                        "start_time": trace.start_time,
                        "end_time": trace.end_time,
                        "event_count": len(trace.events),
                        "summary": trace.summary
                    })
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x["start_time"], reverse=True)
        return sessions
    
    def export_trace(self, session_id: str, format: str = "json") -> str:
        """Export trace in specified format"""
        trace = self.load_trace(session_id)
        if not trace:
            raise ValueError(f"Trace not found for session {session_id}")
        
        if format.lower() == "json":
            return json.dumps(asdict(trace), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def delete_trace(self, session_id: str) -> bool:
        """Delete a trace session"""
        filename = self.get_trace_filename(session_id)
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True
            except Exception as e:
                print(f"Error deleting trace {session_id}: {e}")
                return False
        return False
    
    def get_conversation_history(self, session_id: str = None) -> List[Dict[str, Any]]:
        """Get formatted conversation history for display"""
        if session_id is None:
            session_id = self.get_session_id()
            
        trace = self.load_trace(session_id)
        if not trace:
            return []
        
        history = []
        for event in trace.events:
            if event.event_type == "user_request":
                history.append({
                    "type": "user",
                    "timestamp": event.timestamp,
                    "company": event.content.get("company_name", "Unknown"),
                    "content": event.content
                })
            elif event.event_type == "bot_response":
                evaluation = event.content.get("evaluation", {})
                history.append({
                    "type": "bot",
                    "timestamp": event.timestamp,
                    "category": evaluation.get("category", "unknown"),
                    "confidence": evaluation.get("confidence", "unknown"),
                    "content": evaluation
                })
        
        return history
