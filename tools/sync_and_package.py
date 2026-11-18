#!/usr/bin/env python3
"""Keep shared files in sync across the skills, then build one zip per skill in dist/.

The full planner (skills/gtm-plan-2027) holds the source copy of every shared
reference, template, and script. Edit them there, then run:

    python tools/sync_and_package.py

Each skill must be self-contained so it can be uploaded to Claude on its own,
which is why shared files are copied instead of linked.
"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "skills" / "gtm-plan-2027"
DIST = ROOT / "dist"

SHARED = {
    "pipeline-model": [
        "references/capacity-and-pipeline.md",
        "references/benchmarks.md",
        "references/sources.md",
        "templates/inputs.json",
        "templates/inputs.md",
        "scripts/build_model.py",
    ],
    "board-red-team": [
        "references/board-questions.md",
        "references/kellogg-planning.md",
        "references/ai-era-assumptions.md",
        "references/tensions.md",
        "references/capacity-and-pipeline.md",
        "references/sources.md",
    ],
    "budget-demand-audit": [
        "references/demand-system.md",
        "references/plan-approval.md",
        "references/kellogg-planning.md",
        "references/benchmarks.md",
        "references/tensions.md",
        "references/ai-era-assumptions.md",
        "references/board-questions.md",
        "references/capacity-and-pipeline.md",
        "references/sources.md",
    ],
    "ai-assumptions-check": [
        "references/ai-era-assumptions.md",
        "references/tensions.md",
        "references/sources.md",
    ],
}


def sync():
    for skill, files in SHARED.items():
        for rel in files:
            dst = ROOT / "skills" / skill / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SRC / rel, dst)
        print(f"synced {skill}: {len(files)} files")


def package():
    DIST.mkdir(exist_ok=True)
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not (skill_dir / "SKILL.md").exists():
            continue
        out = DIST / f"{skill_dir.name}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(skill_dir.rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts:
                    zf.write(f, Path(skill_dir.name) / f.relative_to(skill_dir))
        print(f"packaged {out.relative_to(ROOT)}")


if __name__ == "__main__":
    sync()
    package()
