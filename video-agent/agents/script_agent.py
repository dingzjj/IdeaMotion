"""ScriptAgent — generate + review storyboard, write artifacts into the task folder."""

from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Optional

from .base import BaseAgent
from .review_agent import VideoReviewAgent
from orchestrator.claude_client import generate_storyboard
from orchestrator.asset_retriever import fetch_all_images
from orchestrator.schemas import Storyboard, StoryboardReview
from orchestrator.task_manager import Task, update_stage, mark_stale_from

WORKSPACE = Path(__file__).parent.parent / "workspace"


class ScriptAgent(BaseAgent):
    name = "ScriptAgent"

    def run(
        self,
        task: Task,
        suggestion: Optional[str] = None,
        max_iterations: int = 3,
        no_review: bool = False,
    ) -> dict:
        """
        Generate (or refine) a storyboard for the task concept and iterate until approved.

        Args:
            task:            Active Task object — artifacts are written to task.folder.
            suggestion:      User refinement hint applied to the existing storyboard
                             on the first iteration. Loads task.storyboard_path if present.
            max_iterations:  Maximum generate→review cycles.
            no_review:       Skip the review loop; generate exactly once.

        Returns:
            {
                "storyboard":      Storyboard,
                "storyboard_path": Path,
                "approved":        bool,
                "iterations":      int,
                "history":         list[dict],
            }
        """
        reviewer = VideoReviewAgent() if not no_review else None
        update_stage(task, "script", "running")

        # Seed suggestion mode with the task's current storyboard (if any)
        existing: Optional[Storyboard] = None
        if suggestion and task.storyboard_path.exists():
            try:
                existing = Storyboard.model_validate(
                    json.loads(task.storyboard_path.read_text(encoding="utf-8"))
                )
            except Exception:
                pass
        if suggestion and existing is None:
            self.log("⚠️  No existing storyboard in task — generating from scratch")

        history: list[dict] = []
        revision_instructions: Optional[str] = None
        last_storyboard: Optional[Storyboard] = None
        approved = False

        for iteration in range(1, max_iterations + 1):
            print(f"{'─'*60}")
            print(f"  Iteration {iteration}/{max_iterations}")
            print(f"{'─'*60}")

            # ── Generate ──────────────────────────────────────────────────
            storyboard = generate_storyboard(
                task.concept,
                revision_instructions=revision_instructions,
                suggestion=suggestion if iteration == 1 else None,
                existing_storyboard=existing if iteration == 1 else None,
            )
            last_storyboard = storyboard
            self.log(
                f"Storyboard: '{storyboard.title}' — "
                f"{len(storyboard.scenes)} scenes, {storyboard.total_duration_seconds:.0f}s"
            )

            # ── Fetch assets ───────────────────────────────────────────────
            assets_cache = WORKSPACE / "assets"
            task_assets  = task.folder / "assets"
            task_assets.mkdir(parents=True, exist_ok=True)

            # Also keep assets accessible from video/public/assets for Remotion
            from orchestrator.task_manager import VIDEO_PUBLIC
            pub_assets = VIDEO_PUBLIC / "assets"
            pub_assets.mkdir(parents=True, exist_ok=True)

            image_map = fetch_all_images(storyboard.scenes, assets_cache)
            self.log(f"Assets: {len(image_map)} images fetched")

            for scene in storyboard.scenes:
                if scene.id in image_map:
                    src = Path(image_map[scene.id])
                    # Copy to task folder
                    dst_task = task_assets / src.name
                    shutil.copy2(src, dst_task)
                    # Copy to video/public so Remotion can serve it
                    shutil.copy2(src, pub_assets / src.name)
                    scene.asset_path = f"assets/{src.name}"

            # ── Write storyboard.json ──────────────────────────────────────
            storyboard_data = json.loads(storyboard.model_dump_json(by_alias=True))

            task.storyboard_path.write_text(
                json.dumps(storyboard_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            task.iter_storyboard_path(iteration).write_text(
                json.dumps(storyboard_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            # Keep video/public/storyboard.json in sync for Remotion
            task.sync_to_public()
            self.log(f"Storyboard written → {task.storyboard_path}")
            print()

            # ── Review (unless skipped) ────────────────────────────────────
            if no_review or reviewer is None:
                approved = True
                break

            review_result = reviewer.run(storyboard=storyboard)
            review: StoryboardReview = review_result["review"]
            print()

            history.append({
                "iteration":     iteration,
                "title":         storyboard.title,
                "scenes":        len(storyboard.scenes),
                "duration_s":    storyboard.total_duration_seconds,
                "average_score": review.average_score,
                "approved":      review.approved,
                "issues_count":  len(review.issues),
            })

            if review.approved:
                approved = True
                self.log(f"Storyboard approved at iteration {iteration}!")
                break

            if iteration < max_iterations:
                self.log("Will revise — applying review feedback")
                revision_instructions = review.revision_instructions
            else:
                self.log("Max iterations reached. Using best available storyboard.")

        # ── Persist result ─────────────────────────────────────────────────
        score = history[-1]["average_score"] if history else None
        update_stage(task, "script", "completed",
                     approved=approved,
                     iterations=len(history) or 1,
                     score=score,
                     scenes=len(last_storyboard.scenes) if last_storyboard else 0)
        # Downstream stages are now potentially stale
        if suggestion:
            mark_stale_from(task, "script")

        return {
            "storyboard":      last_storyboard,
            "storyboard_path": task.storyboard_path,
            "approved":        approved,
            "iterations":      len(history) or 1,
            "history":         history,
        }
