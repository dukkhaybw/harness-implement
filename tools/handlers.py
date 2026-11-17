import os
import glob as g
import subprocess
from utils import decode_subprocess_output, safe_path
from config import WORKING_DIR, TEXT_ENCODING


def bash_handler(command: str) -> str:
    if os.name == "nt" and command.strip().lower() == "date":
        command = "date /t & time /t"

    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]

    if any(d in command for d in dangerous):
        return "Error: Dangerous command."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            timeout=120,
        )
        out = decode_subprocess_output(
            (result.stdout or b"") + (result.stderr or b"")
        ).strip()
        return out[:50000] if out else "（无输出）"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except Exception as e:
        return f"Error: {e}"


def read_file_handler(file_path: str, limit: int = 50000) -> str:
    """读取文件内容
    Args:
        file_path: 文件路径
        limit: 限制输出长度
    Returns:
        str: 文件内容
    """
    try:
        lines = safe_path(file_path).read_text(encoding=TEXT_ENCODING).splitlines()

        if len(lines) > limit:
            lines = lines[:limit] + ["..."]

        return "\n".join(lines)

    except Exception as e:
        return f"Error: {e}"


def write_file_handler(file_path: str, content: str) -> str:
    """写入文件内容

    Args:
        file_path: 文件路径
        content: 文件内容
    Returns:
        str: 文件内容
    """
    try:
        file_path = safe_path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding=TEXT_ENCODING)
        return f"已写入 {len(content)} 字节到 {file_path}"

    except Exception as e:
        return f"Error: {e}"


def edit_file_handler(file_path: str, old_text: str, new_text: str) -> str:
    """编辑文件内容
    Args:
        file_path: 文件路径
        content: 文件内容
    Returns:
        str: 文件内容
    """
    try:
        file_path = safe_path(file_path)
        text = file_path.read_text()
        if old_text not in text:
            return f"错误：在 {file_path} 中未找到指定文本"
        file_path.write_text(
            text.replace(old_text, new_text, 1), encoding=TEXT_ENCODING
        )
        return f'已编辑 {file_path}，替换文本："{old_text}" -> "{new_text}"'

    except Exception as e:
        return f"Error: {e}"


def glob_file_handler(pattern: str) -> str:
    """
    根据模式匹配文件
    Args:
        pattern: 模式
    Returns:
        str: 文件路径
    """
    try:
        results = []
        for match in g.glob(pattern, root_dir=WORKING_DIR):
            if (WORKING_DIR / match).resolve().is_relative_to(WORKING_DIR):
                results.append(match)
        return "\n".join(results) if results else "（无匹配）"

    except Exception as e:
        return f"Error: {e}"


TOOL_HANDLERS = {
    "bash": bash_handler,
    "read_file": read_file_handler,
    "write_file": write_file_handler,
    "edit_file": edit_file_handler,
    "glob_file": glob_file_handler,
}
