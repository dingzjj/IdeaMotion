"""Task management — tracks every video generation task in workspace/task.json.

Layout
------
workspace/
├── task.json                   ← registry: current task + all task metadata
└── tasks/
    └── task_YYYYMMDD_HHMMSS/
        ├── storyboard.json
        ├── storyboard_iter_N.json
        ├── voiceover_script.json
        ├── audio/
        │   ├── <scene_id>.mp3
        │   └── voiceover.mp3
        └── video.mp4
"""

from __future__ import annotations
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

_ROOT       = Path(__file__).parent.parent
WORKSPACE   = _ROOT / "workspace"
VIDEO_PUBLIC = _ROOT / "video" / "public"
TASK_JSON   = WORKSPACE / "task.json"
TASKS_DIR   = WORKSPACE / "tasks"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _new_id() -> str:
    return datetime.now().strftime("task_%Y%m%d_%H%M%S")


def _load() -> dict:
    if TASK_JSON.exists():
        return json.loads(TASK_JSON.read_text(encoding="utf-8"))
    return {"current": None, "tasks": {}}


def _save(registry: dict) -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    TASK_JSON.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── Task class ────────────────────────────────────────────────────────────────

class Task:
    """Represents a single video generation task and its artifact paths."""

    def __init__(self, data: dict) -> None:
        self.id: str       = data["id"]
        self.concept: str  = data["concept"]
        self.created_at: str = data.get("created_at", "")
        self.stages: dict  = data.get("stages", {})
        self.folder: Path  = TASKS_DIR / self.id
        self.folder.mkdir(parents=True, exist_ok=True)

    # ── Artifact paths ────────────────────────────────────────────────────────

    @property
    def storyboard_path(self) -> Path:
        return self.folder / "storyboard.json"

    def iter_storyboard_path(self, n: int) -> Path:
        return self.folder / f"storyboard_iter_{n}.json"

    @property
    def voiceover_script_path(self) -> Path:
        return self.folder / "voiceover_script.json"

    @property
    def audio_dir(self) -> Path:
        d = self.folder / "audio"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def scene_audio_path(self, scene_id: str) -> Path:
        return self.audio_dir / f"{scene_id}.mp3"

    @property
    def merged_audio_path(self) -> Path:
        return self.audio_dir / "voiceover.mp3"

    @property
    def video_path(self) -> Path:
        return self.folder / "video.mp4"

    # ── Remotion sync ─────────────────────────────────────────────────────────

    def sync_to_public(self) -> None:
        """Copy storyboard into video/public/ so Remotion can read it."""
        if self.storyboard_path.exists():
            VIDEO_PUBLIC.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.storyboard_path, VIDEO_PUBLIC / "storyboard.json")

    # ── Convenience ───────────────────────────────────────────────────────────

    def stage_status(self, stage: str) -> str:
        return self.stages.get(stage, {}).get("status", "pending")

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, concept={self.concept!r})"


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_task(concept: str) -> Task:
    """Create a new task, register it, and set it as current."""
    registry = _load()
    tid = _new_id()
    data: dict = {
        "id":         tid,
        "concept":    concept,
        "created_at": _now(),
        "updated_at": _now(),
        "stages": {
            "script":    {"status": "pending"},
            "voiceover": {"status": "pending"},
            "video":     {"status": "pending"},
        },
    }
    registry["tasks"][tid] = data
    registry["current"] = tid
    _save(registry)
    return Task(data)


def get_task(task_id: Optional[str] = None) -> Optional[Task]:
    """Return a Task by ID, or the current task when task_id is None."""
    registry = _load()
    tid = task_id or registry.get("current")
    if not tid:
        return None
    data = registry["tasks"].get(tid)
    return Task(data) if data else None


def update_stage(task: Task, stage: str, status: str, **meta) -> None:
    """Persist stage status + extra metadata into task.json."""
    registry = _load()
    if task.id not in registry["tasks"]:
        return
    entry = registry["tasks"][task.id]["stages"].setdefault(stage, {})
    entry["status"] = status
    if status == "completed":
        entry["completed_at"] = _now()
    entry.update(meta)
    registry["tasks"][task.id]["updated_at"] = _now()
    _save(registry)


def mark_stale_from(task: Task, stage: str) -> None:
    """Mark all stages after *stage* as stale (upstream changed)."""
    ORDER = ["script", "voiceover", "video"]
    registry = _load()
    if task.id not in registry["tasks"]:
        return
    try:
        idx = ORDER.index(stage)
    except ValueError:
        return
    for s in ORDER[idx + 1:]:
        entry = registry["tasks"][task.id]["stages"].setdefault(s, {})
        if entry.get("status") == "completed":
            entry["status"] = "stale"
    registry["tasks"][task.id]["updated_at"] = _now()
    _save(registry)


def list_tasks() -> list[dict]:
    """Return all tasks sorted newest-first."""
    registry = _load()
    current = registry.get("current")
    rows = []
    for tid, data in registry["tasks"].items():
        rows.append({**data, "is_current": tid == current})
    return sorted(rows, key=lambda t: t.get("created_at", ""), reverse=True)
