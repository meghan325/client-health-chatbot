# Trace Capabilities Documentation

This document explains how to use the comprehensive trace capabilities added to the Client Health Chatbot.

## Overview

The tracing system captures all user interactions and bot responses, providing detailed conversation logs for analysis, debugging, and reporting.

## Features

### 1. Automatic Conversation Tracing
- **User Requests**: Captures company information and campaign data submitted for analysis
- **Bot Responses**: Records evaluation results, confidence scores, and processing metrics
- **Error Tracking**: Logs any errors that occur during processing
- **Session Management**: Groups interactions into sessions with unique identifiers

### 2. Data Captured

#### User Requests
- Company name and account manager
- Campaign budget and duration
- Performance metrics and objectives
- Client notes and concerns
- Timestamp and session information

#### Bot Responses
- Complete evaluation results (category, confidence, reasoning)
- Processing time and performance metrics
- OpenAI model used and token consumption
- Link to originating request

#### Errors
- Error messages and types
- Context information
- Processing time until failure

### 3. Trace Viewing Interface

Access the trace viewer through the sidebar navigation in the Streamlit app:

1. **Session Selection**: Browse and select from available conversation sessions
2. **Session Summary**: View metrics for requests, responses, and errors
3. **Conversation Timeline**: See chronological flow of user requests and bot responses
4. **Detailed Views**: Expand to see complete data for each interaction

### 4. Export and Management

#### Export Options
- **JSON Export**: Download complete trace data for external analysis
- **Session-specific**: Export individual conversation sessions
- **Bulk Export**: Use the cleanup utility to export all traces

#### Session Management
- **New Session**: Start fresh conversation sessions
- **Session Tracking**: Monitor current session activity in sidebar
- **Auto-cleanup**: Configurable retention policies

## Configuration

Configure tracing behavior in `config.py`:

```python
TRACE_SETTINGS = {
    "enabled": True,                    # Enable/disable tracing
    "traces_directory": "traces",       # Storage directory
    "max_trace_age_days": 30,          # Retention period
    "max_traces_per_session": 1000,    # Event limit per session
    "auto_cleanup": True,               # Automatic cleanup
    "include_sensitive_data": False,    # Control data sensitivity
    "trace_errors": True,               # Log errors
    "trace_performance": True           # Capture timing metrics
}
```

## Command Line Management

Use the `trace_cleanup.py` utility for trace management:

### View Statistics
```bash
python trace_cleanup.py stats
```

### Clean Up Old Traces
```bash
# Dry run (preview what would be deleted)
python trace_cleanup.py cleanup --dry-run

# Delete traces older than 30 days
python trace_cleanup.py cleanup --days 30

# Delete traces older than 7 days
python trace_cleanup.py cleanup --days 7
```

### Export All Traces
```bash
# Export with auto-generated filename
python trace_cleanup.py export

# Export to specific file
python trace_cleanup.py export --output my_traces.json
```

## Privacy and Security

### Data Sensitivity
- By default, sensitive client data (detailed notes, performance metrics) is not stored
- Enable `include_sensitive_data` only if required and ensure proper security measures
- Traces are stored locally in JSON files

### Retention Management
- Configurable automatic cleanup based on age
- Manual deletion through UI or command line
- No data is sent to external services

## Use Cases

### 1. Debugging and Support
- Identify patterns in failed evaluations
- Track user interaction flows
- Analyze processing performance

### 2. Analytics and Reporting
- Understand usage patterns
- Track most analyzed companies/categories
- Monitor bot performance over time

### 3. Quality Assurance
- Review evaluation accuracy
- Identify areas for prompt improvement
- Track error rates and types

### 4. Audit and Compliance
- Maintain records of analyses performed
- Track when and what data was processed
- Support compliance requirements

## File Structure

```
traces/
├── trace_[session-id].json     # Individual session traces
└── ...

trace.py                        # Core tracing module
trace_cleanup.py               # Management utilities
config.py                      # Configuration settings
app.py                         # Main application with tracing integration
```

## Troubleshooting

### Common Issues

1. **Traces Not Appearing**
   - Check `TRACE_SETTINGS["enabled"]` is `True`
   - Verify traces directory exists and is writable
   - Ensure proper import of trace module

2. **Performance Issues**
   - Reduce `max_traces_per_session` if sessions become large
   - Enable automatic cleanup to manage disk space
   - Consider disabling `trace_performance` if not needed

3. **Storage Concerns**
   - Monitor trace directory size
   - Adjust `max_trace_age_days` for your needs
   - Use cleanup utility regularly

### Getting Help

If you encounter issues with the tracing system:

1. Check the console for error messages
2. Verify configuration settings
3. Review trace file permissions
4. Test with tracing disabled to isolate issues

## Example Trace Data Structure

```json
{
  "session_id": "uuid-string",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:45:00Z",
  "events": [
    {
      "event_id": "uuid-string",
      "session_id": "uuid-string", 
      "timestamp": "2024-01-15T10:31:00Z",
      "event_type": "user_request",
      "content": {
        "company_name": "TechCorp Solutions",
        "client_info": { /* campaign data */ }
      },
      "metadata": {}
    },
    {
      "event_id": "uuid-string",
      "session_id": "uuid-string",
      "timestamp": "2024-01-15T10:31:05Z", 
      "event_type": "bot_response",
      "content": {
        "evaluation": { /* assessment results */ }
      },
      "metadata": {
        "processing_time_seconds": 3.2,
        "openai_model": "gpt-3.5-turbo"
      }
    }
  ],
  "summary": {
    "total_requests": 1,
    "total_responses": 1,
    "companies_analyzed": ["TechCorp Solutions"]
  }
}
```
