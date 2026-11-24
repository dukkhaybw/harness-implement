from config import WORKING_DIR
from skills import SKILL_REGISTRY

PROMPT_SECTIONS = {
    # 'identity'键对应一个多行字符串，作为智能体的系统身份提示
    "identity": (
        f"你是一个编程 Agent。直接行动，不要解释。"
        f"你将在 Windows cmd 环境下执行任务。使用 cmd 命令完成任务。"
        f"所有破坏性操作需要用户批准。"
        f"针对复杂的需要多个步骤完成的任务，请先使用工具todo_write生成待办事项列表，然后根据待办事项列表完成任务。"
        f"遇到复杂子问题时，使用 spawn_subagent 工具派生子Agent。"
        f"上下文过长时可使用 compact 工具。"
    ),
    "workspace": f"工作目录: {WORKING_DIR}",
    "skill": "需要完整技术说明时，使用 load_skill 加载相关文档。",
}


def _skills_text() -> str:
    if not SKILL_REGISTRY:
        return ""

    return "\n".join(
        f"- **{s['name']}**: {s['description']}" for s in SKILL_REGISTRY.values()
    )


def _assemble_system_prompt(skills: str) -> str:
    sections = [PROMPT_SECTIONS["identity"], PROMPT_SECTIONS["workspace"]]
    if skills:
        sections.append(PROMPT_SECTIONS["skill"])
        sections.append(f"可用的技能:\n {skills}")
    return "\n\n".join(sections)


def get_system_prompt() -> str:
    # 内部调用技能文本拼接及总装配函数
    return _assemble_system_prompt(_skills_text())


SUB_SYSTEM = {
    "identity": (
        f"你是一个位于{WORKING_DIR}目录下的编程 Agent。直接行动，不要解释。"
        f"你将在 Windows cmd 环境下执行任务。使用 cmd 命令完成任务。"
        f"所有破坏性操作需要用户批准。"
        f"针对复杂的需要多个步骤完成的任务，请先使用工具todo_write生成待办事项列表，然后根据待办事项列表完成任务。"
        f"完成分配给你的任务，然后返回简洁摘要。不要继续委派。"
    )
}
