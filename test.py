import os
import glob as globlib
from pathlib import Path

# 工作区根目录
WORKDIR = Path.cwd()
TEXT_ENCODING = "utf-8"

def safe_path(path: str) -> str:
    """把 path 解析到 WORKDIR 内，越界则抛 ValueError。"""
    path = (WORKDIR / path).resolve()

    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"路径超出工作区：{path}")

    return path

# 工具 Schema 列表
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文件的内容",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "按 glob 模式查找文件",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        },
    }
    # TODO: 新增 read_file 工具描述
    # TODO: 新增 glob 工具描述
]

# 工具处理函数
def handle_read_file(file_path: str, limit: int|None) -> str:
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

def handle_glob(pattern: str) -> str:
    """
    根据模式匹配文件
    Args:
        pattern: 模式
    Returns:
        str: 文件路径
    """
    try:
        results = []
        for match in globlib.glob(pattern, root_dir=WORKDIR):
            if (WORKDIR / match).resolve().is_relative_to(WORKDIR):
                results.append(match)
        return "\n".join(results) if results else "（无匹配）"

    except Exception as e:
        return f"Error: {e}"

TOOL_HANDLERS = {
    "bash": lambda args: "(bash 实现略)",
    "read_file": handle_read_file,
    "glob": handle_glob
}

def execute_tool(name: str, args: dict):
    """查表分发，保持结构不变"""
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return f"未知工具: {name}"
    try:
        return handler(args)
    except Exception as e:
        return f"工具执行失败: {e}"

def agent_loop(...):
    """s01 的循环骨架，不用改动"""
    # while True:
    #   response = model(...)
    #   for tool_call in response.tool_calls:
    #       result = execute_tool(tool_call.name, tool_call.args)
    #   ...
    raise NotImplementedError