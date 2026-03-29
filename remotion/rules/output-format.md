# 脚本输出格式（script.json）

## 标准格式

```json
{
  "meta": {
    "topic": "视频主题名（用于目录命名，不含特殊字符）",
    "title": "视频标题（观众看到的标题）",
    "duration": 60,
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "target_audience": "目标观众描述",
    "challenge": "让[目标观众]在[场景]下，[解决的问题]",
    "hkrr": {
      "H": "本视频的快乐元素：[具体描述]",
      "K": "核心知识点：[一句话]",
      "R_resonance": "共鸣点：[具体描述]",
      "R_rhythm": "节奏设计：[快/慢/快/慢分布]"
    }
  },
  "scenes": [
    {
      "id": "scene_1",
      "name": "Hook",
      "startFrame": 0,
      "durationInFrames": 210,
      "visual": {
        "type": "big_word",
        "layout": "模板1（大字冲击）",
        "content": {
          "line1": "主文字（具体文字内容）",
          "line2": "副文字（可选）",
          "accent_color": "#0070F3"
        },
        "background": "deep_dark",
        "animation": "spring_bounce_in"
      },
      "subtitle": "字幕文字，≤15字/行",
      "voiceover": "完整口播内容，口语化，包含停顿标记[pause]"
    },
    {
      "id": "scene_2",
      "name": "Journey_Step1",
      "startFrame": 210,
      "durationInFrames": 270,
      "visual": {
        "type": "step_by_step",
        "layout": "模板2（逐句打字）",
        "content": {
          "label": "场景小标题",
          "lines": [
            { "text": "第一句", "sub": "辅助说明", "color": "#FFFFFF" },
            { "text": "第二句", "sub": "辅助说明", "color": "#0070F3" }
          ]
        },
        "background": "pure_black",
        "animation": "stagger_slide_up"
      },
      "subtitle": "字幕文字",
      "voiceover": "口播内容[pause]更多内容"
    }
  ],
  "assets": {
    "images_needed": ["需要的图片描述"],
    "icons_needed": ["需要的图标（Phosphor Icons 名称）"],
    "fonts": ["DMSans", "SpaceGrotesk"]
  },
  "theme": "modern_dark"
}
```

## 字段说明

### meta 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| topic | ✅ | 英文/拼音，用于创建目录，如 `rag-explain` |
| title | ✅ | 中文标题，如 `RAG 是什么？让 AI 学会查资料` |
| duration | ✅ | 总秒数，通常 60 |
| fps | ✅ | 帧率，通常 30 |
| width/height | ✅ | 竖屏 1080×1920，横屏 1920×1080 |
| challenge | ✅ | 挑战定义，必须包含目标观众、场景、目标 |
| hkrr | ✅ | 四项评估，K 必须填具体知识点 |

### scene 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| id | ✅ | 唯一 ID，如 `scene_1`、`scene_2` |
| name | ✅ | 语义名称：Hook / Journey_Step1~N / Payoff |
| startFrame | ✅ | 起始帧（从 0 开始，等于前一场景的 startFrame + durationInFrames） |
| durationInFrames | ✅ | 持续帧数（秒数 × fps，如 7秒 = 210帧） |
| visual.type | ✅ | big_word / step_by_step / split_compare / highlight / payoff |
| visual.layout | ✅ | 对应 component-templates.md 的模板编号 |
| visual.content | ✅ | 具体可执行的内容，不能写"展示原理"这种模糊描述 |
| visual.background | ✅ | deep_dark / pure_black / theme_color / warm_dark |
| subtitle | ✅ | 精简字幕，每行 ≤15 字，换行用 `\n` |
| voiceover | ✅ | 完整口播，口语化，停顿用 `[pause]` 标记 |

### visual.type 枚举值

| 类型 | 对应模板 | 适用场景 |
|------|---------|---------|
| `big_word` | 模板1 | Hook、单个核心观点、Payoff |
| `step_by_step` | 模板2 | 流程步骤、概念逐句解释 |
| `split_compare` | 模板3 | 对比场景（好/坏、有/无） |
| `highlight` | 模板4 | 关键词强调、警示结论 |
| `payoff` | 模板5 | 最后一屏，极简收尾 |

### theme 枚举值（对应 design-guide.md）

| 值 | 主题 | 适用 |
|----|------|------|
| `modern_dark` | Modern Dark | 商务/演示/通用 ⭐ |
| `deep_blue` | Deep Blue | AI/技术/数据 |
| `warm_minimal` | Warm Minimal | 教育/人文 |
| `brutalism` | Brutalism | 创意/设计 |
| `glassmorphism` | Glassmorphism | 科技/SaaS |
| `xiaohongshu_morandi` | 小红书莫兰迪 | 知识/生活方式 |
| `xiaohongshu_champagne` | 小红书香槟金 | 时尚/美妆 |
| `xiaohongshu_terracotta` | 小红书大地陶土 | 美食/旅行 |

