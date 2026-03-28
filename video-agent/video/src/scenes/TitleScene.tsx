import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, staticFile, Img } from "remotion";
import { Scene, Theme } from "../types";
import { sp, SPRING_GENTLE, SPRING_SLOW } from "../utils/springs";

interface Props {
  scene: Scene;
  theme: Theme;
}

export const TitleScene: React.FC<Props> = ({ scene, theme }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgOpacity = sp(frame, fps, 0, SPRING_SLOW);
  const titleProgress = sp(frame, fps, 8, SPRING_GENTLE);
  const subtitleProgress = sp(frame, fps, 20, SPRING_GENTLE);

  const titleY = interpolate(titleProgress, [0, 1], [60, 0]);
  const subtitleY = interpolate(subtitleProgress, [0, 1], [40, 0]);

  const bgSrc = scene.asset_path ? staticFile(scene.asset_path) : null;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: theme.background_color,
        fontFamily: theme.font_family,
        overflow: "hidden",
      }}
    >
      {/* Background image */}
      {bgSrc && (
        <Img
          src={bgSrc}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: bgOpacity * 0.35,
          }}
        />
      )}

      {/* Gradient overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(135deg, ${theme.background_color}ee 0%, ${theme.primary_color}88 100%)`,
        }}
      />

      {/* Accent line */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: "50%",
          width: `${titleProgress * 6}px`,
          height: "200px",
          marginTop: "-100px",
          background: theme.accent_color,
          borderRadius: "0 4px 4px 0",
        }}
      />

      {/* Content */}
      <div style={{ position: "relative", textAlign: "center", padding: "0 120px" }}>
        <div
          style={{
            fontSize: 88,
            fontWeight: 800,
            color: theme.text_color,
            lineHeight: 1.1,
            opacity: titleProgress,
            transform: `translateY(${titleY}px)`,
            textShadow: "0 4px 24px rgba(0,0,0,0.4)",
            letterSpacing: "-1px",
          }}
        >
          {scene.title}
        </div>

        {scene.subtitle && (
          <div
            style={{
              marginTop: 32,
              fontSize: 36,
              fontWeight: 400,
              color: theme.accent_color,
              opacity: subtitleProgress,
              transform: `translateY(${subtitleY}px)`,
            }}
          >
            {scene.subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
