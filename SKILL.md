---
name: iskill-video-clipper
description: 实拍素材短视频剪辑（照片+视频混合 → 15-60s 成片/剪映草稿），双引擎：--engine local 程序化合成（默认）/ aigc-mix 混合（缺镜 AI 补）/ aigc-full 全 AI。两种入口：①独立剪辑——用户要求"剪视频/切条/做成片/活动视频剪辑"并给素材目录；②六步爆款工作流第 6 步——输入 viral-video-team-output/文案/ 下的定稿口播稿（v2）+ 预检通过的选题，字幕用定稿文案、按需配音对齐，产出成片或剪映工程。素材支持零输入：raw/ → dig-media/（图库）→ AIGC 补镜多级回退。有 BGM 时自动调 iskill-music-beats 分析节拍点，转场卡在节拍上。转场默认 gl 档（HyperFrames GPU shader 转场，详见 reference/gpu-transitions.md），xfade 为回退。全流程本地 ffmpeg，免费无付费环节（AIGC 档除外，计费且事前确认）。
---

# iskill-video-clipper 实拍素材短视频剪辑

把「照片 + 视频」原始素材剪成带标题、字幕、LOGO、BGM 的短视频成片。核心理念：**先侦察再剪辑**——绝不在没看过素材内容前动手。

```
六步爆款工作流：[1]选题(hot-topic-scout) → [2]拆解(viral-teardown) → [3]文案(viral-copywriter)
→ [4]去AI味+点评(copy-deslop) → [5]预检(content-precheck) → [6]成片/剪映草稿(本skill)
```

**素材引擎三档（--engine，只决定「画面从哪来」，剪辑管线完全共用）**：
- `local`（默认）：实拍 + 图库，全免费，现状流程
- `aigc-mix`：免费素材优先，缺的镜头按 iskill-dig-media「AI 生成供给」协议补（计费、事前确认）
- `aigc-full`：无实拍，口播稿逐段 prompt 化全量 AI 生成（计费最高、必须逐次确认）

**按用途分流（与引擎档位正交，防误判）**：用户指定「封面用AI」「标题卡用AI」「其他不要AI」这类**单点 AI 约束**时——引擎保持 `local`（成片画面不引入 AI），仅指定用途单独走 iskill-dig-media「AI 生成供给」的 ai-image 协议（credits 事前确认）。**不要因为出现「AI」关键词就提升引擎档位**；约束原文记入分镜表备注，交付时注明「仅 X 为 AI 生成」。

## 封面产出（第 6 步附属交付物）

成片完成后默认产出封面：`viral-video-team-output/成片/YYYY-MM-DD-<选题短名>-封面.png`。

- **默认截帧（免费）**：用 ffmpeg 从成片挑高光帧（优先【钩子】段对应的画面时刻，`-q:v 1` 高质量导出）；可叠标题字（drawtext 用 imageio 构建，样式与字幕强调层一致）
- **AI 封面（仅用户明确要求）**：走 iskill-dig-media ai-image 协议——竖屏 1024x1536，prompt = 选题视觉描述 + 与成片一致的 style 后缀，落 `dig-media/ai-封面-<选题短名>/`，credits 事前确认，成品复制到成片目录
- 交付时注明封面来源（截帧/AI），AI 时附 credits 估算

### 封面标题字体库（内置 `fonts/`，免费可商用）

封面/标题卡/花字加字**优先用本目录字体**（样式预览见 `fonts/preview.png`），按气质选型：

| 文件 | 字体 | 气质 | 适用 |
|---|---|---|---|
| `fonts/YouSheBiaoTiHei.ttf` | 优设标题黑 | 前倾斜切、超粗、动势强 | **爆款封面默认首选**——短视频封面圈顶流，参考爆款图还原度最高 |
| `fonts/ZCOOLKuHei.ttf` | 站酷酷黑 | 方正超粗、正体、体量最大 | 极致冲击力场景（大字报式标题、关键词强调） |
| `fonts/PangMenZhengDaoBiaoTiTi.ttf` | 庞门正道标题体 | 端正收敛、现代黑 | 正文标题、正式感较强的选题 |
| `fonts/ZCOOLQingKeHuangYou.ttf` | 站酷庆科黄油体 | 圆头 butter 风、活泼亲和 | 轻松/趣味选题、生活类内容、副标题点缀 |

