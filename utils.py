from pathlib import Path
from config import WORKING_DIR


def decode_subprocess_output(output: bytes) -> str:
    if not output:
        return ""
    for encoding in ("utf-8", "gbk", "cp936"):
        try:
            return output.decode(encoding)
        except UnicodeDecodeError:
            continue
    return output.decode("utf-8", errors="replace")


def safe_path(path: str) -> Path:
    path = (WORKING_DIR / path).resolve()

    if not path.is_relative_to(WORKING_DIR):
        raise ValueError(f"路径超出工作区：{path}")

    return path


def parse_frontmatter(text: str) -> tuple[dict, str]:

    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}, text

    meta = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"').strip("'")

    return meta, parts[2].strip()
