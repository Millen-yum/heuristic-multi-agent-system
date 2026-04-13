<<<<<<< HEAD
import os
from pathlib import Path
import chainlit as cl
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = PROJECT_ROOT / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_API_KEY")

llm = ChatOpenAI(
    api_key=api_key,
    model="gpt-4o-mini",
)

llm_code = ChatOpenAI(
    api_key=api_key,
    model="gpt-4o",
=======
# agents/common.py
# This file contains common objects and functions that can be shared across multiple agents or modules.
# Just for reducing redundacy
import os
import chainlit as cl
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

# from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chat_models import init_chat_model

# Load environment variables once
load_dotenv()

# Shared LLM instance
api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_API_KEY")
# Initialize OpenAI LLMs
llm = init_chat_model(api_key=api_key, model="gpt-4o-mini", model_provider="openai")
llm_code = init_chat_model(
    api_key=api_key,
    model="gpt-4o",
    model_provider="openai",
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
    temperature=0,
    max_tokens=4096,
)

<<<<<<< HEAD
# Only create Claude model if a Claude key exists
llm_code_claude = None
if claude_api_key:
    llm_code_claude = ChatAnthropic(
        api_key=claude_api_key,
        model="claude-3-5-sonnet-latest",
        temperature=0,
        max_tokens=4096,
    )

def get_generated_path(filename: str) -> Path:
    return GENERATED_DIR / filename

__all__ = [
    "cl",
    "PydanticOutputParser",
    "llm",
    "llm_code",
    "llm_code_claude",
    "PROJECT_ROOT",
    "GENERATED_DIR",
    "get_generated_path",
]
=======
# Initialize Claude LLM
""" llm_code_claude = ChatAnthropic(
    api_key=claude_api_key,
    model="claude-3-7-sonnet-latest",
    temperature=0,
    max_tokens=4096,
    disable_streaming=True,
    thinking={"type":"disabled"},
) """
llm_code_claude = init_chat_model(
    api_key=claude_api_key,
    model="claude-3-5-sonnet-latest",
    model_provider="anthropic",
    temperature=0,
    max_tokens=4096,
)

# Export common objects or functions
__all__ = ["cl", "PydanticOutputParser", "llm", "llm_code", "llm_code_claude"]
>>>>>>> e8c207795ffbe94871b8456444269f4c6fcb2acc
