# IdeaMotion - Remotion 视频创作知识库

AI 驱动的视频创作框架，基于 Remotion（React 视频合成库），为 Claude 等 AI Agent 提供完整的视频脚本编写与代码生成规则体系。

## 项目简介

本项目是一套面向 AI Agent 的视频创作知识库，涵盖：

- **脚本理论**：HKRR 模型（幸福感/知识量/共鸣度/节奏感）、何同学式叙事结构
- **设计系统**：5 套配色方案（Modern Dark / Deep Blue / Warm Minimal / Glassmorphism / 小红书风格）
- **Remotion 技术规范**：动画、合成、序列、转场、字幕等 47 条规则
- **媒体处理**：音频可视化、TTS 语音合成、视频处理、字幕同步

## 项目结构

```
IdeaMotion/
├── remotion/
│   ├── SKILL.md                 # 主工作流定义（启动检查、铁律、规则索引）
│   └── rules/                   # 47 条 Markdown 规则文件
│       ├── output-format.md     # script.json 标准格式
│       ├── hkrr-theory.md       # HKRR 内容质量模型
│       ├── hook-patterns.md     # 5 种开场钩子类型
│       ├── hetongxue-narrative.md # 三幕叙事结构
│       ├── design-system.md     # 完整设计系统（配色/字体/间距）
│       ├── animations.md        # Spring / interpolate 动画规范
│       ├── compositions.md      # Composition / Still / Folder
│       ├── sequencing.md        # Sequence / Series / premountFor
│       ├── transitions.md       # TransitionSeries 转场
│       ├── audio.md             # 音频导入与控制
│       ├── audio-visualization.md # 频谱/波形可视化
│       ├── voiceover.md         # ElevenLabs / MiniMax TTS
│       ├── 3d.md                # Three.js + React Three Fiber
│       ├── charts.md            # 数据可视化图表
│       └── ...                  # 更多规则详见 rules/ 目录
└── agent-promo/src/             # Remotion 视频项目（待创建）
```

## 技术栈

| 类别 | 技术 |
|------|------|
| 视频框架 | [Remotion](https://www.remotion.dev/) |
| 前端 | React + TypeScript |
| 样式 | Tailwind CSS（仅布局，禁用 animate-*） |
| 字体 | @remotion/google-fonts |
| 3D | Three.js + React Three Fiber |
| TTS | ElevenLabs / MiniMax |
| 视频处理 | FFmpeg |

## 快速开始

### 1. 初始化 Remotion 项目

```bash
npx create-video@latest agent-promo --no-open
cd agent-promo
npm install
```

### 2. 开发预览

```bash
npx remotion studio
```

### 3. 渲染输出

```bash
npx remotion render src/index.ts MyComposition out/video.mp4
```

## 核心铁律

使用本知识库进行视频创作时，必须遵守以下规则：

1. **所有动画必须使用** `useCurrentFrame()` + `spring()` / `interpolate()`，禁止 CSS Transitions 和 Tailwind `animate-*`
2. **字体必须通过** `@remotion/google-fonts` 加载，禁止硬编码字体字符串
3. **`premountFor` 必须写为** `premountFor={1 * fps}`，禁止硬编码 `30`
4. **脚本输出格式**严格遵循 `script.json` 标准（见 `rules/output-format.md`）

## 内容创作模型

### HKRR 模型

每个视频从四个维度评估质量：

- **H**appiness（幸福感）— 观众的情绪体验
- **K**nowledge（知识量）— 信息密度与深度
- **R**esonance（共鸣度）— 与观众经验的连接
- **R**hythm（节奏感）— 叙事节奏与张力

### 三幕叙事结构

| 阶段 | 时长 | 目标 |
|------|------|------|
| Hook（钩子） | 5-8 秒 | 抓住注意力 |
| Journey（旅程） | 40-45 秒 | 传递核心内容 |
| Payoff（收尾） | 5-8 秒 | 留下深刻印象 |

## 开发者

- 刘奕彤
- 丁梓健
- 杨洋
- 大可DK

## 许可证

MIT
