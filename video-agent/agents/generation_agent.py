"""VideoGenerationAgent — storyboard → assets → render."""

from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Optional

from .base import BaseAgent
from orchestrator.claude_client import generate_storyboard
from orchestrator.asset_retriever import fetch_all_images
from orchestrator.renderer import render_video
from orchestrator.schemas import Storyboard

VIDEO_PUBLIC = Path(__file__).parent.parent / "video" / "public"
WORKSPACE    = Path(__file__).parent.parent / "workspace"


class VideoGenerationAgent(BaseAgent):
    name = "VideoGenerationAgent"

    def run(
        self,
        concept: str,
        revision_instructions: Optional[str] = None,
        suggestion: Optional[str] = None,
        existing_storyboard: Optional[Storyboard] = None,
        dry_run: bool = False,
        output_path: Optional[Path] = None,
        iteration: int = 1,
    ) -> dict:
        """
        Generate (or revise) a video storyboard and optionally render it.

        Returns:
            {
                "storyboard": Storyboard,
                "storyboard_path": Path,   # video/public/storyboard.json
                "output_path": Path | None,  # None if dry_run=True
            }
        """
        if suggestion and existing_storyboard:
            mode = f"refining with suggestion: {suggestion!r}"
        elif revision_instructions:
            mode = "revising (auto-review feedback)"
        else:
            mode = "generating"
        self.log(f"Iteration {iteration} — {mode}")

        # ── 1. Generate storyboard ────────────────────────────────────────────
        storyboard = generate_storyboard(
            concept,
            revision_instructions=revision_instructions,
            suggestion=suggestion,
            existing_storyboard=existing_storyboard,
        )
        self.log(f"Storyboard: '{storyboard.title}' — {len(storyboard.scenes)} scenes, "
                 f"{storyboard.total_duration_seconds:.0f}s")

        # ── 2. Fetch images ───────────────────────────────────────────────────
        assets_dir = WORKSPACE / "assets"
        pub_assets = VIDEO_PUBLIC / "assets"
        pub_assets.mkdir(parents=True, exist_ok=True)

        image_map = fetch_all_images(storyboard.scenes, assets_dir)
        self.log(f"Assets: {len(image_map)} images fetched")

        for scene in storyboard.scenes:
            if scene.id in image_map:
                src = Path(image_map[scene.id])
                dst = pub_assets / src.name
                shutil.copy2(src, dst)
                scene.asset_path = f"assets/{src.name}"

        # ── 3. Write storyboard.json ──────────────────────────────────────────
        VIDEO_PUBLIC.mkdir(parents=True, exist_ok=True)
        storyboard_data = json.loads(storyboard.model_dump_json(by_alias=True))

        storyboard_path = VIDEO_PUBLIC / "storyboard.json"
        storyboard_path.write_text(
            json.dumps(storyboard_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Save per-iteration copy for debugging
        iter_path = WORKSPACE / f"storyboard_iter_{iteration}.json"
        iter_path.parent.mkdir(parents=True, exist_ok=True)
        iter_path.write_text(
            json.dumps(storyboard_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.log(f"Storyboard written → {storyboard_path}")

        # ── 4. Render (if not dry_run) ────────────────────────────────────────
        final_output = None
        if not dry_run:
            if output_path is None:
                safe = storyboard.title[:40].replace(" ", "_").replace("/", "_")
                output_path = WORKSPACE / "output" / f"{safe}.mp4"
            render_video(storyboard_path, output_path)
            final_output = output_path
            self.log(f"Video rendered → {final_output}")

        return {
            "storyboard": storyboard,
            "storyboard_path": storyboard_path,
            "output_path": final_output,
        }