- **选型规则**：对标爆款封面/用户给参考图 → 优设标题黑；用户没要求 → 优设标题黑兜底；需要正体超重 → 站酷酷黑；忌讳斜体 → 庞门正道；轻松活泼调性 → 庆科黄油体
- 授权均为免费可商用（来源与授权详情见 `fonts/README.md`）；**用户指定字体时用户优先**
- HTML/HyperFrames 渲染：`@font-face` 声明本文件（注意 file:// 下 web font 被 CORS 拦截，需走本地 HTTP 或 base64 内联）；ffmpeg drawtext：`fontfile=<本目录绝对路径>`
- 三款均为单字重；粗细对比用「字号分级 + 描边/挤出」实现，勿指望字重族

## 接入五步工作流（第 6 步契约）

上游 skill 传来的输入，**命中任意一条即按本节走**：用户说「出成片」「剪成片」「做成片」「生成剪映草稿」「接着剪辑」，且工作区存在 `viral-video-team-output/文案/*-口播稿-v2.md` 或当天选题卡。

### 输入（按此优先级收集）

| 输入 | 位置 | 用法 |
|---|---|---|
| 定稿口播稿 v2 | `viral-video-team-output/文案/*-口播稿-v2.md`（无 v2 则用 `*-口播稿.md` 并提醒用户先过 deslop+预检） | **字幕唯一来源**：按段落注释（【钩子】等）分段，逐句上字幕；**禁止自行创作/改写字幕文案**——改动会绕过第 4、5 步的定稿。发现文案问题→退回 iskill-copy-deslop，不代改 |
| 预检报告 | `viral-video-team-output/文案/*-预检.md` | 结论必须是 ✅放行 或 ⚠️改后放行（已复检）；❌打回的不接单 |
| 素材 | 按下方「素材决策树」定位 | 照片+视频混合照常走 Phase 1 侦察；按口播稿段落语义选片（【价值】段的句子配对应素材镜头） |

### 素材决策树（不提供素材目录也能出片，多级回退 + 引擎档位）

**引擎档位（--engine）**：用户说「AIGC 出片」「AI 生成镜头」→ aigc-mix；「全 AI 出片」「纯 AI 生成」→ aigc-full；没提 AI 一律 local。用户用了 AI 关键词但档位模糊时，AskUserQuestion 确认并**报 credit 成本测算**。

```
用户指定了素材目录？
├─ 是 → 直接用（aigc-mix/full 下仍可对空缺镜头 AI 补镜）
└─ 否 → 工作区有 raw/ 目录且含音视频/照片？
        ├─ 是 → 用 raw/（优先自家实拍素材）
        └─ 否 → 工作区有 dig-media/ 目录且含可用素材？
                ├─ 是 → 用 dig-media/（网络素材库，查 manifest.json 确认内容对题）
                └─ 否 → 调用 iskill-dig-media 从网络挖掘：
                        1. 关键词从口播稿提取：拍摄提示段 > 段落语义 > 选题卡「内容形式」；
                           中文关键词翻成 2-4 组英文查询词（如「晒秋」→ autumn harvest / drying crops）
                        2. 每个段落语义挖 2-3 条，竖屏成片加 --min-width 1280
                        3. 素材落 dig-media/<关键词>/，沿用 manifest.json
                        4. 【按引擎档位】挖掘后仍有缺口：
                           ├─ local     → 到此为止，如实告知卡在哪一级（零素材样片规则）
                           ├─ aigc-mix  → 按 iskill-dig-media「AI 生成供给」协议补镜
                           │              （锚帧优先：关键叙事镜 ImageGen 锚帧→图生视频；空镜直接文生视频；
                           │               事前报 credits 估算并获用户确认，缓存查重防重复计费）
                           └─ aigc-full → 跳过图库直接全量 AI 生成：
                                          口播稿逐段 prompt 化（统一 style 后缀）→ 锚帧 → VideoGen
```

