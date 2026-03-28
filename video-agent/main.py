"""
Knowledge Video Agent — task-based modular pipeline.

Each step runs independently or as a full pipeline.
Every run is tracked as a task under workspace/tasks/.

── Individual steps ────────────────────────────────────────────────────
  python main.py script "人工智能如何改变现代医疗"   # new task, generate storyboard
  python main.py voiceover                           # generate audio for current task
  python main.py video                               # render video for current task

── Refinement with --suggestion ────────────────────────────────────────
  python main.py script    --suggestion "更多图表"   # refine storyboard
  python main.py voiceover --suggestion "语气更活泼" # refine narration + re-synthesize
  python main.py video     --suggestion "画面更动感" # refine script → re-voiceover → re-render

── Full pipeline ────────────────────────────────────────────────────────
  python main.py all "大脑是如何学习的"              # script → voiceover → video
  python main.py all --suggestion "加更多类比"       # refine current task end-to-end
  python main.py "大脑是如何学习的"                  # same as 'all' (backward compat)

── Task management ──────────────────────────────────────────────────────
  python main.py list                                # show all tasks
  python main.py script --task task_20260328_100000 "新概念"  # use specific task slot

── Options ──────────────────────────────────────────────────────────────
  --max-iterations N    max generate→review cycles (default: 3)
  --no-review           skip review agent
  --skip-voiceover      all pipeline without voiceover
  --no-audio            render silent video even if audio exists
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# ── Backward compat: bare concept → 'all' ────────────────────────────────────
_SUBCMDS = {"script", "video", "voiceover", "all", "list"}
if len(sys.argv) > 1 and sys.argv[1] not in _SUBCMDS and not sys.argv[1].startswith("-"):
    sys.argv.insert(1, "all")


# ── Shared argument helpers ───────────────────────────────────────────────────

def _add_task_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("--task", default=None, metavar="TASK_ID",
                   help="Work on a specific task ID (default: current task)")

def _add_suggestion_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("--suggestion", default=None, metavar="TEXT",
                   help="Refine this stage using the given suggestion")

def _add_review_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--max-iterations", type=int, default=3, metavar="N",
                   help="Max generate→review cycles (default: 3)")
    p.add_argument("--no-review", action="store_true",
                   help="Skip review; generate exactly once")


# ── Parser ────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Knowledge Video Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # list
    sub.add_parser("list", help="Show all tasks")

    # script
    sp = sub.add_parser("script", help="Generate/refine storyboard")
    sp.add_argument("concept", nargs="?", default=None,
                    help="Topic (required for new task; optional when --suggestion is used)")
    _add_task_arg(sp); _add_suggestion_arg(sp); _add_review_args(sp)

    # voiceover
    vop = sub.add_parser("voiceover", help="Generate/refine voiceover audio")
    _add_task_arg(vop); _add_suggestion_arg(vop)

    # video
    vp = sub.add_parser("video", help="Render video (auto-mixes voiceover if available)")
    _add_task_arg(vp); _add_suggestion_arg(vp); _add_review_args(vp)
    vp.add_argument("--no-audio", action="store_true",
                    help="Render silent video even if voiceover audio exists")

    # all
    ap = sub.add_parser("all", help="Run full pipeline: script → voiceover → video")
    ap.add_argument("concept", nargs="?", default=None,
                    help="Topic (required for new task; optional when --suggestion is used)")
    _add_task_arg(ap); _add_suggestion_arg(ap); _add_review_args(ap)
    ap.add_argument("--skip-voiceover", action="store_true",
                    help="Skip voiceover; render silent video")
    ap.add_argument("--no-audio", action="store_true",
                    help="Render silent video even if voiceover audio exists")

    return parser


# ── Task resolution helpers ───────────────────────────────────────────────────

def _resolve_task(args, require_concept: bool = False):
    """Return an active Task, creating one if concept is provided."""
    from orchestrator.task_manager import get_task, create_task

    concept = getattr(args, "concept", None)
    task_id = getattr(args, "task", None)
    suggestion = getattr(args, "suggestion", None)

    if task_id:
        task = get_task(task_id)
        if task is None:
            print(f"❌  Task '{task_id}' not found. Run `list` to see available tasks.")
            sys.exit(1)
        return task

    if concept:
        # Always create a fresh task when a concept is given AND no --suggestion
        if suggestion:
            # Refining: try to use current task first
            task = get_task()
            if task and task.concept == concept:
                return task
        return create_task(concept)

    # No concept: use current task
    task = get_task()
    if task is None:
        if require_concept:
            print("❌  No current task. Provide a concept: python main.py script \"Your topic\"")
            sys.exit(1)
        return None
    return task


# ── Command handlers ──────────────────────────────────────────────────────────

def _cmd_list(_args) -> None:
    from orchestrator.task_manager import list_tasks
    tasks = list_tasks()
    if not tasks:
        print("No tasks yet. Run: python main.py all \"Your concept\"")
        return

    print(f"\n{'─'*72}")
    print(f"  {'ID':<26}  {'CONCEPT':<28}  STAGES")
    print(f"{'─'*72}")
    for t in tasks:
        stages = t.get("stages", {})
        def _icon(s): return {"completed": "✅", "stale": "⚠️ ", "failed": "❌", "running": "⏳"}.get(s, "·")
        stage_str = (f"script:{_icon(stages.get('script',{}).get('status',''))} "
                     f"voice:{_icon(stages.get('voiceover',{}).get('status',''))} "
                     f"video:{_icon(stages.get('video',{}).get('status',''))}")
        marker = " ◀ current" if t.get("is_current") else ""
        print(f"  {t['id']:<26}  {t['concept'][:28]:<28}  {stage_str}{marker}")
    print(f"{'─'*72}\n")


def _cmd_script(args) -> None:
    from agents.script_agent import ScriptAgent

    suggestion = args.suggestion
    concept    = args.concept

    if not concept and not suggestion:
        print("❌  Provide a concept or use --suggestion to refine current task.")
        sys.exit(1)

    task = _resolve_task(args, require_concept=not suggestion)
    _print_header("script", task=task, suggestion=suggestion)

    result = ScriptAgent().run(
        task=task,
        suggestion=suggestion,
        max_iterations=args.max_iterations,
        no_review=args.no_review,
    )

    _print_done("SCRIPT", task)
    _print_history(result["history"])
    icon = "✅" if result["approved"] else "⚠️ "
    print(f"\n  Status : {icon} {'Approved' if result['approved'] else 'Best available'}"
          f" ({result['iterations']} iteration(s))")
    print(f"  Output : {result['storyboard_path']}\n")


def _cmd_voiceover(args) -> None:
    from agents.voiceover_agent import VoiceoverAgent

    task = _resolve_task(args, require_concept=False)
    if task is None:
        print("❌  No current task. Run `script` first.")
        sys.exit(1)

    _print_header("voiceover", task=task, suggestion=args.suggestion)
    result = VoiceoverAgent().run(task=task, suggestion=args.suggestion)

    _print_done("VOICEOVER", task)
    if result["success"]:
        print(f"\n  Scenes  : {len(result['audio_files'])} synthesized")
        if result["merged_path"]:
            mb = result["merged_path"].stat().st_size / 1_048_576
            print(f"  Audio   : {result['merged_path']}  ({mb:.1f} MB)")
    else:
        print("\n  ⚠️  Voiceover failed. Check edge-tts installation.")
    print()


def _cmd_video(args) -> None:
    from agents.script_agent import ScriptAgent
    from agents.voiceover_agent import VoiceoverAgent
    from agents.video_render_agent import VideoRenderAgent

    suggestion = args.suggestion
    task = _resolve_task(args, require_concept=bool(suggestion))
    if task is None:
        print("❌  No current task. Run `script` first.")
        sys.exit(1)

    _print_header("video", task=task, suggestion=suggestion)

    # If suggestion given: refine script first, then regenerate voice, then render
    if suggestion:
        print("\n📝  Refining script...")
        print("─" * 60)
        ScriptAgent().run(task=task, suggestion=suggestion,
                          max_iterations=args.max_iterations,
                          no_review=args.no_review)
        print("\n🎙️  Regenerating voiceover...")
        print("─" * 60)
        VoiceoverAgent().run(task=task)

    result = VideoRenderAgent().run(task=task, merge_audio=not args.no_audio)

    _print_done("VIDEO", task)
    out = result["output_path"]
    mb = out.stat().st_size / 1_048_576
    note = " (with voiceover)" if result["audio_merged"] else " (silent)"
    print(f"\n  Video{note}: {out}  ({mb:.1f} MB)\n")


def _cmd_all(args) -> None:
    from agents.script_agent import ScriptAgent
    from agents.voiceover_agent import VoiceoverAgent
    from agents.video_render_agent import VideoRenderAgent

    suggestion = args.suggestion
    concept    = args.concept

    if not concept and not suggestion:
        print("❌  Provide a concept: python main.py all \"Your topic\"")
        sys.exit(1)

    task = _resolve_task(args, require_concept=not suggestion)
    _print_header("all", task=task, suggestion=suggestion,
                  skip_voiceover=args.skip_voiceover)

    # ── 1. Script ──────────────────────────────────────────────────────────
    print("\n📝  STEP 1 / 3 — Script")
    print("─" * 60)
    script_result = ScriptAgent().run(
        task=task,
        suggestion=suggestion,
        max_iterations=args.max_iterations,
        no_review=args.no_review,
    )

    # ── 2. Voiceover ───────────────────────────────────────────────────────
    merged_audio = None
    if not args.skip_voiceover:
        print("\n🎙️  STEP 2 / 3 — Voiceover")
        print("─" * 60)
        vo = VoiceoverAgent().run(task=task)
        merged_audio = vo.get("merged_path")
        if not vo["success"]:
            print("  ⚠️  Voiceover failed — continuing with silent video")
    else:
        print("\n🎙️  STEP 2 / 3 — Voiceover  [skipped]")

    # ── 3. Video ───────────────────────────────────────────────────────────
    print("\n🎬  STEP 3 / 3 — Video")
    print("─" * 60)
    video_result = VideoRenderAgent().run(
        task=task,
        merge_audio=not (args.skip_voiceover or args.no_audio),
    )

    # ── Summary ────────────────────────────────────────────────────────────
    _print_done("PIPELINE", task)
    _print_history(script_result["history"])

    approved = script_result["approved"]
    print(f"\n  Script    : {'✅ Approved' if approved else '⚠️  Best available'}"
          f" ({script_result['iterations']} iteration(s))")

    if not args.skip_voiceover:
        print(f"  Voiceover : {'✅ OK' if merged_audio else '❌ Failed'}")

    out = video_result["output_path"]
    mb = out.stat().st_size / 1_048_576
    note = " (with voiceover)" if video_result["audio_merged"] else " (silent)"
    print(f"  Video{note}: {out}  ({mb:.1f} MB)\n")


# ── Print helpers ─────────────────────────────────────────────────────────────

def _print_header(command: str, task=None, suggestion=None, skip_voiceover=False) -> None:
    print("\n🎬 Knowledge Video Agent")
    print("=" * 60)
    print(f"  Command : {command}")
    if task:
        print(f"  Task    : {task.id}")
        print(f"  Concept : {task.concept!r}")
    if suggestion:
        print(f"  Suggest : {suggestion!r}")
    if command == "all":
        steps = ["script", "video"] if skip_voiceover else ["script", "voiceover", "video"]
        print(f"  Steps   : {' → '.join(steps)}")
    print("=" * 60)
    print()


def _print_done(label: str, task=None) -> None:
    print("\n" + "=" * 60)
    print(f"  {label} COMPLETE")
    print("=" * 60)
    if task:
        from orchestrator.task_manager import TASK_JSON
        print(f"\n  Task registry : {TASK_JSON}")
        print(f"  Task folder   : {task.folder}")


def _print_history(history: list[dict]) -> None:
    if not history:
        return
    print("\n  Iteration history:")
    for h in history:
        icon = "✅" if h["approved"] else "❌"
        print(f"    {icon} Iter {h['iteration']}: score={h['average_score']:.1f}  "
              f"scenes={h['scenes']}  duration={h['duration_s']:.0f}s  "
              f"issues={h['issues_count']}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    {
        "list":      _cmd_list,
        "script":    _cmd_script,
        "voiceover": _cmd_voiceover,
        "video":     _cmd_video,
        "all":       _cmd_all,
    }[args.command](args)


if __name__ == "__main__":
    main()
