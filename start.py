#!/usr/bin/env python3
"""
Startup script for the Client Health Assessment Chatbot
This script checks dependencies and starts the FastAPI application
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'litellm',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_environment():
    """Check environment configuration"""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        if env_example.exists():
            print(f"📋 Please copy {env_example} to .env and configure your API keys")
            print("   cp env_example.txt .env")
        else:
            print("📋 Please create a .env file with your API configuration")
        print()
    
    # Check for at least one API key
    api_keys = [
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY")
    ]
    
    if not any(api_keys):
        print("⚠️  No API keys found in environment variables")
        print("Available providers:")
        print("  - OpenAI: Set OPENAI_API_KEY")
        print("  - Anthropic: Set ANTHROPIC_API_KEY")
        print("  - See LiteLLM docs for more providers")
        print()
        return False
    else:
        providers = []
        if os.getenv("OPENAI_API_KEY"):
            providers.append("OpenAI")
        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append("Anthropic")
        print(f"✅ API keys found for: {', '.join(providers)}")
        return True

def check_directories():
    """Ensure required directories exist"""
    directories = ['backend', 'frontend', 'traces']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"📁 Creating directory: {directory}")
            dir_path.mkdir(exist_ok=True)

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting the Client Health Assessment Chatbot...")
    print("The application will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the application")
    print()
    
    try:
        # Change to the project directory to ensure proper imports
        os.chdir(Path(__file__).parent)
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're in the correct directory")
        print("2. Check that backend/main.py exists")
        print("3. Verify your .env configuration")

def main():
    """Main startup function"""
    print("=" * 60)
    print("CLIENT HEALTH ASSESSMENT CHATBOT")
    print("=" * 60)
    print()
    
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        if input("Install missing packages? (y/n): ").lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            print("Cannot start without required packages")
            sys.exit(1)
    else:
        print("✅ All dependencies are installed")
    
    # Check directories
    check_directories()
    
    # Check environment
    has_api_keys = check_environment()
    if not has_api_keys:
        print("⚠️  Warning: No API keys configured. The application may not work properly.")
        if input("Continue anyway? (y/n): ").lower() != 'y':
            sys.exit(1)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()