import React from "react";
import { Composition, staticFile, CalculateMetadataFunction } from "remotion";
import { KnowledgeVideo, TRANSITION_FRAMES } from "./compositions/KnowledgeVideo";
import { Storyboard } from "./types";
import { totalFrames } from "./utils/timing";

// Trigger Inter font loading before any rendering begins
import "./utils/fonts";

// Fallback duration if storyboard.json hasn't been generated yet
const DEFAULT_DURATION_FRAMES = 1800; // 60s @ 30fps
const DEFAULT_FPS = 30;

/**
 * Dynamically compute composition duration from storyboard.json.
 * Accounts for the cross-fade transition overlap between scenes.
 */
const calculateMetadata: CalculateMetadataFunction = async () => {
  try {
    const response = await fetch(staticFile("storyboard.json"));
    const storyboard: Storyboard = await response.json();
    const fps = storyboard.fps ?? DEFAULT_FPS;
    const totalSceneFrames = totalFrames(storyboard.scenes, fps);
    // Each transition overlaps two adjacent scenes, reducing total duration
    const transitionReduction =
      Math.max(0, storyboard.scenes.length - 1) * TRANSITION_FRAMES;
    return {
      durationInFrames: Math.max(1, totalSceneFrames - transitionReduction),
      fps,
    };
  } catch {
    return { durationInFrames: DEFAULT_DURATION_FRAMES, fps: DEFAULT_FPS };
  }
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="KnowledgeVideo"
      component={KnowledgeVideo}
      durationInFrames={DEFAULT_DURATION_FRAMES}
      fps={DEFAULT_FPS}
      width={1920}
      height={1080}
      calculateMetadata={calculateMetadata}
    />
  );
};
