"""VoiceoverAgent — generate narration via LLM + synthesize audio via edge-tts."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from .base import BaseAgent
from orchestrator.claude_client import generate_voiceover_script, refine_voiceover_script
from orchestrator.schemas import Storyboard, VoiceoverScript
from orchestrator import tts_client
from orchestrator.task_manager import Task, update_stage, mark_stale_from


class VoiceoverAgent(BaseAgent):
    name = "VoiceoverAgent"

    def run(
        self,
        task: Task,
        suggestion: Optional[str] = None,
    ) -> dict:
        """
        Generate per-scene MP3 audio from the task's storyboard.

        When *suggestion* is provided and a voiceover script already exists in
        the task folder, the LLM refines the existing narration before re-synthesizing.

        Returns:
            {
                "voiceover_script": VoiceoverScript | None,
                "audio_files":      list[Path],
                "merged_path":      Path | None,
                "success":          bool,
            }
        """
        if not tts_client.is_available():
            self.log("edge-tts not installed — run: pip install edge-tts")
            return {"voiceover_script": None, "audio_files": [], "merged_path": None, "success": False}

        update_stage(task, "voiceover", "running")

        # ── 1. Load storyboard ─────────────────────────────────────────────
        if not task.storyboard_path.exists():
            self.log(f"No storyboard found in task folder. Run `script` first.")
            update_stage(task, "voiceover", "failed", error="no storyboard")
            return {"voiceover_script": None, "audio_files": [], "merged_path": None, "success": False}

        storyboard = Storyboard.model_validate(
            json.loads(task.storyboard_path.read_text(encoding="utf-8"))
        )
        self.log(f"Loaded storyboard: '{storyboard.title}' ({len(storyboard.scenes)} scenes)")

        # ── 2. Generate / refine narration script ──────────────────────────
        existing_script: Optional[VoiceoverScript] = None
        if suggestion and task.voiceover_script_path.exists():
            try:
                existing_script = VoiceoverScript.model_validate(
                    json.loads(task.voiceover_script_path.read_text(encoding="utf-8"))
                )
                self.log(f"Refining existing voiceover with suggestion: {suggestion!r}")
            except Exception:
                pass

        if existing_script and suggestion:
            voiceover_script = refine_voiceover_script(storyboard, existing_script, suggestion)
        else:
            voiceover_script = generate_voiceover_script(storyboard)

        narration_map = {n.scene_id: n.text for n in voiceover_script.scenes}
        self.log(f"Narration ready: {len(voiceover_script.scenes)} scenes, lang={voiceover_script.language}")

        # Save narration script to task folder
        task.voiceover_script_path.write_text(
            json.dumps(voiceover_script.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # ── 3. Synthesize per-scene audio ──────────────────────────────────
        audio_files: list[Path] = []
        for scene in storyboard.scenes:
            text = narration_map.get(scene.id, "")
            if not text.strip():
                self.log(f"  [{scene.id}] No narration — skipping")
                continue

            mp3_path = task.scene_audio_path(scene.id)
            preview = text[:50] + ("…" if len(text) > 50 else "")
            self.log(f"  [{scene.id}] {preview}")

            if tts_client.synthesize_scene(text, mp3_path, voiceover_script.language):
                audio_files.append(mp3_path)
            else:
                self.log(f"  [{scene.id}] TTS failed — skipping")

        self.log(f"Synthesized {len(audio_files)}/{len(storyboard.scenes)} scenes")

        # ── 4. Merge into single track ─────────────────────────────────────
        merged_path: Optional[Path] = None
        if audio_files:
            merged_path = task.merged_audio_path
            if tts_client.merge_audio_files(audio_files, merged_path):
                size_mb = merged_path.stat().st_size / 1_048_576
                self.log(f"Merged audio → {merged_path} ({size_mb:.1f} MB)")
            else:
                self.log("Audio merge failed — per-scene files still available")
                merged_path = None

        success = bool(audio_files)
        update_stage(task, "voiceover", "completed" if success else "failed",
                     scenes_synthesized=len(audio_files))
        if suggestion:
            mark_stale_from(task, "voiceover")

        return {
            "voiceover_script": voiceover_script,
            "audio_files":      audio_files,
            "merged_path":      merged_path,
            "success":          success,
        }
