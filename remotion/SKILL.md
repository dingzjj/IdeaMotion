---
name: remotion-pro
description: Best practices for Remotion - Video creation in React. Includes script writing (HKRR/得到/何同学), unified design system, and Remotion technical rules.
metadata:
  tags: remotion, video, react, animation, composition, script, design
---

## When to use

Use this skill whenever you are dealing with Remotion video creation — from script writing to code generation.

---

## 启动检查（每次必做）

**先读取用户偏好**：检查 workspace memory 中是否有 `remotion_user_prefs.md`，有则应用，详见 `rules/user-prefs.md`。

---

## 铁律（不可违反）

- **所有动效必须基于 `useCurrentFrame()` + `spring()`/`interpolate()`**
- **CSS transitions 和 Tailwind `animate-*`/`transition-*` 类 FORBIDDEN**
- **字体必须用 `@remotion/google-fonts` 的 `loadFont()` 加载，不写裸字符串**
- **`premountFor` 必须写 `premountFor={1 * fps}`，不写 `premountFor={30}`**

---

## 设计风格系统

### 两大风格体系

| 风格体系 | 主题 | 适用平台/场景 |
|---------|------|-------------|
| **暗色专业系** | Modern Dark / Deep Blue / Warm Minimal / Brutalism / Glassmorphism | B站、YouTube、商务演示、技术讲解 |
| **温暖小红书系** | 莫兰迪、香槟金、大地陶土、复古电影 | 小红书、视频号、Instagram |

**选择规则**：
- 用户明确说"小红书风格" → 温暖小红书系，加载 `rules/xiaohongshu-style.md`
- 其余所有场景 → 暗色专业系，默认 Modern Dark（`#000000` 背景 + `#0070F3` 强调色）

完整配色、字号、字体、光晕代码 → `rules/design-system.md`

---

## 质量评估（生成前必做）

**在生成任何场景代码前，加载 `rules/quality-eval.md` 并执行预检清单。**

预检六项（快速版）：
- [ ] 每个场景只有1个核心重点？
- [ ] 主标题已设计为 ≥96px？
- [ ] 多元素已设计 stagger 延迟（每个差 3-8 帧）？
- [ ] 场景时长与口播字数匹配（字数÷3.5≈秒数）？
- [ ] 配色控制在3种以内（背景+主色+强调色）？
- [ ] 无超过6行文字的场景？

**动效铁律**：
- Spring 弹出必须带轻微超越回弹：`damping: 8-15`，禁止纯淡入
- 同屏多元素必须 stagger，每个延迟 3-8 帧，禁止同时出现
- 弹入后加慢速微动消除 PPT 感：`Math.sin(frame/fps * Math.PI * 0.5) * 6`

---

## 脚本创作（Script Writing）

### 何时加载参考文件

| 需求 | 加载文件 |
|------|---------|
| 设计开场钩子 | `rules/hook-patterns.md` |
| 评估内容质量 | `rules/hkrr-theory.md` |
| 品控感性材料 | `rules/dedao-standards.md` |
| 叙事结构设计 | `rules/hetongxue-narrative.md` |
| 输出 script.json 格式 | `rules/output-format.md` |
| 深度知识拆解 | `rules/knowledge-decomposition.md` |
| 生成前预检 / 生成后评审 | `rules/quality-eval.md` |

### 脚本核心流程

1. **定义挑战**（得到标准）：`让[目标观众]在[场景]下，[解决的问题]`
2. **选择钩子类型**：痛点唤醒 / 反常识 / 承诺结果 / 场景代入 / 数据冲击
3. **HKRR 检查**：K 必选 + 至少 1 项 H 或 R
4. **何同学结构**：Hook → Journey → Payoff
5. **输出 script.json**（output-format.md）
6. **生成前预检**（quality-eval.md）：六项检查全部通过再生成代码

---

## Remotion 技术规则索引

### 动画与时序
- `rules/animations.md` — spring、interpolate、easing 基础
- `rules/timing.md` — 插值曲线、spring 预设、出入场合并
- `rules/sequencing.md` — Sequence、Series、premountFor 规范
- `rules/transitions.md` — TransitionSeries、fade、slide 转场

### 文字与字体
- `rules/text-animations.md` — 打字机、关键词高亮、逐行出现
- `rules/fonts.md` — Google Fonts 加载、中文字体
- `rules/subtitles.md` — 字幕组件、SRT 同步

### 媒体
- `rules/audio.md` — 音频导入、音量、速度
- `rules/videos.md` — 视频嵌入、trimming、循环
- `rules/images.md` — Img 组件、静态资源
- `rules/gifs.md` — GIF 动图同步
- `rules/voiceover.md` — ElevenLabs/MiniMax TTS 配音

### 高级功能
- `rules/3d.md` — Three.js + React Three Fiber
- `rules/charts.md` — 图表可视化（柱/饼/折线）
- `rules/lottie.md` — Lottie 动画嵌入
- `rules/tailwind.md` — Tailwind 在 Remotion 中的使用（布局可用，animate-* 禁止）
- `rules/ffmpeg.md` — 视频剪辑、静音检测
- `rules/fast-render.md` — Node.js API 渲染（比 CLI 快）
- `rules/parameters.md` — Zod schema 参数化
- `rules/audio-visualization.md` — 频谱、波形、低频响应

### 内容创作 & 风格
- `rules/knowledge-decomposition.md` — 深度知识拆解
- `rules/xiaohongshu-style.md` — 小红书温暖风格设计系统
- `rules/design-system.md` — 暗色专业系完整配色 + spring 预设

---

## 用户偏好 & 设计灵感

- **偏好记忆**：启动时检查 memory，创作过程中收集并保存偏好 → 详见 `rules/user-prefs.md`
- **灵感更新**：用户说「更新设计风格」/「灵感更新」时，搜索 GitHub/clawhub.world/remotion.dev showcase，追加新配色主题到 `rules/design-system.md`，新建 `rules/design-inspo-[YYYY-MM].md` 存放参考，**禁止改动铁律和脚本流程**。更新后告知用户新增内容及使用方式。
