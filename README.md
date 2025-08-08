# Client Health Assessment Chatbot

A Streamlit-based chatbot that analyzes client information and provides health evaluations using LLM APIs. The system categorizes clients into four health status categories and provides detailed assessments with recommendations.

## Features

- **Comprehensive Client Analysis**: Evaluates symptoms, medical history, medications, lifestyle factors, and recent changes
- **Four-Category Assessment System**:
  - 🟢 **Healthy**: No immediate concerns
  - 🟡 **Might Need Attention**: Monitoring recommended
  - 🟠 **Need Attention - Positive**: Manageable situation requiring attention
  - 🔴 **Need Attention - Negative**: Immediate attention required
- **AI-Powered Evaluation**: Uses OpenAI GPT models for intelligent analysis
- **Structured Output**: Provides confidence levels, reasoning, recommendations, and risk factors
- **Export Functionality**: Download assessment reports as JSON files
- **User-Friendly Interface**: Clean, intuitive Streamlit web interface

## Installation

1. **Clone or download this repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key** (choose one method):
   
   **Method 1: Environment Variable**
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   
   **Method 2: Environment File**
   - Copy `env_example.txt` to `.env`
   - Add your API key to the `.env` file
   
   **Method 3: Enter in App**
   - Run the app and enter your API key in the interface

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to the provided URL (usually `http://localhost:8501`)

3. **Enter client information**:
   - Client name and age
   - Current symptoms
   - Medical history
   - Current medications
   - Lifestyle factors
   - Recent changes

4. **Click "Analyze Client Health"** to get the assessment

5. **Review the results**:
   - Health category classification
   - Confidence level
   - Detailed reasoning
   - Specific recommendations
   - Risk factors identified
   - Positive health indicators

6. **Export report** (optional): Download a JSON report of the assessment

## Assessment Categories

### 🟢 Healthy
Client appears to be in good health with no immediate concerns. Regular monitoring may be sufficient.

### 🟡 Might Need Attention
Client shows some indicators that warrant monitoring or mild intervention. Preventive measures recommended.

### 🟠 Need Attention - Positive
Client requires attention but indicators suggest a positive or manageable situation. Proactive care recommended.

### 🔴 Need Attention - Negative
Client requires immediate attention due to concerning indicators. Urgent care or professional consultation recommended.

## API Configuration

### OpenAI (Default)
The application uses OpenAI's GPT models by default. You'll need an OpenAI API key from [OpenAI Platform](https://platform.openai.com/).

### Alternative LLM Providers
The code can be extended to support other LLM providers like:
- Anthropic Claude
- Hugging Face models
- Azure OpenAI
- Local models

## Security and Privacy

- **API Keys**: Never commit API keys to version control
- **Client Data**: Client information is processed but not stored permanently
- **HIPAA Compliance**: This tool is for general health monitoring and should not be used for protected health information without proper safeguards

## Disclaimer

⚠️ **Important Medical Disclaimer**

This application is designed for general health monitoring and educational purposes only. It should NOT be used as:
- A replacement for professional medical advice
- A diagnostic tool for medical conditions
- A substitute for consulting with healthcare professionals

Always consult with qualified healthcare providers for medical concerns and decisions.

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your OpenAI API key is valid and has sufficient credits
   - Check that the API key is properly set in environment variables or entered in the app

2. **Installation Issues**
   - Make sure you have Python 3.8 or higher
   - Use a virtual environment to avoid dependency conflicts

3. **Streamlit Issues**
   - Clear Streamlit cache: `streamlit cache clear`
   - Restart the application

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is provided as-is for educational and general monitoring purposes.