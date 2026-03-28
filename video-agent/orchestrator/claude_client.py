"""LLM client — storyboard generation and review via Azure OpenAI."""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

from openai import AzureOpenAI

from .schemas import Storyboard, StoryboardReview, VoiceoverScript

_PROMPTS = Path(__file__).parent / "prompts"
_STORYBOARD_SYSTEM = (_PROMPTS / "storyboard_prompt.txt").read_text(encoding="utf-8")
_REVIEW_SYSTEM     = (_PROMPTS / "review_prompt.txt").read_text(encoding="utf-8")
_VOICEOVER_SYSTEM  = (_PROMPTS / "voiceover_prompt.txt").read_text(encoding="utf-8")

# Azure OpenAI config (read from env; fallback to empty string)
AZURE_ENDPOINT    = os.environ.get("AZURE_OPENAI_ENDPOINT",    "")
AZURE_API_KEY     = os.environ.get("AZURE_OPENAI_API_KEY",     "")
AZURE_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "")
AZURE_DEPLOYMENT  = os.environ.get("AZURE_OPENAI_DEPLOYMENT",  "")


def _client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )


def _chat_json(system: str, messages: list[dict]) -> dict:
    """Call Azure OpenAI and return parsed JSON dict."""
    resp = _client().chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "system", "content": system}] + messages,
        max_completion_tokens=4096,
        response_format={"type": "json_object"},
    )
    raw = (resp.choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = "\n".join(
            line for line in raw.splitlines() if not line.startswith("```")
        ).strip()
    return json.loads(raw)


# ── Storyboard generation ─────────────────────────────────────────────────────

def generate_storyboard(
    concept: str,
    revision_instructions: Optional[str] = None,
    suggestion: Optional[str] = None,
    existing_storyboard: Optional["Storyboard"] = None,
) -> Storyboard:
    """Generate (or revise) a storyboard for the given concept.

    When ``suggestion`` + ``existing_storyboard`` are provided, the LLM receives
    the current storyboard as context and refines it according to the user's
    suggestion rather than starting from scratch.
    """
    print(f"  [LLM] Generating storyboard [{AZURE_DEPLOYMENT}]...", flush=True)

    # ── Suggestion mode: refine existing storyboard ───────────────────────────
    if suggestion and existing_storyboard:
        existing_json = json.dumps(
            json.loads(existing_storyboard.model_dump_json(by_alias=True)),
            ensure_ascii=False,
            indent=2,
        )
        messages: list[dict] = [
            {"role": "user", "content": concept},
            {"role": "assistant", "content": existing_json},
            {
                "role": "user",
                "content": (
                    "USER SUGGESTION — please refine the storyboard above:\n\n"
                    + suggestion
                    + "\n\n"
                    "Rules:\n"
                    "- Keep everything that already works well.\n"
                    "- Only change what the suggestion explicitly addresses.\n"
                    "- Return a new, complete storyboard JSON — not a summary or explanation."
                ),
            },
        ]
        data = _chat_json(_STORYBOARD_SYSTEM, messages)
        return Storyboard.model_validate(data)

    # ── Normal generation / auto-review revision ──────────────────────────────
    messages = [{"role": "user", "content": concept}]

    if revision_instructions:
        messages.append({
            "role": "user",
            "content": (
                "REVISION REQUIRED — the previous storyboard was reviewed and rejected.\n\n"
                "Apply ALL of the following instructions to produce an improved storyboard:\n\n"
                + revision_instructions
                + "\n\nYour response must be a new, complete storyboard JSON — not a summary or explanation."
            ),
        })

    data = _chat_json(_STORYBOARD_SYSTEM, messages)
    return Storyboard.model_validate(data)


# ── Voiceover script ─────────────────────────────────────────────────────────

def generate_voiceover_script(storyboard: Storyboard) -> VoiceoverScript:
    """Generate narration text for every scene in the storyboard."""
    print(f"  [LLM] Generating voiceover script [{AZURE_DEPLOYMENT}]...", flush=True)

    storyboard_json = json.dumps(
        json.loads(storyboard.model_dump_json(by_alias=True)),
        ensure_ascii=False,
        indent=2,
    )
    messages = [{"role": "user", "content": storyboard_json}]
    data = _chat_json(_VOICEOVER_SYSTEM, messages)
    return VoiceoverScript.model_validate(data)


def refine_voiceover_script(
    storyboard: Storyboard,
    existing_script: VoiceoverScript,
    suggestion: str,
) -> VoiceoverScript:
    """Refine an existing voiceover script based on a user suggestion."""
    print(f"  [LLM] Refining voiceover script [{AZURE_DEPLOYMENT}]...", flush=True)

    storyboard_json = json.dumps(
        json.loads(storyboard.model_dump_json(by_alias=True)),
        ensure_ascii=False,
        indent=2,
    )
    existing_json = json.dumps(existing_script.model_dump(), ensure_ascii=False, indent=2)

    messages = [
        {"role": "user",      "content": storyboard_json},
        {"role": "assistant", "content": existing_json},
        {
            "role": "user",
            "content": (
                "USER SUGGESTION — please refine the voiceover script above:\n\n"
                + suggestion
                + "\n\n"
                "Rules:\n"
                "- Keep the scene_id values exactly as-is.\n"
                "- Only change the narration text, not the structure.\n"
                "- Return a new, complete voiceover JSON — not a summary or explanation."
            ),
        },
    ]
    data = _chat_json(_VOICEOVER_SYSTEM, messages)
    return VoiceoverScript.model_validate(data)


# ── Storyboard review ─────────────────────────────────────────────────────────

def review_storyboard(storyboard: Storyboard) -> StoryboardReview:
    """Review a storyboard for educational quality. Returns structured review."""
    print(f"  [LLM] Reviewing storyboard [{AZURE_DEPLOYMENT}]...", flush=True)

    storyboard_json = json.dumps(
        json.loads(storyboard.model_dump_json(by_alias=True)),
        ensure_ascii=False,
        indent=2,
    )
    messages = [{"role": "user", "content": storyboard_json}]
    data = _chat_json(_REVIEW_SYSTEM, messages)
    return StoryboardReview.model_validate(data)
