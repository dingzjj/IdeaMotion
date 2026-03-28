"""TTS synthesis via edge-tts (Microsoft Edge TTS — no API key required).

Install:  pip install edge-tts
Voices:   https://speech.microsoft.com/portal/voicegallery
"""

from __future__ import annotations
import asyncio
import subprocess
from pathlib import Path

VOICE_MAP: dict[str, str] = {
    "zh":    "zh-CN-XiaoxiaoNeural",
    "zh-CN": "zh-CN-XiaoxiaoNeural",
    "zh-TW": "zh-TW-HsiaoChenNeural",
    "en":    "en-US-JennyNeural",
    "en-US": "en-US-JennyNeural",
    "ja":    "ja-JP-NanamiNeural",
}
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


def is_available() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


def synthesize_scene(text: str, output_path: Path, language: str = "zh-CN") -> bool:
    """Synthesize one scene's narration text to an MP3 file.

    Returns True on success, False on failure (prints reason).
    """
    if not is_available():
        print("  [TTS] edge-tts not installed — run: pip install edge-tts")
        return False

    import edge_tts

    voice = VOICE_MAP.get(language, DEFAULT_VOICE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

    try:
        asyncio.run(_run())
        return True
    except Exception as exc:
        print(f"  [TTS] Synthesis failed for scene: {exc}")
        return False


def merge_audio_files(audio_files: list[Path], output_path: Path) -> bool:
    """Concatenate MP3 files in order using ffmpeg.

    Returns True on success.
    """
    if not audio_files:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    list_file = output_path.parent / "_concat_list.txt"
    list_file.write_text(
        "\n".join(f"file '{f.resolve()}'" for f in audio_files),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )
    list_file.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"  [TTS] ffmpeg merge failed:\n{result.stderr[-500:]}")
        return False
    return True


def merge_audio_into_video(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
) -> bool:
    """Mix an audio track into a video file using ffmpeg.

    Video codec is copied (no re-encode). Audio is encoded as AAC.
    -shortest ensures the output stops when the shorter stream ends.

    Returns True on success.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  [TTS] ffmpeg audio merge failed:\n{result.stderr[-500:]}")
        return False
    return True
