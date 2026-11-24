import os
import dotenv
from pathlib import Path
from openai import OpenAI

dotenv.load_dotenv()

DEFAULT_MAX_TOKENS = 8000

MODEL_ID = os.getenv("MODEL_ID")

WORKING_DIR = Path.cwd()

os.system("chcp 65001")

TEXT_ENCODING = "utf-8"

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

SKILLS_DIR = WORKING_DIR / "skills"

MAX_BYTES = 10000

PERSIST_THRESHOLD = 1000

TOOL_RESULTS_DIR = WORKING_DIR / ".task_outputs" / "tool_results"

MAX_MESSAGES = 50

KEEP_RECENT = 10

CONTEXT_LIMIT = 10000

TRANSCRIPT_DIR = WORKING_DIR / ".transcripts"
