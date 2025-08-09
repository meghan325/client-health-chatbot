# Client Health Assessment Chatbot

An AI-powered tool for analyzing advertising campaign health and providing actionable insights to optimize client performance and satisfaction. Built with FastAPI and supporting multiple LLM providers through LiteLLM.

## Features

- **Multi-Provider LLM Support**: Works with OpenAI, Anthropic, and other providers via LiteLLM
- **Intelligent Campaign Analysis**: Uses AI models to evaluate campaign performance across multiple metrics
- **Health Classification**: Categorizes campaigns into four distinct health levels:
  - 🟢 **Campaign Healthy**: Performing well, on track
  - 🟡 **Monitoring Needed**: Optimization opportunities exist
  - 🟠 **Growth Opportunity**: Positive indicators for scaling
  - 🔴 **Risk Management**: Immediate attention required

- **Comprehensive Assessment**: Analyzes budget efficiency, performance metrics, client satisfaction, and campaign objectives
- **Actionable Recommendations**: Provides specific, actionable recommendations for campaign optimization
- **Risk & Opportunity Identification**: Highlights both potential risks and growth opportunities
- **Conversation Tracing**: Optional tracing of all interactions for analysis and improvement
- **Modern Web Interface**: Clean, responsive HTML/CSS/JS frontend similar to recipe-chatbot
- **REST API**: FastAPI backend with full API documentation

## Quick Start

### Prerequisites
- Python 3.8 or higher
- API key for at least one supported LLM provider (OpenAI, Anthropic, etc.)

### Installation

1. **Clone or download this repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment**:
   ```bash
   cp env_example.txt .env
   # Edit .env file and configure your API keys and model preference
   ```

4. **Run the application**:
   ```bash
   python start.py
   ```
   
   Or directly with uvicorn:
   ```bash
   uvicorn backend.main:app --reload
   ```

The application will be available at `http://localhost:8000`

## Configuration

### Environment Variables (.env file)

```bash
# Model Configuration (LiteLLM format)
MODEL_NAME=gpt-3.5-turbo
# Alternatives:
# MODEL_NAME=openai/gpt-4
# MODEL_NAME=anthropic/claude-3-haiku-20240307

# API Keys (add only the ones you need)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Configuration
MAX_TOKENS=1000
TEMPERATURE=0.3

# Tracing Configuration
TRACE_ENABLED=true
TRACES_DIRECTORY=traces
MAX_TRACE_AGE_DAYS=30
INCLUDE_SENSITIVE_DATA=false
```

### Supported LLM Providers

Thanks to LiteLLM, you can use any of these providers:
- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
- **Anthropic**: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`
- **Cohere**: `command-nightly`
- **Replicate**: Various open-source models
- **Hugging Face**: Various models
- And many more - see [LiteLLM docs](https://litellm.vercel.app/docs/providers)

## Usage

### Web Interface

1. **Navigate to Campaign Analysis**:
   - Open `http://localhost:8000` in your browser
   - Fill out the campaign information form
   - Click "Analyze Campaign Health"

2. **View Results**:
   - Health category classification with confidence level
   - Detailed reasoning and analysis
   - Specific action items and recommendations
   - Risk factors and positive indicators
   - Budget, performance, and client satisfaction assessments

3. **View History**:
   - Click "View History" to see past analyses
   - Click on any analysis to view detailed results
   - Conversation traces are automatically saved

### API Endpoints

The FastAPI backend provides REST endpoints:

- **POST /api/analyze**: Analyze campaign health
- **GET /api/conversations**: List all conversation history
- **GET /api/conversations/{id}**: Get specific conversation details
- **DELETE /api/conversations/{id}**: Delete a conversation
- **GET /api/config**: Get current configuration
- **GET /health**: Health check endpoint

Full API documentation available at `http://localhost:8000/docs`

### API Integration Example

```python
import requests

# Analyze campaign
response = requests.post("http://localhost:8000/api/analyze", json={
    "company_name": "Example Corp",
    "account_manager": "John Doe",
    "monthly_budget": 50000,
    "campaign_duration_months": 6,
    "campaign_objectives": "Brand awareness and lead generation",
    "current_performance_metrics": "CTR: 2.3%, CPA: $45, ROAS: 3.2x",
    "budget_utilization": "85% spend rate, on track",
    "client_reported_notes": "Happy with performance",
    "recent_changes_or_concerns": "None"
})

result = response.json()
print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']}%")
```

## Project Structure

```
client-health-chatbot/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration management
│   ├── client_evaluator.py  # Core evaluation logic
│   └── trace_manager.py     # Conversation tracing
├── frontend/
│   ├── index.html           # Main web interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── traces/                  # Conversation trace storage (auto-created)
├── start.py                # Startup script
├── requirements.txt        # Python dependencies
├── env_example.txt         # Environment variable template
├── README.md               # This file
├── app.py                  # Legacy Streamlit app (can be removed)
├── config.py               # Legacy config (can be removed)
├── trace.py                # Legacy trace module (can be removed)
├── test_chatbot.py         # Legacy test script
└── TRACE_USAGE.md          # Tracing documentation
```

## Testing

Test the application with sample data:

```bash
# Test with the web interface
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "account_manager": "Jane Smith",
    "monthly_budget": 25000,
    "campaign_duration_months": 3,
    "campaign_objectives": "Drive sales",
    "current_performance_metrics": "CTR: 1.5%",
    "budget_utilization": "90% utilized",
    "client_reported_notes": "Concerned about costs",
    "recent_changes_or_concerns": "Budget constraints"
  }'
```

## Conversation Tracing

The application automatically traces conversations when enabled:
- User requests with campaign information
- AI responses with evaluations
- Processing times and metadata
- Error events for debugging

Traces are stored as JSON files in the `traces/` directory and can be viewed through the web interface or accessed via API.

## Migration from Streamlit

If you have the previous Streamlit version, the new FastAPI version provides:
- **Better Performance**: Async processing and faster response times
- **API Access**: RESTful endpoints for integration
- **Multi-Provider Support**: Not limited to OpenAI
- **Modern Frontend**: Responsive design without Streamlit dependencies
- **Production Ready**: Better suited for deployment and scaling

The old files (`app.py`, `config.py`, `trace.py`) can be safely removed after migration.

## Deployment

### Local Development
```bash
python start.py
```

### Production Deployment
```bash
# Using uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Using gunicorn with uvicorn workers
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **API Key Errors**: Check your `.env` file configuration
3. **Model Not Found**: Verify the MODEL_NAME format matches LiteLLM conventions
4. **Port Already in Use**: Change the port in start.py or kill existing processes

### Getting Help

1. Check the FastAPI logs for detailed error messages
2. Visit `http://localhost:8000/docs` for API documentation
3. Verify your `.env` configuration matches `env_example.txt`
4. Test individual endpoints with curl or Postman

## Security & Privacy

- **Data Storage**: Conversation traces are stored locally, can be disabled
- **API Security**: All API calls use secure connections
- **Environment Variables**: Sensitive keys stored in `.env` (not committed)
- **Input Validation**: Comprehensive input validation via Pydantic models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

The codebase is modular and designed for easy customization of evaluation logic, health categories, and frontend appearance.

## License

This project is provided as-is for advertising campaign analysis. Customize as needed for your organization.