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
    temperature=0,
    max_tokens=4096,
)

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
