"""
Conversation Tracing Manager for Client Health Chatbot
FastAPI-compatible version without Streamlit dependencies
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any

@dataclass
class TraceEvent:
    """Individual trace event (user request, bot response, or error)"""
    event_id: str
    conversation_id: str
    timestamp: str
    event_type: str  # 'user_request', 'bot_response', or 'error'
    content: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class ConversationTrace:
    """Complete conversation trace"""
    conversation_id: str
    start_time: str
    end_time: Optional[str]
    events: List[TraceEvent]
    summary: Dict[str, Any]

class TraceManager:
    """Manager for conversation traces without Streamlit dependencies"""
    
    def __init__(self, traces_dir: str = "traces"):
        self.traces_dir = traces_dir
        self.ensure_traces_directory()
        
    def ensure_traces_directory(self):
        """Create traces directory if it doesn't exist"""
        if not os.path.exists(self.traces_dir):
            os.makedirs(self.traces_dir)
    
    def trace_user_request(self, 
                          conversation_id: str,
                          company_name: str,
                          client_info: Dict[str, Any],
                          metadata: Dict[str, Any] = None) -> str:
        """Trace a user request for campaign analysis"""
        event_id = str(uuid.uuid4())
        
        content = {
            "company_name": company_name,
            "client_info": client_info,
            "request_type": "campaign_analysis"
        }
        
        event = TraceEvent(
            event_id=event_id,
            conversation_id=conversation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="user_request",
            content=content,
            metadata=metadata or {}
        )
        
        self.add_event_to_trace(conversation_id, event)
        return event_id
    
    def trace_bot_response(self,
                          conversation_id: str,
                          evaluation_result: Dict[str, Any],
                          processing_time: float = None,
                          metadata: Dict[str, Any] = None) -> str:
        """Trace a bot response with evaluation results"""
        event_id = str(uuid.uuid4())
        
        content = {
            "evaluation": evaluation_result,
            "response_type": "campaign_evaluation"
        }
        
        trace_metadata = metadata or {}
        if processing_time is not None:
            trace_metadata["processing_time_seconds"] = processing_time
            
        event = TraceEvent(
            event_id=event_id,
            conversation_id=conversation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="bot_response",
            content=content,
            metadata=trace_metadata
        )
        
        self.add_event_to_trace(conversation_id, event)
        return event_id
    
    def trace_error(self,
                   conversation_id: str,
                   error_message: str,
                   error_type: str,
                   context: Dict[str, Any] = None) -> str:
        """Trace an error event"""
        event_id = str(uuid.uuid4())
        
        content = {
            "error_message": error_message,
            "error_type": error_type,
            "context": context or {}
        }
        
        event = TraceEvent(
            event_id=event_id,
            conversation_id=conversation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="error",
            content=content,
            metadata={}
        )
        
        self.add_event_to_trace(conversation_id, event)
        return event_id
    
    def add_event_to_trace(self, conversation_id: str, event: TraceEvent):
        """Add an event to an existing trace or create new trace"""
        trace = self.load_trace(conversation_id)
        if trace:
            trace.events.append(event)
        else:
            # Create new trace
            trace = ConversationTrace(
                conversation_id=conversation_id,
                start_time=event.timestamp,
                end_time=None,
                events=[event],
                summary={}
            )
        
        self.save_trace(trace)
    
    def get_trace_filename(self, conversation_id: str) -> str:
        """Get the filename for a trace"""
        return os.path.join(self.traces_dir, f"trace_{conversation_id}.json")
    
    def save_trace(self, trace: ConversationTrace):
        """Save trace to file"""
        filename = self.get_trace_filename(trace.conversation_id)
        with open(filename, 'w') as f:
            json.dump(asdict(trace), f, indent=2, default=str)
    
    def load_trace(self, conversation_id: str) -> Optional[ConversationTrace]:
        """Load trace from file"""
        filename = self.get_trace_filename(conversation_id)
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
            print(f"Error loading trace {conversation_id}: {e}")
            return None
    
    def end_conversation(self, conversation_id: str, summary: Dict[str, Any] = None):
        """End a conversation and generate summary"""
        trace = self.load_trace(conversation_id)
        if trace:
            trace.end_time = datetime.now(timezone.utc).isoformat()
            trace.summary = summary or self.generate_conversation_summary(trace)
            self.save_trace(trace)
    
    def generate_conversation_summary(self, trace: ConversationTrace) -> Dict[str, Any]:
        """Generate automatic summary of conversation"""
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
            "conversation_duration_minutes": self.calculate_conversation_duration(trace),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def calculate_conversation_duration(self, trace: ConversationTrace) -> float:
        """Calculate conversation duration in minutes"""
        if not trace.events:
            return 0
            
        start_time = datetime.fromisoformat(trace.start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(trace.end_time.replace('Z', '+00:00')) if trace.end_time else datetime.now(timezone.utc)
        
        duration = end_time - start_time
        return duration.total_seconds() / 60
    
    def list_all_conversations(self) -> List[Dict[str, Any]]:
        """List all available conversations"""
        conversations = []
        
        if not os.path.exists(self.traces_dir):
            return conversations
            
        for filename in os.listdir(self.traces_dir):
            if filename.startswith("trace_") and filename.endswith(".json"):
                conversation_id = filename.replace("trace_", "").replace(".json", "")
                trace = self.load_trace(conversation_id)
                
                if trace and trace.events:
                    # Get company name and category from first request/response
                    company_name = "Unknown"
                    category = "unknown"
                    confidence = 0
                    
                    for event in trace.events:
                        if event.event_type == "user_request":
                            company_name = event.content.get("company_name", "Unknown")
                        elif event.event_type == "bot_response":
                            evaluation = event.content.get("evaluation", {})
                            category = evaluation.get("category", "unknown")
                            confidence = evaluation.get("confidence", 0)
                            break
                    
                    conversations.append({
                        "conversation_id": conversation_id,
                        "timestamp": trace.start_time,
                        "company_name": company_name,
                        "category": category,
                        "confidence": confidence,
                        "event_count": len(trace.events)
                    })
        
        # Sort by timestamp (newest first)
        conversations.sort(key=lambda x: x["timestamp"], reverse=True)
        return conversations
    
    def get_conversation_details(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed conversation information"""
        trace = self.load_trace(conversation_id)
        if not trace:
            return None
        
        # Format events for display
        formatted_events = []
        for event in trace.events:
            formatted_event = {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "content": event.content,
                "metadata": event.metadata
            }
            formatted_events.append(formatted_event)
        
        return {
            "conversation_id": trace.conversation_id,
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "events": formatted_events,
            "summary": trace.summary
        }
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation trace"""
        filename = self.get_trace_filename(conversation_id)
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True
            except Exception as e:
                print(f"Error deleting trace {conversation_id}: {e}")
                return False
        return False
    
    def cleanup_old_traces(self, max_age_days: int = 30):
        """Clean up traces older than specified days"""
        if not os.path.exists(self.traces_dir):
            return
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        
        for filename in os.listdir(self.traces_dir):
            if filename.startswith("trace_") and filename.endswith(".json"):
                filepath = os.path.join(self.traces_dir, filename)
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        print(f"Cleaned up old trace: {filename}")
                except Exception as e:
                    print(f"Error cleaning up trace {filename}: {e}")
    
    def cleanup(self):
        """Perform cleanup operations"""
        # Could add automatic cleanup here
        pass
