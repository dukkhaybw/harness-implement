PROMPT_SECTIONS = {
    # 'identity'键对应一个多行字符串，作为智能体的系统身份提示
    "identity": (
        f"你是一个编程 Agent。直接行动，不要解释。"
        f"你将在 Windows cmd 环境下执行任务。使用 cmd 命令完成任务。"
    )
}


def get_system_prompt() -> str:
    return PROMPT_SECTIONS["identity"]
