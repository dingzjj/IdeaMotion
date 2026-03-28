"""Invoke Remotion CLI to render the video."""

from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

VIDEO_DIR = Path(__file__).parent.parent / "video"
CHROMIUM = "/usr/bin/chromium-browser"


def render_video(
    storyboard_path: Path,
    output_path: Path,
    dry_run: bool = False,
) -> None:
    """Call `npx remotion render` to produce the MP4."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read metadata from storyboard for logging only
    storyboard = json.loads(storyboard_path.read_text())
    fps = storyboard.get("fps", 30)
    total_seconds = storyboard.get("total_duration_seconds", 60)
    n_scenes = len(storyboard.get("scenes", []))
    transition_reduction = max(0, n_scenes - 1) * 15  # 15-frame fade between scenes
    effective_frames = round(total_seconds * fps) - transition_reduction

    # No --frames flag: let calculateMetadata in Root.tsx control the exact duration
    cmd = [
        "npx", "remotion", "render",
        "KnowledgeVideo",
        str(output_path),
        f"--browser-executable={CHROMIUM}",
        "--chromium-flags=--no-sandbox",
        "--concurrency=2",
    ]

    print(f"  Total: {effective_frames} frames ({total_seconds:.0f}s @ {fps}fps, {n_scenes} scenes)", flush=True)
    print(f"  Output: {output_path}", flush=True)

    if dry_run:
        print("  [dry-run] Skipping actual render.", flush=True)
        return

    result = subprocess.run(cmd, cwd=VIDEO_DIR, stdout=sys.stdout, stderr=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Remotion render failed (exit code {result.returncode})")
