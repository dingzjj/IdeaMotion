"""OrchestratorAgent — coordinates generation → review → revise loop."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from .base import BaseAgent
from .generation_agent import VideoGenerationAgent
from .review_agent import VideoReviewAgent
from orchestrator.schemas import Storyboard, StoryboardReview

_STORYBOARD_PATH = Path(__file__).parent.parent / "video" / "public" / "storyboard.json"


def _load_existing_storyboard() -> Optional[Storyboard]:
    """Load the most recently generated storyboard, if any."""
    if not _STORYBOARD_PATH.exists():
        return None
    try:
        data = json.loads(_STORYBOARD_PATH.read_text(encoding="utf-8"))
        return Storyboard.model_validate(data)
    except Exception:
        return None


class OrchestratorAgent(BaseAgent):
    name = "OrchestratorAgent"
    MAX_ITERATIONS = 3

    def run(
        self,
        concept: str,
        dry_run: bool = False,
        output_path: Optional[Path] = None,
        max_iterations: int = MAX_ITERATIONS,
        suggestion: Optional[str] = None,
    ) -> dict:
        """
        Run the full generate → review → revise loop.

        Returns:
            {
                "approved": bool,
                "iterations": int,
                "final_storyboard": Storyboard,
                "final_review": StoryboardReview,
                "output_path": Path | None,
                "history": list[dict],          # per-iteration log entries
            }
        """
        generator = VideoGenerationAgent()
        reviewer  = VideoReviewAgent()

        history: list[dict] = []
        revision_instructions: Optional[str] = None
        last_storyboard: Optional[Storyboard] = None
        last_review: Optional[StoryboardReview] = None
        storyboard_path: Optional[Path] = None

        # In suggestion mode, seed the first iteration with the existing storyboard
        existing_storyboard: Optional[Storyboard] = None
        if suggestion:
            existing_storyboard = _load_existing_storyboard()
            if existing_storyboard is None:
                self.log("⚠️  No existing storyboard found — generating from scratch with suggestion as context")

        self.log(f"Starting pipeline — max {max_iterations} iteration(s)")
        self.log(f"Concept: {concept!r}")
        if suggestion:
            self.log(f"Suggestion: {suggestion!r}")
        print()

        for iteration in range(1, max_iterations + 1):
            print(f"{'─'*60}")
            print(f"  Iteration {iteration}/{max_iterations}")
            print(f"{'─'*60}")

            # ── Generate ──────────────────────────────────────────────────────
            # suggestion + existing_storyboard only apply on the first iteration;
            # subsequent iterations are driven by auto-review revision_instructions.
            gen_result = generator.run(
                concept=concept,
                revision_instructions=revision_instructions,
                suggestion=suggestion if iteration == 1 else None,
                existing_storyboard=existing_storyboard if iteration == 1 else None,
                dry_run=True,           # never render during the review loop
                output_path=None,
                iteration=iteration,
            )
            storyboard: Storyboard = gen_result["storyboard"]
            storyboard_path = gen_result["storyboard_path"]
            last_storyboard = storyboard
            print()

            # ── Review ───────────────────────────────────────────────────────
            review_result = reviewer.run(storyboard=storyboard)
            review: StoryboardReview = review_result["review"]
            last_review = review
            print()

            # ── Log iteration ─────────────────────────────────────────────────
            entry = {
                "iteration": iteration,
                "title": storyboard.title,
                "scenes": len(storyboard.scenes),
                "duration_s": storyboard.total_duration_seconds,
                "average_score": review.average_score,
                "approved": review.approved,
                "issues_count": len(review.issues),
                "review_summary": review_result["summary"],
            }
            history.append(entry)

            if review.approved:
                self.log(f"Storyboard approved at iteration {iteration}!")
                break

            if iteration < max_iterations:
                self.log(f"Will revise — applying review feedback to next iteration")
                revision_instructions = review.revision_instructions
            else:
                self.log(
                    f"Max iterations ({max_iterations}) reached. "
                    f"Proceeding with best available storyboard."
                )

        print()
        print(f"{'─'*60}")

        # ── Final render (once, outside the loop) ────────────────────────────
        final_output: Optional[Path] = None
        if not dry_run and last_storyboard is not None and storyboard_path is not None:
            if output_path is None:
                safe = last_storyboard.title[:40].replace(" ", "_").replace("/", "_")
                from orchestrator.renderer import render_video
                from pathlib import Path as P
                output_path = P(__file__).parent.parent / "workspace" / "output" / f"{safe}.mp4"
            self.log(f"Rendering final video → {output_path}")
            from orchestrator.renderer import render_video
            render_video(storyboard_path, output_path)
            final_output = output_path
        elif dry_run:
            self.log("Dry-run: skipping final render")

        return {
            "approved": last_review.approved if last_review else False,
            "iterations": len(history),
            "final_storyboard": last_storyboard,
            "final_review": last_review,
            "output_path": final_output,
            "history": history,
        }
