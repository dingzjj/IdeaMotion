import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, staticFile, Img } from "remotion";
import { Scene, Theme } from "../types";
import { sp, SPRING_SLOW } from "../utils/springs";
import { secToFrames } from "../utils/timing";

interface Props {
  scene: Scene;
  theme: Theme;
}

export const ImageScene: React.FC<Props> = ({ scene, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationFrames = secToFrames(scene.duration_seconds, fps);

  // Ken Burns: slow scale + drift
  const scale = interpolate(frame, [0, durationFrames], [1.0, 1.08]);
  const translateX = interpolate(frame, [0, durationFrames], [0, -20]);

  const captionProgress = sp(frame, fps, 12, SPRING_SLOW);
  const captionY = interpolate(captionProgress, [0, 1], [40, 0]);

  const bgSrc = scene.asset_path ? staticFile(scene.asset_path) : null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        overflow: "hidden",
        background: theme.background_color,
      }}
    >
      {/* Background with Ken Burns */}
      {bgSrc && (
        <Img
          src={bgSrc}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale}) translateX(${translateX}px)`,
          }}
        />
      )}

      {/* Dark overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 60%)",
        }}
      />

      {/* Caption */}
      {scene.caption && (
        <div
          style={{
            position: "absolute",
            bottom: 80,
            left: 0,
            right: 0,
            padding: "0 120px",
            opacity: captionProgress,
            transform: `translateY(${captionY}px)`,
          }}
        >
          <div
            style={{
              fontSize: 42,
              fontWeight: 500,
              color: "#ffffff",
              textAlign: "center",
              textShadow: "0 2px 16px rgba(0,0,0,0.8)",
              fontFamily: theme.font_family,
              borderLeft: `6px solid ${theme.accent_color}`,
              paddingLeft: 28,
              textAlign: "left",
            }}
          >
            {scene.caption}
          </div>
        </div>
      )}
    </div>
  );
};
