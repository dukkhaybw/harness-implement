from config import WORKING_DIR

DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]

DESTRUCTIVE = ["rm ", "> /etc/", "chmod 777", "del ", "erase "]


def check_permission(tool_name: str, args: dict):

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