## 时长速查表

| 秒数 | 帧数（30fps） | 适用场景 |
|------|-------------|---------|
| 5s | 150f | 极简 Hook / 极简 Payoff |
| 7s | 210f | 标准 Hook |
| 8s | 240f | 认知冲突 Step |
| 10s | 300f | 标准 Journey Step |
| 12s | 360f | 流程步骤（每步4秒） |
| 15s | 450f | 核心知识点重点场景 |
| 20s | 600f | 最长单场景（Step 4 核心知识） |

## 完整示例（RAG 解释视频）

```json
{
  "meta": {
    "topic": "rag-explain",
    "title": "RAG 是什么？让 AI 学会查资料",
    "duration": 60,
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "target_audience": "想用 AI 的产品经理和开发者",
    "challenge": "让想用 AI 的产品经理，在工具选型时，搞清楚 RAG 能干什么",
    "hkrr": {
      "H": "用开卷考试类比，让技术概念变得好笑又好懂",
      "K": "RAG = 给 AI 一个实时图书馆，让它带资料回答",
      "R_resonance": "AI 胡说八道是很多人的痛点",
      "R_rhythm": "Hook(7s)快 → Step1-2(10s)中 → Step3(15s)慢 → Payoff(7s)快"
    }
  },
  "scenes": [
    {
      "id": "scene_1",
      "name": "Hook",
      "startFrame": 0,
      "durationInFrames": 210,
      "visual": {
        "type": "big_word",
        "layout": "模板1（大字冲击）",
        "content": {
          "line1": "AI 为什么会",
          "line2": "胡说八道？",
          "accent_color": "#0070F3"
        },
        "background": "pure_black",
        "animation": "spring_scale_in"
      },
      "subtitle": "AI 为什么会胡说八道？",
      "voiceover": "你有没有发现，ChatGPT 有时候说的话一本正经，但完全是错的。[pause] 它在胡说八道。[pause] 为什么？"
    },
    {
      "id": "scene_2",
      "name": "Journey_Step1",
      "startFrame": 210,
      "durationInFrames": 300,
      "visual": {
        "type": "split_compare",
        "layout": "模板3（左右对比）",
        "content": {
          "left": { "label": "普通 AI", "points": ["闭卷考试", "只靠记忆", "知识停在训练时"] },
          "right": { "label": "RAG", "points": ["开卷考试", "实时查资料", "知识始终最新"] },
          "leftColor": "#FF4444",
          "rightColor": "#22C55E"
        },
        "background": "pure_black",
        "animation": "slide_in_from_sides"
      },
      "subtitle": "普通AI：闭卷\nRAG：开卷考试",
      "voiceover": "普通 AI 就像闭卷考试，只能靠训练时记住的东西回答。[pause] 而 RAG 是开卷考试——考试时可以翻书。"
    },
    {
      "id": "scene_3",
      "name": "Journey_Step2",
      "startFrame": 510,
      "durationInFrames": 450,
      "visual": {
        "type": "step_by_step",
        "layout": "模板2（逐句打字）",
        "content": {
          "label": "RAG 三步走",
          "lines": [
            { "text": "① 你提问", "sub": "输入你的问题", "color": "#FFFFFF" },
            { "text": "② AI 去查资料", "sub": "知识库语义检索", "color": "#0070F3" },
            { "text": "③ 带资料回答你", "sub": "有据可查，不乱编", "color": "#22C55E" }
          ]
        },
        "background": "pure_black",
        "animation": "stagger_slide_up"
      },
      "subtitle": "你问 → AI查 → 准确答",
      "voiceover": "RAG 让 AI 多了三步动作。[pause] 第一，你提问。第二，AI 去知识库查相关资料。[pause] 第三，带着查到的资料，回来准确回答你。"
    },
    {
      "id": "scene_4",
      "name": "Payoff",
      "startFrame": 960,
      "durationInFrames": 240,
      "visual": {
        "type": "payoff",
        "layout": "模板5（极简结尾）",
        "content": {
          "line1": "不是让 AI 更聪明",
          "accent_word": "给它一个图书馆",
          "line2": "RAG 就是这么简单",
          "accent_color": "#0070F3"
        },
        "background": "pure_black",
        "animation": "heavy_spring_in"
      },
      "subtitle": "给 AI 一个图书馆",
      "voiceover": "记住这句话：不是让 AI 更聪明，而是给它一个图书馆。[pause] 这就是 RAG。"
    }
  ],
  "assets": {
    "icons_needed": ["BookOpen", "MagnifyingGlass", "CheckCircle", "XCircle"],
    "fonts": ["DMSans"]
  },
  "theme": "modern_dark"
}
```