- **混用规则**：raw/ 素材优先入片，dig-media/ 补空缺镜头（空镜/氛围镜最适合用网络素材）。
- **标注义务**：成片使用了 dig-media 素材时，交付信息里注明「部分素材来自 Pixabay（可商用免署名），manifest.json 可溯源」。
- **零素材样片**：`--engine local` 下 raw/、dig-media/ 全无且挖掘失败时，明确告知用户卡在哪一级并给出补救动作（含「可改用 --engine aigc-mix 让 AI 补镜」的提示），不要凭空编造素材硬拼。
- dig-media 下载是网络重活，批量走后台执行（run_in_background）。
- **AIGC 镜头使用边界**：AI 镜头落盘 `dig-media/ai-<slug>/`，分镜表记录每镜的 prompt 与素材路径映射；交付信息注明「部分画面为 AI 生成」+ credits 估算（manifest 可溯源）。真实感选题（纪实/人物/手作）把 AI 镜头限定在空镜/氛围/转场镜。

### 音频开关（`--audio` / `--no-audio`，**默认开**）

用户没表态就按开处理；`--no-audio` 或「无声版/纯画面」才关。开启时三层各自级联，**每一层失败要明说，不静默跳过**：

**① 配音（台词声）级联：**

1. **用户自录音频**（真实感最好）→ 复用 iskill-media-transcribe 的 transcribe 阶段转成 srt，用 srt 时间轴驱动 drawtext，字幕与语音天然对齐；装了 whisper CLI（mlx-whisper）才有逐句时间戳，只有 VoiceBox 转写时是整段单块时间轴，此时按口播稿段落近似切分
2. **VoiceBox**（本地 TTS，`http://127.0.0.1:17493`，`VOICEBOX_URL` 可改）：
   - 探测 `GET /profiles`；**中文稿必须 `language:"zh"`**（male/child 档案走 qwen 引擎可出中文；female preset 档案只支持 kokoro 引擎=英文音色，中文会 400「only supports engine 'kokoro', not 'qwen'」）
   - 合成链：`POST /generate {profile_id, text, language}` → 轮询 `GET /history/{id}` 至 completed → `GET /audio/{id}` 存 WAV。qwen 引擎约 10-25s/句，**逐句合成 + 后台执行（run_in_background），并发 ≤2**
   - 段落时长 = max(字数估时, 配音时长 + 0.3s)，配音驱动分镜节奏
3. **VoiceStudio**（`http://localhost:3900`，`VOICESTUDIO_URL` 可改）在线则优先于 VoiceBox（MP3、更快、真人级音色）
4. 都不可用 → 无配音出片（BGM 仍在），交付时明确说「台词无声音」及原因

**② BGM 级联：** 用户指定 → 工作区 `bgm/` 目录有现成的 → 调 iskill-dig-media `music --kw "<对题英文音乐词>"` 自动挖 1 首。混音：`volume=0.15~0.2` 压在配音下 + 结尾 `afade=t=out`；**CC BY 许可的曲子要在交付信息里附署名**（manifest 里有 artist/license）。**BGM 一旦确定，立即调 iskill-music-beats 做节拍分析（见下节），转场对准节拍点**。

**③ 音效：** 默认跳过（Commons 音效质量杂、Pixabay 无音效 API）；用户给了 `sfx/` 目录才按段落插入。

**混音管线（ffmpeg 实锤）：** 逐段视频渲染（`-an`）→ 逐段配音 `apad` 补齐段长 → 画面/配音两轨分别 concat → `amix` 混 BGM（bgm 用 `-stream_loop` 拉到全片长）→ 最终 `-c:v copy -c:a aac`。

### BGM 节拍对齐（卡点转场，**有 BGM 时必做**）

BGM 确定后第一步就是节拍分析——**转场尽量打在节拍点上**，观众感知为"画面跟着音乐走"，成片质感立刻上一档。

**① 分析（调 iskill-music-beats）：**

