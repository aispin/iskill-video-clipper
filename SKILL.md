---
name: iskill-video-clipper
description: 实拍素材短视频剪辑（照片+视频混合 → 15-60s 成片/剪映草稿）。两种入口：①独立剪辑——用户要求"剪视频/切条/做成片/活动视频剪辑"并给素材目录；②五步爆款工作流第 6 步——输入 文案/ 下的定稿口播稿（v2）+ 预检通过的选题，字幕用定稿文案、按需配音对齐，产出成片或剪映工程。全流程本地 ffmpeg，免费无付费环节。
---

# iskill-video-clipper 实拍素材短视频剪辑

把「照片 + 视频」原始素材剪成带标题、字幕、LOGO、BGM 的短视频成片。核心理念：**先侦察再剪辑**——绝不在没看过素材内容前动手。

```
六步爆款工作流：[1]选题(hot-topic-scout) → [2]拆解(viral-teardown) → [3]文案(viral-copywriter)
→ [4]去AI味+点评(copy-deslop) → [5]预检(content-precheck) → [6]成片/剪映草稿(本skill)
```

## 接入五步工作流（第 6 步契约）

上游 skill 传来的输入，**命中任意一条即按本节走**：用户说「出成片」「剪成片」「做成片」「生成剪映草稿」「接着剪辑」，且工作区存在 `文案/*-口播稿-v2.md` 或当天选题卡。

### 输入（按此优先级收集）

| 输入 | 位置 | 用法 |
|---|---|---|
| 定稿口播稿 v2 | `文案/*-口播稿-v2.md`（无 v2 则用 `*-口播稿.md` 并提醒用户先过 deslop+预检） | **字幕唯一来源**：按段落注释（【钩子】等）分段，逐句上字幕；**禁止自行创作/改写字幕文案**——改动会绕过第 4、5 步的定稿。发现文案问题→退回 iskill-copy-deslop，不代改 |
| 预检报告 | `文案/*-预检.md` | 结论必须是 ✅放行 或 ⚠️改后放行（已复检）；❌打回的不接单 |
| 素材目录 | 用户指定 | 照片+视频混合照常走 Phase 1 侦察；按口播稿段落语义选片（【价值】段的句子配对应素材镜头） |
| 配音音轨（可选） | 用户自录音频文件 | 见下方「配音与字幕对齐」 |

### 配音与字幕对齐（口播稿成片的关键，二选一）

- **用户自录**（默认，真实感最好）：拿到音频后**复用 iskill-media-transcribe 的 transcribe 阶段**（`node scripts/video-transcribe.mjs transcribe <mp3>`）把配音转成 srt——再用 srt 时间轴驱动 drawtext 字幕，字幕与语音天然对齐。装了 whisper CLI（mlx-whisper）才有逐句时间戳，只有 VoiceBox 时是整段单块时间轴，此时按口播稿段落近似切分。
- **无配音**：BGM-only + 字幕按段落注释估时分段（每句时长≈字数/5.5 秒，段落注释间均分）。
- TTS 配音（VoiceBox/VoiceStudio）仅在用户明确要求时用，产出后同样走上面的转写对齐链路。

### 输出契约

- 成片写 `{工作区}/成片/YYYY-MM-DD-<选题短名>.mp4`（替代独立模式下的 `cuts/`）
- 剪映草稿名 `{选题短名}-精修`，草稿内字幕同样用定稿文案
- 交付时在消息里给：成片路径 + 分镜表摘要 + 「如需改文案请回 iskill-copy-deslop，别直接改字幕」的提示
- 工作流模式下**跳过 Phase 2 参考分析的「问三个问题」**（画幅/BGM/调性从上游推断：口播稿有拍摄提示段则遵照；拿不准只问缺的那一项）

## 独立剪辑模式（原生流程）

以下 Phase 0-7 适用于用户直接给素材目录的独立剪辑场景；工作流模式同样复用这些 Phase，只是字幕来源与产物目录按上面契约覆盖。

## Phase 0 环境自检（一次性）

```bash
PY=/Users/lv/.workbuddy/binaries/python/versions/3.13.12/bin/python3
$PY -m venv /Users/lv/.workbuddy/binaries/python/envs/default   # 已存在则跳过
/Users/lv/.workbuddy/binaries/python/envs/default/bin/pip install -q imageio-ffmpeg
FFMPEG=$(/Users/lv/.workbuddy/binaries/python/envs/default/bin/python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
```

- 无 Homebrew 时的 ffmpeg 获取方式；无 ffprobe，时长用 `ffmpeg -i 2>&1 | grep -oE "Duration: [0-9:.]+"` 解析
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

## Phase 4 构建

用 `reference/build_videos.py` 作模板：分镜表驱动（VIDEOS dict），逐镜头渲染 → concat → LOGO 叠加 → BGM 混音 → 输出。改分镜表即可复用。

关键技术点（全部实锤验证）：
- **Ken Burns 防抖**：先 `scale=2160:3840`（2x 超采样）再 `zoompan=...s=1080x1920`，直接在小图上 zoompan 会抖
- **zoompan 表达式**：in: `min(1+0.14*on/{frames},1.14)`；out: `max(1.14-0.14*on/{frames},1.0)`；居中 `x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'`
- **中文 drawtext**：文本写入临时文件用 `textfile=`（彻底避开转义地狱），定时用 `enable='between(t,a,b)'`
- **字幕样式**：白字 + `box=1:boxcolor=black@0.34:boxborderw=18` 半透明底条（视频号风格）
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

## Phase 6 交付

独立模式：成片输出 `cuts/` 命名 `1_主题.mp4`；工作流模式：输出 `成片/YYYY-MM-DD-<选题短名>.mp4`（见顶部接入契约）。用 present_files 交付。BGM 若取自参考样片，提醒用户可指定替换（分镜表 bgm 字段一行改动）。

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
- 视频素材探测链：pymediainfo → ffprobe fallback；**没有 ffprobe 时纯照片草稿能成、含视频草稿直接失败**（Errno 2 'ffprobe'），所以先注入 static_ffmpeg 的 ffprobe
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
