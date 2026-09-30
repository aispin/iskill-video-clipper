---
name: iskill-video-clipper
description: 实拍素材短视频剪辑（照片+视频混合 → 15-60s 成片/剪映草稿）。两种入口：①独立剪辑——用户要求"剪视频/切条/做成片/活动视频剪辑"并给素材目录；②五步爆款工作流第 6 步——输入 文案/ 下的定稿口播稿（v2）+ 预检通过的选题，字幕用定稿文案、按需配音对齐，产出成片或剪映工程。素材支持零输入：raw/ → dig-media/ → 自动调 iskill-dig-media 网络挖掘三级回退。全流程本地 ffmpeg，免费无付费环节。
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
| 素材 | 按下方「素材决策树」定位 | 照片+视频混合照常走 Phase 1 侦察；按口播稿段落语义选片（【价值】段的句子配对应素材镜头） |

### 素材决策树（不提供素材目录也能出片，三级回退）

```
用户指定了素材目录？
├─ 是 → 直接用
└─ 否 → 工作区有 raw/ 目录且含音视频/照片？
        ├─ 是 → 用 raw/（优先自家实拍素材）
        └─ 否 → 工作区有 dig-media/ 目录且含可用素材？
                ├─ 是 → 用 dig-media/（网络素材库，查 manifest.json 确认内容对题）
                └─ 否 → 调用 iskill-dig-media 从网络挖掘：
                        1. 关键词从口播稿提取：拍摄提示段 > 段落语义 > 选题卡「内容形式」；
                           中文关键词翻成 2-4 组英文查询词（如「晒秋」→ autumn harvest / drying crops）
                        2. 每个段落语义挖 2-3 条，竖屏成片加 --min-width 1280
                        3. 素材落 dig-media/<关键词>/，沿用 manifest.json
```

- **混用规则**：raw/ 素材优先入片，dig-media/ 补空缺镜头（空镜/氛围镜最适合用网络素材）。
- **标注义务**：成片使用了 dig-media 素材时，交付信息里注明「部分素材来自 Pixabay（可商用免署名），manifest.json 可溯源」。
- **零素材样片**：raw/、dig-media/ 全无且挖掘失败（无 key/断网）时，明确告知用户卡在哪一级并给出补救动作，不要凭空编造素材硬拼。
- dig-media 下载是网络重活，批量走后台执行（run_in_background）。

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

**② BGM 级联：** 用户指定 → 工作区 `bgm/` 目录有现成的 → 调 iskill-dig-media `music --kw "<对题英文音乐词>"` 自动挖 1 首。混音：`volume=0.15~0.2` 压在配音下 + 结尾 `afade=t=out`；**CC BY 许可的曲子要在交付信息里附署名**（manifest 里有 artist/license）。

**③ 音效：** 默认跳过（Commons 音效质量杂、Pixabay 无音效 API）；用户给了 `sfx/` 目录才按段落插入。

**混音管线（ffmpeg 实锤）：** 逐段视频渲染（`-an`）→ 逐段配音 `apad` 补齐段长 → 画面/配音两轨分别 concat → `amix` 混 BGM（bgm 用 `-stream_loop` 拉到全片长）→ 最终 `-c:v copy -c:a aac`。

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
- **⚠️ drawtext 引擎实锤（2026-09-30）**：本机 `/opt/homebrew/bin/ffmpeg` 无 drawtext（构建缺 freetype，有 drawgrid）！渲染字幕必须用 imageio-ffmpeg 静态构建：
  `/Users/lv/.workbuddy/binaries/python/envs/default/lib/python3.13/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1`（drawtext/libx264 齐全）。用前先 `-filters | grep drawtext` 验一下。
- **超长句换行**：drawtext 不自动折行，>16 字的句子在 textfile 里手动 `\n` 断行（一行 ≤16 字，fontsize 52 @ 1080 宽）
- **字幕要有设计感（2026-09-30 实锤，三层）**：
  1. **底部渐变压条**：`geq=r=0:g=0:b=0:a=153*Y/359` 生成 1080x360 透明→黑渐变 png，成片级 `overlay=0:main_h-overlay_h` 全程压底（综艺感，字幕不再浮在画面上）
  2. **描边+阴影替代灰底框**：`borderw=4:bordercolor=black@0.88:shadowcolor=black@0.55:shadowx=2:shadowy=3`，比 box 底条通透
  3. **强调句分层**：钩子/金句用金色 `0xFFC93C` + 62 号，普通句白色 54 号；每句 `alpha='if(lt(t,a+0.25),(t-a)/0.25,1)'` 淡入
- **照片素材必须动（Ken Burns，工作流管线版）**：`-loop 1 -t dur` 输入 → `scale=2160:3840...crop=2160:3840`（2x 超采样防抖）→ `zoompan=z='min(1+0.10*on/F,1.10)'`（推近）或 `z='max(1.10-0.10*on/F,1.0)'`（拉远），`x/y` 居中，`d=1:s=1080x1920:fps=25`，F=25*段长；相邻段交替 in/out
- **视频段慢平移微动效**：1.15x 放大（`scale=1242:2208`）+ 动画 crop `crop=1080:1920:x='(iw-ow)*min(t/DUR,1)':y='(ih-oh)/2'`（crop 支持 t 表达式，左右轮换；比 zoompan 稳，无抖动）
- **场景转场（concat 硬切的原罪解法）**：xfade 链——`[v0][v1]xfade=transition=fade:duration=0.4:offset=D0-0.4[vx1]`，`offset_k = Σ前k段时长 - k×转场时长`，链到最后一层；**音频必须同步 acrossfade 同参数**，否则画面字幕与配音漂移。转场类型对调性选：fade/dissolve 平缓、smoothleft/right 干净、zoomin 收尾有力
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
