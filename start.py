#!/usr/bin/env python3
"""
Startup script for the Client Health Assessment Chatbot
This script checks dependencies and starts the Streamlit application
"""

import os
import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'openai'
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

def check_api_key():
    """Check if API key is available"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OpenAI API key not found in environment variables")
        print("You can:")
        print("1. Set it as an environment variable: export OPENAI_API_KEY='your_key_here'")
        print("2. Enter it in the web interface when prompted")
        print()
        return False
    else:
        print("✅ OpenAI API key found")
        return True

def start_application():
    """Start the Streamlit application"""
    print("🚀 Starting the Client Health Assessment Chatbot...")
    print("The application will open in your default web browser")
    print("Press Ctrl+C to stop the application")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")

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
    
    # Check API key
    check_api_key()
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()