```bash
PY=/Users/lv/.workbuddy/binaries/python/envs/default/bin/python
# BGM 循环铺底时只分析前 60s 即可，速度快
$PY ~/.workbuddy/skills/iskill-music-beats/scripts/beat_detect.py <bgm文件> --end 60 --json <bgm>.beats.json
```

产出 `beats.json`：`bpm` / `beat_interval`（平均节拍间隔）/ `beats`（节拍时间轴+强度）/ `strong_beats`（强节拍）/ `cut_candidates`（等距采样的最佳转场点池）。`note` 非空时是警告（无明确节拍的氛围曲），要转告用户并改用 fade 平缓转场、不强求卡点。

**② 分镜表卡节拍（Phase 3 选片时约束段长）：**

- 每段时长 = `beat_interval` 的整数倍（1x/2x/4x 按叙事节奏选），段边界对齐最近的强节拍
- 钩子段（0-3s）对齐开头第一个强拍后的落点；收尾段对齐渐弱前的强拍
- **配音约束优先于节拍**：段落时长公式 `dur = 0.8 + max(字数估时, 配音时长+0.8)` 不变，但把结果**向上取整到 `beat_interval` 的整数倍**，两边都满足

**③ 转场卡点（Phase 4 渲染）：**

- **gl 档（默认）**：转场=独立片段插在段间（非 xfade 重叠区），段边界落在节拍网格 + 转场片段时长=整数拍 → 转场中心天然落拍，无需 offset 计算（见下节「转场档位」）
- **xfade（回退档）**：转场**中心**落在 `offset + T/2`，要转场打在节拍 `t_b` 上：

```
offset_k = t_b - T/2        （T=转场时长，clamp ≥0）
```

操作顺序：先用节拍定好各段边界 `t_0=0, t_1, t_2…`，再按上式算每段 xfade offset（`offset_k = t_{k-1} - T/2` 对应"第 k 段起点处的转场打在 t_{k-1} 节拍上"）。段长为 `beat_interval` 整数倍时，各转场天然全落在节拍网格上。

**④ 验收加一项（Phase 5）：** 抽帧检查每个转场中点帧，对照 beats.json 确认转场时刻与节拍偏差 ≤ 0.1s。验证音轨可用 `--click` 生成的节拍 blip 与成片并播对比。

**⑤ 剪映草稿模式（Phase 7）同步对齐：** 段落 `start_time` 直接用节拍边界值（beats.json 的 t 就是草稿时间轴）；`add_transition_simple` 加在段边界处即天然卡点。

### 转场档位（Phase 4，--transitions）

**gl（默认）**：GPU shader 转场——段间转场渲染为独立「转场片段」（HyperFrames + @hyperframes/shader-transitions，WebGL 逐帧截帧）后 concat 回主链；卡片内（钩子/花字/CTA）多 scene 切换同样走 shader。**完整契约、架构图（整合地图 + 段间转场片段管线）、模板与已踩坑见 `reference/gpu-transitions.md`**，要点：

1. 转场点 **≤6 个/片**（每点渲染 +20~40s），优先【钩子】结束后第一转场、情绪高潮、CTA 前；其余转场点 xfade 或硬切
2. 转场片段时长 = beat_interval 整数倍（无 BGM 1.2~2s）；shader 窗口内缩 0.15s（`time:0.15, duration:T-0.3`），首尾各留纯 A/纯 B 帧保证 concat 连续
3. 模板库：`reference/templates/`（README 有使用流程）——`shader-transition-clip/`（转场片段，换 frameA/frameB/shader 名三处即可）、`hook-card/`（片头钩子+花字+CTA 三场景卡，10s）、`cover-card/`（三段式封面卡：冲击力标题+5张编号卖点卡弧形半包围+出镜主体羽化，3s，`ffmpeg -ss 0` 抽封面，**设计规范与验收清单见 `reference/cover-style-guide.md`**）；渲染 `npm run render`（需代理）
4. 每个转场片段交付前抽首尾帧与 A/B 对比校验；不干净的 shader 换掉。**shader 行为注意**（e2e 实测）：shader 转场普遍有 bgColor 参与相位（domain-warp 尾段撕裂露黑、light-leak 头段曝光黑场、cinematic-zoom/cross-warp-morph 长黑场）——首用 shader 必须**全程逐帧抽查**（`select='not(mod(n\,2))'`）；黑场压不满 1-2 帧时缩窗口（0.8~1.2s）读作闪切，或换 shader
5. 转场片段在 concat 前与相邻段归一编码（libx264/yuv420p/30fps/crf18），`-f concat -c copy` 硬拼

