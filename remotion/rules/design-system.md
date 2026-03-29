# 设计风格系统（完整参考）

## 暗色专业系配色

**Modern Dark（默认 ⭐）** — 商务/演示/技术/通用
```
背景：#000000  主文字：#FFFFFF  强调色：#0070F3（蓝）或 #22C55E（绿）或用户指定色
卡片：rgba(255,255,255,0.05) + 1px solid rgba(255,255,255,0.1)
```

**Deep Blue** — AI/数据/技术
```
背景：#0A0E27  主文字：#FFFFFF  强调色：#3B82F6
卡片：rgba(59,130,246,0.08) + 1px solid rgba(59,130,246,0.2)
```

**Warm Minimal** — 教育/人文/故事
```
背景：#1A1410  主文字：#FFFFFF  强调色：#E8B86D（暖金）
卡片：rgba(232,184,109,0.08) + 1px solid rgba(232,184,109,0.2)
```

**Brutalism** — 创意/设计/前卫
```
背景：#FFFFFF  主文字：#000000  强调色：#FF0000 或 #00FF00
卡片：#FFFF00 + 4px solid #000000（offset shadow）
```

**Glassmorphism** — 科技/SaaS/高端
```
背景：linear-gradient(135deg, #667eea, #764ba2)
卡片：rgba(255,255,255,0.1) + backdrop-filter: blur(10px)
```

## 字体推荐

- **DM Sans**：通用，清晰易读（`@remotion/google-fonts/DMSans`）
- **Space Grotesk**：科技感，数字友好（`@remotion/google-fonts/SpaceGrotesk`）
- **Space Mono**：代码感，赛博风（`@remotion/google-fonts/SpaceMono`）

## 字号规范

**竖屏 1080×1920**：主标题 96-120px / 副标题 60-80px / 正文 36-48px（fontWeight 800-900 / 700 / 400-600）

**横屏 1920×1080**：主标题 72-96px / 副标题 48-64px / 正文 28-40px（fontWeight 800-900 / 700 / 400-600）

## 背景节奏规则

- **奇数场景**：纯黑 `#000000` 或主题深色背景
- **偶数场景**：主题强调色的深变体（如 Deep Blue 用 `#0a1628`）
- 不能全片同一背景，要有节奏变化

## 光晕装饰（酌情）

信息密度高的场景可不加。如需添加，每场景最多 1-2 个：

```tsx
<div style={{
  position: 'absolute', top: '35%', left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 500, height: 500, borderRadius: '50%',
  background: `radial-gradient(circle, ${accent}22 0%, transparent 70%)`,
  pointerEvents: 'none',
}} />
```

## Spring 四种预设

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
const frame = useCurrentFrame();
const { fps } = useVideoConfig();

// 平滑无弹跳（标题、内容淡入）—— 最常用
const smooth = spring({ frame, fps, config: { damping: 200 } });

// 快弹最小弹跳（UI 元素、卡片弹入）
const snappy = spring({ frame, fps, config: { damping: 20, stiffness: 200 } });

// 明显弹跳（Emoji、数字、活泼元素）
const bouncy = spring({ frame, fps, config: { damping: 8 } });

// 沉重缓慢（大标题、警示文字）
const heavy = spring({ frame, fps, config: { damping: 15, stiffness: 80, mass: 2 } });
```
