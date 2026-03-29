# 小红书风格设计系统

面向小红书/Instagram/视频号的温暖风格视频。与暗色主题形成鲜明对比，适合生活方式、知识分享、情感类内容。

## 何时使用

- 用户明确要求"小红书风格"
- 目标平台是小红书、Instagram、视频号
- 内容调性：生活方式、美妆、美食、情感、轻知识
- 不适用：技术讲解、商务演示、严肃分析

---

## 四套配色方案

### 1. 莫兰迪暖调（默认推荐）
**适用**：知识类、生活方式、情感治愈

```typescript
export const MORANDI = {
  primary: "#C9A87C",       // 核心暖棕 - 标题/重点
  accent: "#D4A574",        // 杏仁橙 - 强调/按钮
  secondary: "#C9B8A8",     // 暖灰米 - 次要元素
  dark: "#3D3D3D",          // 正文
  cream: "#FDF8F3",         // 奶油白
  warmGray: "#F5F0EB",      // 暖灰背景
  bgGradient: "linear-gradient(135deg, #FDF8F3 0%, #F0E6DB 100%)",
};
```

### 2. 香槟金
**适用**：时尚、美妆、高端产品

```typescript
export const CHAMPAGNE = {
  primary: "#C9A86C",       // 香槟金
  accent: "#B76E79",        // 玫瑰金
  secondary: "#E8D5B5",     // 奶油米
  dark: "#2C2C2C",
  cream: "#FDF8F0",
  bgGradient: "linear-gradient(135deg, #FDF8F0 0%, #F5EBD9 100%)",
};
```

### 3. 大地陶土
**适用**：美食、旅行、家居、手作

```typescript
export const TERRACOTTA = {
  primary: "#C17F59",       // 赤陶色
  accent: "#8B7355",        // 橄榄绿
  secondary: "#D4C4A8",     // 沙色
  dark: "#3A3028",
  cream: "#FAF6F0",
  bgGradient: "linear-gradient(135deg, #FAF6F0 0%, #EBE0D0 100%)",
};
```

### 4. 复古电影
**适用**：文艺、情感故事、怀旧

```typescript
export const VINTAGE = {
  primary: "#B5651D",       // 焦糖棕
  accent: "#E6C35C",        // 奶油黄
  secondary: "#8B4513",     // 深红褐
  dark: "#2D2620",
  cream: "#FFF8F0",
  bgGradient: "linear-gradient(135deg, #FFF8F0 0%, #F0E0C8 100%)",
};
```

---

## 字体系统

```typescript
// 在 Root.tsx 顶层加载
import { loadFont } from "@remotion/google-fonts/ZCOOLKuaiLe";
import { loadFont as loadNotoSans } from "@remotion/google-fonts/NotoSansSC";

loadFont();      // ZCOOL KuaiLe - 标题，俏皮圆润
loadNotoSans();  // Noto Sans SC - 正文，清晰易读

export const FONT_DISPLAY = "ZCOOL KuaiLe";
export const FONT_BODY = "Noto Sans SC";
```

**字号规范（竖屏 1080×1920）**：
- 主标题：72-96px，fontWeight: 700-900，FONT_DISPLAY
- 副标题：48-64px，fontWeight: 700，FONT_DISPLAY
- 正文：32-40px，fontWeight: 400-600，FONT_BODY
- 标签/badge：24-28px，fontWeight: 700，FONT_BODY

---

## 可复用组件

### AnimatedTitle（弹入标题）
```tsx
export const AnimatedTitle: React.FC<{
  text: string; delay?: number; fontSize?: number; color?: string;
}> = ({ text, delay = 0, fontSize = 72, color = "#3D3D3D" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - delay, fps, config: { damping: 15, stiffness: 120 } });
  const translateY = interpolate(progress, [0, 1], [60, 0]);

  return (
    <div style={{
      fontSize, fontWeight: 700, color,
      transform: `translateY(${translateY}px)`,
      opacity: Math.max(0, progress),
      fontFamily: `"ZCOOL KuaiLe", "Noto Sans SC", sans-serif`,
      textAlign: "center", lineHeight: 1.3,
    }}>
      {text}
    </div>
  );
};
```