**xfade（回退）**：无 Chrome/WebGL 环境、用户点名「快速出片」、或 GL 渲染重试 1 次仍失败时按点降级使用（单点降级不打回整片，交付注明）。**none**：硬切。

gl 档成本提示：GL 转场渲染显著慢于 xfade（xfade 近零成本），交付信息注明用了几个 GL 点及渲染耗时。

### 输出契约

- 成片写 `{工作区}/viral-video-team-output/成片/YYYY-MM-DD-<选题短名>.mp4`（替代独立模式下的 `cuts/`）
- 剪映草稿名 `{选题短名}-精修`，草稿内字幕同样用定稿文案
- 交付时在消息里给：成片路径 + 分镜表摘要 + 「如需改文案请回 iskill-copy-deslop，别直接改字幕」的提示
- 工作流模式下**跳过 Phase 2 参考分析的「问三个问题」**（画幅/BGM/调性从上游推断：口播稿有拍摄提示段则遵照；拿不准只问缺的那一项）

## 独立剪辑模式（原生流程）

以下 Phase 0-7 适用于用户直接给素材目录的独立剪辑场景；工作流模式同样复用这些 Phase，只是字幕来源与产物目录按上面契约覆盖。

## Phase 0 环境自检（一次性）

**ffmpeg 探测决策树（先探测 brew 安装的 ffmpeg，能力够就直接用，别上来就装 imageio）：**

```bash
# ① 定位候选：PATH（含 brew link 的）→ Apple Silicon brew → Intel brew
FFMPEG=$(command -v ffmpeg 2>/dev/null || true)
[ -z "$FFMPEG" ] && [ -x /opt/homebrew/bin/ffmpeg ] && FFMPEG=/opt/homebrew/bin/ffmpeg
[ -z "$FFMPEG" ] && [ -x /usr/local/bin/ffmpeg ]   && FFMPEG=/usr/local/bin/ffmpeg

# ② 能力探测（关键一步）：产线要用的滤镜逐个验，齐了才算过关
$FFMPEG -hide_banner -filters 2>/dev/null | grep -E ' (drawtext|zoompan|xfade) '
```

- **brew ffmpeg 过关即用**：brew 公式（无论 Intel/Apple Silicon）自带 ffprobe，时长/流探测直接用，不必 grep Duration
- **候选缺失或缺 drawtext** → 装 imageio-ffmpeg 静态构建兜底：

```bash
PY=/Users/lv/.workbuddy/binaries/python/versions/3.13.12/bin/python3
$PY -m venv /Users/lv/.workbuddy/binaries/python/envs/default   # 已存在则跳过
/Users/lv/.workbuddy/binaries/python/envs/default/bin/pip install -q imageio-ffmpeg
FFMPEG=$(/Users/lv/.workbuddy/binaries/python/envs/default/bin/python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
```

- imageio 构建无 ffprobe：时长用 `ffmpeg -i 2>&1 | grep -oE "Duration: [0-9:.]+"` 解析（剪映草稿阶段另有 static_ffmpeg 补 ffprobe，见 Phase 7）
- 本构建含 libx264/aac，**不含 heic 解码**（iPhone heic 照片需先转或剔除）
- 中文字体：`/System/Library/Fonts/STHeiti Medium.ttc`（路径含空格，滤镜里用 `fontfile='...'` 单引号包裹）

## Phase 1 素材侦察

