"""Pydantic schemas for the storyboard — shared contract between LLM, agents and Remotion."""

from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


SceneType = Literal["title", "bullet", "split", "image", "diagram", "step", "outro"]

AnimationType = Literal[
    "fade_zoom_in",
    "stagger_slide_up",
    "slide_in_from_left",
    "draw_arrows",
    "ken_burns",
    "fade_in_center",
    "slide_in_steps",
]


class DiagramNode(BaseModel):
    id: str
    label: str
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class DiagramEdge(BaseModel):
    from_node: str = Field(alias="from")
    to: str
    label: Optional[str] = None

    model_config = {"populate_by_name": True}


class StepItem(BaseModel):
    number: int
    title: str
    description: str


class Scene(BaseModel):
    id: str
    type: SceneType
    duration_seconds: float = Field(gt=0)
    animation: AnimationType
    image_query: Optional[str] = None
    asset_path: Optional[str] = None  # filled in by asset_manager

    # type-specific (all optional at schema level)
    title: Optional[str] = None
    subtitle: Optional[str] = None
    heading: Optional[str] = None
    body: Optional[str] = None
    bullets: Optional[list[str]] = None
    caption: Optional[str] = None
    message: Optional[str] = None
    nodes: Optional[list[DiagramNode]] = None
    edges: Optional[list[DiagramEdge]] = None
    steps: Optional[list[StepItem]] = None

    @model_validator(mode="after")
    def validate_required_fields(self) -> "Scene":
        if self.type == "title" and not self.title:
            raise ValueError("title scene requires 'title' field")
        if self.type == "bullet" and not self.bullets:
            raise ValueError("bullet scene requires 'bullets' field")
        if self.type == "step" and not self.steps:
            raise ValueError("step scene requires 'steps' field")
        if self.type == "outro" and not self.message:
            raise ValueError("outro scene requires 'message' field")
        return self


class Theme(BaseModel):
    primary_color: str = "#1E3A5F"
    accent_color: str = "#4CAF50"
    background_color: str = "#0D1B2A"
    font_family: str = "Inter"
    text_color: str = "#FFFFFF"


class Resolution(BaseModel):
    width: int = 1920
    height: int = 1080


class Storyboard(BaseModel):
    title: str
    total_duration_seconds: float
    fps: int = 30
    resolution: Resolution = Resolution()
    theme: Theme
    scenes: list[Scene]

    @model_validator(mode="after")
    def validate_duration(self) -> "Storyboard":
        computed = sum(s.duration_seconds for s in self.scenes)
        if abs(computed - self.total_duration_seconds) > 1.0:
            self.total_duration_seconds = computed
        return self

    def total_frames(self) -> int:
        return round(self.total_duration_seconds * self.fps)


# ── Voiceover models ──────────────────────────────────────────────────────────

class SceneNarration(BaseModel):
    scene_id: str
    text: str  # narration text to be read aloud for this scene

class VoiceoverScript(BaseModel):
    scenes: list[SceneNarration]
    language: str = "zh-CN"  # BCP-47 tag used to pick TTS voice


# ── Review models ─────────────────────────────────────────────────────────────

class DimensionScores(BaseModel):
    educational_quality: float = Field(ge=1.0, le=10.0,
        description="Does it clearly answer WHAT/HOW/WHY?")
    completeness: float = Field(ge=1.0, le=10.0,
        description="Are all key aspects covered with real examples?")
    variety: float = Field(ge=1.0, le=10.0,
        description="Scene type diversity; no repeated consecutive types")
    pacing: float = Field(ge=1.0, le=10.0,
        description="Duration distribution; no scene too short or too long")
    clarity: float = Field(ge=1.0, le=10.0,
        description="Language plainness; analogies; bullet conciseness")

    @property
    def average(self) -> float:
        vals = [self.educational_quality, self.completeness,
                self.variety, self.pacing, self.clarity]
        return round(sum(vals) / len(vals), 2)


APPROVAL_THRESHOLD = 7.5


class StoryboardReview(BaseModel):
    scores: DimensionScores
    average_score: float = 0.0          # computed below
    approved: bool = False               # computed below
    issues: list[str]                    # concrete problems found
    suggestions: list[str]               # improvement ideas
    revision_instructions: str           # actionable instructions for the generator

    @model_validator(mode="after")
    def compute_approval(self) -> "StoryboardReview":
        self.average_score = self.scores.average
        self.approved = self.average_score >= APPROVAL_THRESHOLD
        return self
