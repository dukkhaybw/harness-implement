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