1. **时长普查**：所有视频 duration + 分辨率（`ffmpeg -i` grep Stream 行）
2. **抽帧**：每条视频取 20%/50%/80% 三帧（`-ss <t> -i in -frames:v 1 -vf scale=480:-1`），逐一查看，记录内容
3. **照片看板**：全部照片缩略图 → 5x5 拼图看板，按行列映射表快速识图
4. **输出**：素材→主题映射表（哪个镜头拍的是什么），这是选片依据

⚠️ **看板大坑（踩过实锤）**：`tile` 滤镜遇到输入帧参数不一致（尺寸/像素格式 yuvj420p vs yuv420p 混杂）会**提前刷出半空网格**（黑/白格子）。必须两步走：
- 先逐张归一化：`scale=200:200:force_original_aspect_ratio=decrease,pad=200:200:...,format=yuvj420p -q:v 3`
- 再 `concat demuxer`（不用 glob pattern_type）+ `tile=5x5`
- 混入 <5KB 的坏缩略图也会让 concat 中断，先清掉

## Phase 2 参考分析

- 有参考样片时：抽帧看风格（画幅/调色/节奏/字幕样式），**从样片提取 BGM**（`-vn -acodec copy` 提取音轨，约 10-11s，后续 `-stream_loop` 循环拉长 + afade 收尾）
- 没有参考时：问用户画幅（9:16 vs 16:9）、BGM 来源、字幕调性——三个问题一次问完

## Phase 3 选片与分镜表

三段式结构（15-30s）：
1. **开场钩子 0-3s**：空镜/氛围镜 + 大标题（explain 主题）
2. **过程叙事 3-22s**：4-5 个镜头按工序/时间线排列，照片 Ken Burns + 视频动作段穿插
3. **收尾 22-30s**：合影/意境镜 + 落款（「品牌 · 日期」）+ fade out

- 字幕文案「温馨纪实体」：短句、口语、有画面感（如「打出糯米的韧劲」），不用感叹号堆砌
- 照片横竖混排：竖图 fill 满屏裁切；横图人像群像用 blur 垫底（fit + boxblur 背景）
- Ken Burns 推拉交替 in/out 避免单调
- **有 BGM 时段长受节拍约束**：每段取 `beat_interval` 整数倍、边界对强节拍（详见「BGM 节拍对齐」节）

## Phase 4 构建

用 `reference/build_videos.py` 作模板：分镜表驱动（VIDEOS dict），逐镜头渲染 → concat → LOGO 叠加 → BGM 混音 → 输出。改分镜表即可复用。

关键技术点（全部实锤验证）：
- **Ken Burns 防抖**：先 `scale=2160:3840`（2x 超采样）再 `zoompan=...s=1080x1920`，直接在小图上 zoompan 会抖
- **zoompan 表达式**：in: `min(1+0.14*on/{frames},1.14)`；out: `max(1.14-0.14*on/{frames},1.0)`；居中 `x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'`
- **中文 drawtext**：文本写入临时文件用 `textfile=`（彻底避开转义地狱），定时用 `enable='between(t,a,b)'`
- **⚠️ drawtext 引擎（2026-09-30 实锤）**：Homebrew 公式默认**不带 freetype**——本机 `/opt/homebrew/bin/ffmpeg` 无 drawtext（有 drawgrid），**别假设 brew ffmpeg 能渲染字幕**。按 Phase 0 决策树先探测：brew ffmpeg 若带 drawtext（部分第三方 tap 构建）直接用、白得 ffprobe；没有才切 imageio-ffmpeg 静态构建：
  `/Users/lv/.workbuddy/binaries/python/envs/default/lib/python3.13/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1`（drawtext/libx264 齐全）。不管用哪个引擎，产线开跑前都再 `-filters | grep drawtext` 验一遍。
- **超长句换行**：drawtext 不自动折行，>16 字的句子在 textfile 里手动 `\n` 断行（一行 ≤16 字，fontsize 52 @ 1080 宽）
- **字幕要有设计感（2026-09-30 实锤，三层）**：
  1. **底部渐变压条**：`geq=r=0:g=0:b=0:a=153*Y/359` 生成 1080x360 透明→黑渐变 png，成片级 `overlay=0:main_h-overlay_h` 全程压底（综艺感，字幕不再浮在画面上）
  2. **描边+阴影替代灰底框**：`borderw=4:bordercolor=black@0.88:shadowcolor=black@0.55:shadowx=2:shadowy=3`，比 box 底条通透
  3. **强调句分层**：钩子/金句用金色 `0xFFC93C` + 62 号，普通句白色 54 号；每句 `alpha='if(lt(t,a+0.25),(t-a)/0.25,1)'` 淡入