### Card（内容卡片）
```tsx
export const Card: React.FC<{
  children: React.ReactNode;
  delay?: number;
  backgroundColor?: string;
  borderColor?: string;
}> = ({ children, delay = 0, backgroundColor = "#FFFFFF", borderColor = "#D4A574" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - delay, fps, config: { damping: 15, stiffness: 100 } });
  const scale = interpolate(progress, [0, 1], [0.8, 1]);

  return (
    <div style={{
      backgroundColor, borderRadius: 24, padding: "40px 50px",
      borderLeft: `6px solid ${borderColor}`,
      boxShadow: "0 10px 40px rgba(0,0,0,0.08)",
      transform: `scale(${scale})`,
      opacity: Math.max(0, progress),
    }}>
      {children}
    </div>
  );
};
```

### Badge（标签胶囊）
```tsx
export const Badge: React.FC<{
  text: string; color?: string; textColor?: string; delay?: number;
}> = ({ text, color = "#C9A87C", textColor = "#FFFFFF", delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - delay, fps, config: { damping: 12 } });

  return (
    <div style={{
      backgroundColor: color, color: textColor,
      padding: "8px 24px", borderRadius: 50,
      fontSize: 28, fontWeight: 700,
      fontFamily: `"Noto Sans SC", sans-serif`,
      transform: `scale(${progress})`,
      opacity: Math.max(0, progress),
      display: "inline-block",
    }}>
      {text}
    </div>
  );
};
```

### EmojiPop（弹跳 Emoji）
```tsx
export const EmojiPop: React.FC<{
  emoji: string; delay?: number; size?: number;
}> = ({ emoji, delay = 0, size = 80 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({ frame: frame - delay, fps, config: { damping: 8, stiffness: 200 } });
  const scale = interpolate(progress, [0, 1], [0, 1.2]);
  const rotation = interpolate(progress, [0, 1], [-20, 5]);

  return (
    <div style={{
      fontSize: size,
      transform: `scale(${scale}) rotate(${rotation}deg)`,
      opacity: Math.max(0, progress),
      display: "inline-block",
    }}>
      {emoji}
    </div>
  );
};
```

---

## 布局模式

### 模式 A：Hook / Outro（全屏居中）
```
┌─────────────────────────────────┐
│    ● 装饰圆圈                   │
│                                 │
│         [Badge]                 │
│    ✨ Main Title ✨             │
│       Subtitle                  │
│    🤯  📈  (emoji 行)          │
│    ● 装饰圆圈                   │
└─────────────────────────────────┘
```

### 模式 B：卡片对比
```
┌─────────────────────────────────┐
│         [Badge]                 │
│    Main Title                   │
│  ┌──────────┐ ┌──────────┐     │
│  │  Card 1  │ │  Card 2  │     │
│  │  emoji   │ │  emoji   │     │
│  └──────────┘ └──────────┘     │
│      [底部 tag / emoji]         │
└─────────────────────────────────┘
```

### 模式 C：进度条数据
```
┌─────────────────────────────────┐
│    Main Title                   │
│  Label1 ████████░░ 60%         │
│  Label2 ████████████ 80%       │
│  Label3 ███░░░░░░░░ 30%        │
└─────────────────────────────────┘
```

---

## 动画原则

1. **错开入场**：每个元素延迟 10-15 帧
2. **spring 参数**：damping: 12-15（一般），damping: 8（Emoji 弹跳）
3. **禁止 CSS animation**：所有动效必须用 `useCurrentFrame()` + spring/interpolate
4. **轻微漂浮**：装饰元素可用 `Math.sin(frame / fps * 2) * 8` 上下浮动
5. **卡片缩放入场**：从 scale(0.8) 到 scale(1)，不只是淡入

---

## 文案风格（小红书口播）

1. **开场钩子**：反问或惊喜事实
2. **Emoji 只用于视觉文字**，不出现在口播里
3. **轻松口语**：朋友们！/ 你猜怎么着？/ 这波叫 XX！
4. **适度幽默**：稳如老狗 / 主打一个 XX / 香不香
5. **重复强调**：重要的事说三遍
6. **结尾 CTA**：点赞收藏，下期再见！
7. **单场景 ≤25 秒**

---

## package.json 额外依赖

```json
{
  "dependencies": {
    "@remotion/google-fonts": "^4.0.0"
  }
}
```

注意：小红书风格**不使用** `@phosphor-icons/react`，改用 Emoji 作为图标，保持轻松感。
