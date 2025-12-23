"""Configuration management for the agent builder."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
GENERATED_AGENTS_DIR = PROJECT_ROOT / "generated_agents"

# Ensure directories exist
GENERATED_AGENTS_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")

# Vector Store Configuration
ENABLE_VECTOR_STORE = os.getenv("ENABLE_VECTOR_STORE", "true").lower() == "true"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# Validation
def validate_config():
    """Validate configuration settings."""
    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set when using OpenAI provider")
    if LLM_PROVIDER == "google" and not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY must be set when using Google provider")
    return True

