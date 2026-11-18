from config import WORKING_DIR
from typing import Callable

HOOKS = {"UserPromptSubmit": [], "PreToolUse": [], "PostToolUse": [], "Stop": []}

DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]

DESTRUCTIVE = ["rm ", "> /etc/", "chmod 777", "del ", "erase "]


def register_hook(event: str, callback: Callable):
    HOOKS[event].append(callback)


def workspace_inject_hook(query: str) -> str | None:
    print(f"\x1b[90m[HOOK] UserPromptSubmit：注入工作目录 {WORKING_DIR}\x1b[0m")
    return f"<workspace>\n当前工作目录：{WORKING_DIR}\n</workspace>\n\n{query}"


def permission_hook(tool_name: str, args: dict):
    if tool_name == "bash":
        for pattern in DENY_LIST:
            if pattern in args.get("command", ""):
                print(f"\n\x1b[31m⛔ 已拦截：'{pattern}'\x1b[0m")
                return "禁止列表拒绝权限"

    for kw in DESTRUCTIVE:
        if kw in args.get("command", ""):
            print(f"\n\x1b[33m⚠  可能破坏性的命令\x1b[0m")
            print(f"   工具: {tool_name}({args})")
            choice = input("   允许？[y/N] ").strip().lower()
            if choice not in ("y", "yes"):
                return "用户拒绝权限"

    if tool_name in ("write_file", "edit_file"):
        path = args.get("path", "")
        if not (WORKING_DIR / path).resolve().is_relative_to(WORKING_DIR):
            print(f"\n\x1b[33m⚠  在工作区外写入\x1b[0m")
            print(f"   工具: {tool_name}({args})")
            choice = input("   允许？[y/N] ").strip().lower()
            if choice not in ("y", "yes"):
                return "用户拒绝权限"

    return None


def log_hook(event: str, args: dict):
    args_preview = str(list(args.values())[:2])
    print(f"\x1b[90m[LOG HOOK] {event}({args_preview})\x1b[0m")
    return None


def large_output_hook(name: str, args: dict, output: str):
    if len(str(output)) > 1000:
        print(f"\x1b[33m[HOOK] ⚠ {name} 输出过大：{len(str(output))} 字符\x1b[0m")
    return None


def summary_hook(messages: list):
    tool_count = sum(1 for msg in messages if msg.get("role") == "tool")
    print(f"\x1b[90m[HOOK] Stop：本次会话共使用 {tool_count} 次工具调用\x1b[0m")
    return None


register_hook("UserPromptSubmit", workspace_inject_hook)
register_hook("PreToolUse", permission_hook)
register_hook("PreToolUse", log_hook)
register_hook("PostToolUse", large_output_hook)
register_hook("Stop", summary_hook)


def trigger_user_prompt_hooks(query: str) -> str:
    current = query
    for callback in HOOKS["UserPromptSubmit"]:
        result = callback(current)
        if isinstance(result, str):
            current = result
    return current


def trigger_hooks(event: str, *args):
    for callback in HOOKS[event]:
        result = callback(*args)
        if result is not None:
            return result
    return None
