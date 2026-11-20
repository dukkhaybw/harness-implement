from config import SKILLS_DIR, TEXT_ENCODING
from utils import parse_frontmatter

SKILL_REGISTRY: dict[str, dict] = {}


def _scan_skills():
    if not SKILLS_DIR.exists():
        return

    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue

        manifest = d / "SKILL.md"

        if not manifest.exists():
            continue

        raw = manifest.read_text(encoding=TEXT_ENCODING, errors="replace")

        meta, content = parse_frontmatter(raw)

        name = meta.get("name", d.name)
        desc = meta.get("description", raw.split("\n")[0].lstrip("#").strip())

        SKILL_REGISTRY[name] = {
            "name": name,
            "description": desc,
            "content": raw,
        }


def load_skill(name: str) -> str:
    skill = SKILL_REGISTRY.get(name)
    if not skill:
        return f"未找到技能：{name}"
    # 在控制台打印加载提示（带颜色）
    print(f"\x1b[90m[技能] 已加载 {name}\x1b[0m")
    # 返回技能内容
    return skill["content"]


_scan_skills()