- **照片素材必须动（Ken Burns，工作流管线版）**：`-loop 1 -t dur` 输入 → `scale=2160:3840...crop=2160:3840`（2x 超采样防抖）→ `zoompan=z='min(1+0.10*on/F,1.10)'`（推近）或 `z='max(1.10-0.10*on/F,1.0)'`（拉远），`x/y` 居中，`d=1:s=1080x1920:fps=25`，F=25*段长；相邻段交替 in/out
- **视频段慢平移微动效**：1.15x 放大（`scale=1242:2208`）+ 动画 crop `crop=1080:1920:x='(iw-ow)*min(t/DUR,1)':y='(ih-oh)/2'`（crop 支持 t 表达式，左右轮换；比 zoompan 稳，无抖动）
- **场景转场（concat 硬切的原罪解法）**：xfade 链——`[v0][v1]xfade=transition=fade:duration=0.4:offset=D0-0.4[vx1]`，`offset_k = Σ前k段时长 - k×转场时长`，链到最后一层；**有 BGM 时 offset 换用节拍公式 `offset = t_b - T/2` 让转场打在节拍上**（详见「BGM 节拍对齐」节）；**音频必须同步 acrossfade 同参数**，否则画面字幕与配音漂移。转场类型对调性选：fade/dissolve 平缓、smoothleft/right 干净、zoomin 收尾有力
- **⚠️ 转场与配音的协调铁律**：转场吃掉每段首尾各 T/2 的重叠区——每段音轨必须 `adelay=500`（头垫）+ `apad`（尾垫），保证**人声不进转场区**（头垫 ≥ 转场时长 + 0.1s）；段长公式 `dur = 0.8 + max(字数估时, 配音时长+0.8)`
- **字幕样式**：白字 + `box=1:boxcolor=black@0.34:boxborderw=18` 半透明底条（快速档；有设计感用上面三层方案）
- **逐镜头编码再 concat**：concat demuxer 要求参数完全一致（同分辨率/帧率/编码），先统一 `fps=25, format=yuv420p` 再拼
- **BGM**：`-stream_loop 50 -i bgm.m4a` + `atrim=0:总长,afade=t=out:st=总长-1.8:d=1.8,volume=0.9`
- **LOGO**：RGBA png `scale=150:150,colorchannelmixer=aa=0.78` + overlay 右上角，单帧输入 overlay 自动 repeat
- **低清源锐化**：720p 航拍放大到 1080x1920 加 `unsharp=5:5:0.6`
- **暗镜头提亮**：`eq=brightness=0.05:gamma=1.08:saturation=1.05`
- **已知无害问题**：全照片管线产出 yuvj420p（全 range 标记，format=yuv420p 不转换它，别名关系），全片自洽、播放无碍

## Phase 5 验收（必做）

`ffmpeg -i 成片 -vf fps=1,scale=360:-1 check_%02d.jpg` 逐帧抽查：
- 中文字幕是否渲染（不是豆腐块/不缺字）
- 标题/落款/LOGO 位置
- 镜头顺序与分镜表一致（**照片文件名↔内容映射极易记错，验收抓错位**——本项目实锤：221810 被错记为贴花，实为打糍粑）
- Ken Burns 是否在动、压模/特写段是否对准时间点
- **有 BGM 时**：转场中点帧对照 beats.json，卡点偏差 ≤ 0.1s
- **AIGC 镜头（aigc-mix/full）**：抽帧看风格一致性（色调/光影是否与整片协调，锚帧镜头是否漂移成另一风格）；不协调的镜头换 prompt 重生成（重计费，需用户确认）或 dig-media 图库替换

## Phase 6 交付

