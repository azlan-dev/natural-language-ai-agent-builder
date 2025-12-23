#!/usr/bin/env python
"""
Quick start script for Natural Language Agent Builder.
This script checks dependencies and launches the Streamlit app.
"""
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import langchain
        import pydantic
        import jsonschema
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("\n📦 Please install dependencies first:")
        print("   pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("\n📝 Please create a .env file with your API keys:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your API keys (OpenAI or Google)")
        print("\nExample:")
        print("   cp .env.example .env")
        print("   # Then edit .env with your keys")
        return False
    return True

def main():
    """Main entry point."""
    print("🧠 Natural Language Agent Builder")
    print("=" * 50)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ Dependencies OK")
    
    # Check environment
    print("\n🔍 Checking environment configuration...")
    if not check_env_file():
        print("\n⚠️  You can still proceed, but the app will show configuration errors.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✅ Environment OK")
    
    # Launch Streamlit
    print("\n🚀 Launching application...")
    print("=" * 50)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()

