"""VideoRenderAgent — render storyboard → MP4 via Remotion, optionally mix voiceover."""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from .base import BaseAgent
from orchestrator.renderer import render_video
from orchestrator import tts_client
from orchestrator.task_manager import Task, update_stage


class VideoRenderAgent(BaseAgent):
    name = "VideoRenderAgent"

    def run(
        self,
        task: Task,
        merge_audio: bool = True,
    ) -> dict:
        """
        Render the task's storyboard to MP4, then merge voiceover if available.

        The storyboard must already be synced to video/public/ (ScriptAgent does this).
        Audio is read from task.merged_audio_path when merge_audio=True and the file exists.

        Returns:
            {
                "output_path":  Path,   # final MP4 (with or without audio)
                "audio_merged": bool,
            }
        """
        if not task.storyboard_path.exists():
            raise FileNotFoundError(
                f"No storyboard in task folder {task.folder}. Run `script` first."
            )

        update_stage(task, "video", "running")

        # Ensure Remotion is reading the right storyboard
        task.sync_to_public()

        has_audio = merge_audio and task.merged_audio_path.exists()
        silent_path = task.folder / "_video_silent.mp4" if has_audio else task.video_path

        # ── Remotion render ────────────────────────────────────────────────
        self.log(f"Rendering → {task.video_path.name}")
        render_video(task.storyboard_path, silent_path)

        # ── Mix audio ──────────────────────────────────────────────────────
        audio_merged = False
        if has_audio:
            self.log(f"Merging voiceover → {task.video_path.name}")
            ok = tts_client.merge_audio_into_video(
                silent_path, task.merged_audio_path, task.video_path
            )
            if ok:
                audio_merged = True
                silent_path.unlink(missing_ok=True)
                size_mb = task.video_path.stat().st_size / 1_048_576
                self.log(f"Final video (with audio) → {task.video_path} ({size_mb:.1f} MB)")
            else:
                self.log("Audio merge failed — delivering silent video")
                silent_path.rename(task.video_path)
        else:
            size_mb = task.video_path.stat().st_size / 1_048_576
            self.log(f"Final video (silent) → {task.video_path} ({size_mb:.1f} MB)")

        update_stage(task, "video", "completed", audio_merged=audio_merged)

        return {
            "output_path":  task.video_path,
            "audio_merged": audio_merged,
        }
