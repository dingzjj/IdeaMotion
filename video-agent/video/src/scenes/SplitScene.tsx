import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, staticFile, Img } from "remotion";
import { Scene, Theme } from "../types";
import { sp, SPRING_GENTLE, SPRING_SLOW } from "../utils/springs";

interface Props {
  scene: Scene;
  theme: Theme;
}

export const SplitScene: React.FC<Props> = ({ scene, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const imgProgress = sp(frame, fps, 0, SPRING_SLOW);
  const headingProgress = sp(frame, fps, 10, SPRING_GENTLE);
  const bodyProgress = sp(frame, fps, 20, SPRING_GENTLE);

  const imgX = interpolate(imgProgress, [0, 1], [-80, 0]);
  const dividerScale = interpolate(headingProgress, [0, 1], [0, 1]);

  const bgSrc = scene.asset_path ? staticFile(scene.asset_path) : null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        background: theme.background_color,
        fontFamily: theme.font_family,
        overflow: "hidden",
      }}
    >
      {/* Left: Image */}
      <div
        style={{
          width: "48%",
          position: "relative",
          opacity: imgProgress,
          transform: `translateX(${imgX}px)`,
          overflow: "hidden",
        }}
      >
        {bgSrc ? (
          <Img
            src={bgSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              width: "100%",
              height: "100%",
              background: `${theme.primary_color}88`,
            }}
          />
        )}
        {/* Image overlay gradient */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(to right, transparent 80%, ${theme.background_color})`,
          }}
        />
      </div>

      {/* Divider */}
      <div
        style={{
          width: 4,
          background: theme.accent_color,
          margin: "80px 0",
          borderRadius: 2,
          transform: `scaleY(${dividerScale})`,
          transformOrigin: "top",
        }}
      />

      {/* Right: Text */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "60px 80px 60px 60px",
        }}
      >
        <div
          style={{
            fontSize: 56,
            fontWeight: 700,
            color: theme.text_color,
            lineHeight: 1.2,
            marginBottom: 36,
            opacity: headingProgress,
            transform: `translateY(${interpolate(headingProgress, [0, 1], [30, 0])}px)`,
          }}
        >
          {scene.heading}
        </div>

        <div
          style={{
            fontSize: 34,
            fontWeight: 400,
            color: `${theme.text_color}cc`,
            lineHeight: 1.6,
            opacity: bodyProgress,
            transform: `translateY(${interpolate(bodyProgress, [0, 1], [20, 0])}px)`,
          }}
        >
          {scene.body}
        </div>
      </div>
    </div>
  );
};