独立模式：成片输出 `cuts/` 命名 `1_主题.mp4`；工作流模式：输出 `viral-video-team-output/成片/YYYY-MM-DD-<选题短名>.mp4`（见顶部接入契约）。用 present_files 交付。BGM 若取自参考样片，提醒用户可指定替换（分镜表 bgm 字段一行改动）。

## Phase 7 专业模式：剪映草稿精修（可选，强烈推荐）

ffmpeg 直出适合快速交付；要**专业级成片**（真转场、文本动画、剪映特效/贴纸/曲库、关键帧运镜、手动精修），生成**剪映专业版草稿**，用户在剪映里预览微调后导出。

### 前置条件（检测）
- 剪映专业版：`/Applications/剪映专业版`；草稿根：`~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft`
- 依赖技能：`~/.workbuddy/skills/jianying-editor`（第三方 luoluoluo22/jianying-editor-skill，MIT；已过安全审计：网络出口仅剪映官方域名，无危险调用）
- Python 依赖（managed venv）：`pymediainfo`（自带 libmediainfo，媒体解析）、`static-ffmpeg`（补 ffprobe，wheel 自带无需联网）、`edge-tts requests psutil`

### 用法（模板 reference/jianying_drafts.py）
```python
os.environ["JY_SKILL_ROOT"] = os.path.expanduser("~/.workbuddy/skills/jianying-editor")
from static_ffmpeg import run as _sf_run          # 注入 ffprobe 进 PATH，视频素材必须
_ff,_fp = _sf_run.get_or_fetch_platform_executables_else_raise()
os.environ["PATH"] = os.path.dirname(_ff) + os.pathsep + os.environ["PATH"]
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))
from jy_wrapper import JyProject
proj = JyProject(project_name=f"xxx-精修", width=1080, height=1920, overwrite=True)
seg = proj.add_media_safe(path, start_time="0s", duration="3s", source_start="36s", track_name="主轨")
proj.add_transition_simple("叠化", video_segment=seg, duration="0.6s")   # 转场名见 vendor pyJianYingDraft transition_meta.py，支持模糊匹配
proj.add_text_simple("字幕", start_time="0.3s", duration="2.4s", track_name="文本")
proj.add_audio_safe(bgm, start_time="0s", duration="11.5s", track_name="BGM")
proj.save()
```

### 实锤要点
- 草稿根目录自动探测（macOS 路径吻合）；素材自动复制进草稿 materials/ **自包含**，无沙盒媒体丢失问题
- 视频素材探测链：pymediainfo → ffprobe fallback；**没有 ffprobe 时纯照片草稿能成、含视频草稿直接失败**（Errno 2 'ffprobe'），所以先注入 static_ffmpeg 的 ffprobe。brew 装了 ffmpeg 时优先用其自带 ffprobe（`/opt/homebrew/bin/ffprobe` 或 `/usr/local/bin/ffprobe`），static_ffmpeg 仅作兜底
- 草稿生成后剪映**不会实时刷新**：需重启剪映，或随便进出一个旧草稿后再看
- 校验：`python <skill>/scripts/draft_inspector.py summary --name "草稿名"`
- 首次失败残留的空草稿会被技能 Auto-healing 自动清理，不碍事
- macOS 不支持自动导出：**最终导出在剪映内手动完成**（自动导出仅 Windows UI 自动化）

### 双引擎选择
- **快出片/无人值守** → ffmpeg 管线（Phase 4），几分钟全自动
- **精修/专业质感** → 剪映草稿模式（Phase 7），转场+动画+剪映曲库特效，人工微调后导出
- 两条引擎共用同一份分镜表（镜头序、时长、文案、BGM 分配完全一致），可同时出「快速版 + 精修版」

### capcut-mate 评估结论（未采用）
FastAPI 服务型项目（需常驻本地服务或 Docker，依赖 COS/OSS/TOS 云 SDK），云渲染导出走作者云服务（jcaigc.cn）。适合 Coze/n8n 平台工作流场景；本地 Agent 场景下 jianying-editor-skill 直写草稿更轻。若未来要接 Coze/n8n 或云端渲染再启用。
