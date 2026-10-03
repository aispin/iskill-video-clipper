# MoneyPrinterTurbo 接入调研（2026-10-03）

> 调研对象：https://github.com/harry0703/MoneyPrinterTurbo （v1.3.8，2026-10-03）
> 结论先行：**适合接入，但只接「素材/补镜」子能力为主，不接管成片主链路。**
> 所属板块：**第 6 步「出片」板块**（成片合成），子能力分别落在 `iskill-dig-media`（素材）与「发布」板块。

---

## 一、项目画像

| 维度 | 事实 |
|---|---|
| 定位 | 主题/关键词 → 脚本 → 素材 → 配音 → 字幕 → BGM → 成片 的一站式合成器 |
| 热度 | ~123k stars，本项目类别 GitHub 第一 |
| License | **MIT**（可商用可改） |
| 活跃度 | 极高：v1.3.3→v1.3.8 之间每周一版，最新版就是今天发的 |
| 技术栈 | Python 3.11+ / **uv**（强制）/ MoviePy + ffmpeg / Docker 可选 |
| 使用入口 | WebUI / API / CLI / **官方 AI Agent Skill**（`docs/skill/SKILL.md` + `mpt_agent.py`） |
| 素材源 | Pexels/Pixabay/Coverr（免费）+ 本地文件 + **6+ 家 AI 文生视频**（Seedance/Wan/WaveSpeed/MuAPI/MiniMax H3/OFox/OpenAI 文生图） |
| 配音 | Edge TTS（免费无 key）/ Azure / ElevenLabs / Gemini / MiniMax / Kokoro / VoxCPM 等 11 种，支持 `--custom-audio-file` 传入现成配音 |
| 字幕 | edge 时间戳（快、无 GPU）或本地 faster-whisper（更准、3GB 模型）；逐词字幕 + pop_spring 动画 |
| 依赖 key | LLM provider key（必）+ Pexels key（素材，免费注册）；AI 文生视频各 provider 单独 key |

### 关键 CLI 能力（决定接入形态）

- `--video-script`：**可传我们自己的成稿文案**，跳过它的 LLM 脚本环节 ✅
- `--custom-audio-file`：**可传我们 edge-tts 已生成的配音**，跳过它的 TTS ✅
- `--video-materials` + `--video-source local`：可喂本地素材，但**只收逗号分隔的文件路径、不收目录**（agent 侧拼列表即可）
- `--stop-at script|terms|audio|subtitle|materials|video`：**可只跑到素材阶段就停** ✅✅ —— 这是「只借素材、不借合成」的原生开关
- 转场仅 `none/shuffle/fade/slide/zoom`，**无 shader、无节拍卡点**
- 产物路径**不可指定**（固定 `storage/tasks/<task-id>/`），需事后搬运

---

## 二、板块归属

| 板块 | 关系 | 说明 |
|---|---|---|
| **第 6 步「出片」（成片合成）** | **主归属**，与 `iskill-video-clipper` 同位 | 只能作为**引擎档位之一**（快速草稿档），不能当主交付引擎 |
| `iskill-dig-media`（素材板块） | 子能力可拆借 | 关键词自动搜素材 + **AI 文生视频多模型聚合路由**（我们 aigc-mix/aigc-full 现在要逐家接 API，它已聚合 6+ 家且自带计费确认机制） |
| 「发布」板块 | 链路目前唯一空白 | 它带 TikTok/YT Shorts/IG 一键发布；**国内平台（视频号/抖音/小红书）无效**，价值有限 |
| 第 1–5 步（选题/拆解/文案/去AI味/预检） | **不适用** | 它的 LLM 脚本能力被我们「四平台四套 + deslop + 预检」全面覆盖且更强 |

---

## 三、三种接入形态

### 形态 B（推荐主接）：只借「素材 + 补镜」，不借合成
```
我们的文案 → --video-script（可选）
         → --stop-at materials → MPT 去搜/生成素材
         → 素材回填 dig-media/ → 仍由 iskill-video-clipper 出片
```
- **零质量倒退**：gl 转场、节拍卡点、「文案↔画面关联性自检」三道硬门禁全部保留
- 借到的东西：① Pexels/Pixabay 关键词自动匹配下载；② **6+ 家 AI 文生视频聚合 + 统一计费确认**（`*_CHARGE_CONFIRMATION_REQUIRED` 退出码机制，与我们团队 MD 的「credits 事前确认」铁律同构）
- 用 `--stop-at terms` 还能只拿「文案→搜索关键词」的中间产物，喂给我们自己的素材挖掘

### 形态 A（可选副档）：整片交给 MPT 合成（快速草稿档）
```
--video-script <我们的成稿> --custom-audio-file <我们的配音>
--video-source local --video-materials <素材文件列表> --video-source local
```
- 优点：一条命令出整片，字幕/BGM/拼接全自动，批量（`--batch-file`，≤100 任务）
- **硬约束**：它无节拍卡点、转场只有 fade/slide/zoom → 走这档=放弃三道硬门禁
- **定位必须是「快速草稿/内部预览」，交付信息必须标注 `engine=mpt 草稿档，未过卡点/转场门禁`**，不得冒充主交付档

### 形态 C（不接）：连文案一起让它生成
- 直接 `--video-subject` 让它写脚本 → 丢掉四套文案/deslop/预检全部资产，且产出一眼 AI 味。**否决**。

---

## 四、落地风险与前置条件（务实项）

1. ~~沙箱装不动~~ **【已被 P1 实测推翻】**：`uv run` 能在沙箱内正常建 venv + 装全量锁死依赖（MoneyPrinterTurbo 全家桶 **17s** 装完），**uv 绕过了沙箱 pip broker 拦截**。真正的坑是 pip，不是 uv。
2. **key 准备**：LLM key（任意一家）+ Pexels key（免费）；按约定 key/配置放 `ISkills/.workbuddy/`。**但 `--video-script + --video-terms + --custom-audio-file + --video-source local` 组合可全程零 key**（P1 已实测）。
3. **安全**：v1.2.x 及更早有 6 个已知 CVE；WebUI/API **无鉴权**（默认绑 127.0.0.1）。→ **只走 CLI，永不起 WebUI/API 服务**（官方 agent skill 也是这么约束的）。
4. **版权**：仓库内置 BGM 来自 YouTube，README 自注「如有侵权请删除」→ 我们链路用自己 dig-media 的 BGM，别用它的内置曲库。
5. **产物路径**：输出固定在它的 `storage/tasks/<id>/`，接入层要负责搬到我们的 `成片/` 并按命名规范重命名。
6. **串行**：官方明确不支持并发任务，操盘团多分支并行时要注意排队。
7. **体积**：whisper 路线要下 3GB 模型；我们默认走 edge 时间戳字幕，可绕开。仓库本体浅克隆 348MB（大头是内置曲库/字体）。

---

## 四点五、P1 实测结果（2026-10-03，沙箱内，零 API key）

| # | 验证项 | 命令要点 | 结果 |
|---|---|---|---|
| 1 | 环境搭建 | `uv run python cli.py --help` | ✅ **17s** 装完全量锁死依赖并跑通（uv 绕过沙箱 pip 拦截） |
| 2 | 传我们自己的成稿 | `--video-script "<成稿>" --stop-at script` | ✅ exit 0，成稿**原样回显**（跳过它的 LLM） |
| 3 | 传搜索关键词 | `--video-terms "果园,秋天,采摘" --stop-at terms` | ✅ exit 0，terms 原样返回（不调 LLM） |
| 4 | 注入我们的配音 | `--custom-audio-file <vo1.mp3> --stop-at audio` | ✅ exit 0，识别时长 **5.78s**（我们 edge-tts 产物直接可用） |
| 5 | 喂本地素材 | `--video-source local --video-materials "<逗号分隔路径>" --stop-at materials` | ✅ 3 张 dig-media jpg → 各自生成 `.zoom-5.mp4`（Ken Burns） |
| 6 | **零 key 整片直出** | 上面四项合起来 + `--stop-at video` | ✅ **1m15s** 出 `final-1.mp4`（1080×1920 / 5.8s / 174 帧 / aac），产物已归档 `成片/2026-10-03-MPT零key直出-验证.mp4` |

### 实测暴露的三个短板（决定「只借素材、不借合成」的结论更成立）

1. **CLI 字幕是坏的**：`subtitle maker is missing, skip subtitle generation for provider: edge` → `subtitle_path` 为空，成片**没有字幕**。我们链路本来就自己做字幕（imageio 静态构建 ffmpeg），不受影响，但别指望它替你上字幕。
2. **竖屏适配默认 `cover`**：横屏 1280×853 源被硬裁成 1080×1920——正是我们记录过的「cover 裁切腰斩」问题；它只有 `cover/contain`（黑边）两档，**没有 blur-fill**。→ 横屏素材走它的合成，画质必然不如我们自己的 blur-fill 管线。
3. **段长逻辑是「音频驱动」不是「节拍驱动」**：配音 5.78s → 需要 5.88s → 每段 5s，4 个素材只用了 2 个。没有卡拍概念，切点与 BGM 各走各的（与我们刚修掉的 PPT 味同源问题）。

> **P1 结论**：接入可行且成本比预想低（沙箱即可，无需真机）；但它的合成档位**全面弱于**我们的主链路——**形态 B（只借素材/补镜）的价值被实测进一步坐实**。

---

## 五、分阶段落地建议

| 阶段 | 动作 | 验收 |
|---|---|---|
| P1 验证 | 真机 `git clone` 到 `ISkills/deps/moneyprinterturbo/`，uv 装环境，跑 `uv run cli.py --video-script "<一段成稿>" --stop-at terms` | 能产出关键词 JSON；LLM key + Pexels key 配置复用正常 |
| P2 素材档 | 跑 `--stop-at materials`，素材回填 `dig-media/`；`iskill-dig-media` 增补「MPT 聚合素材档」一节 | 拿到可用的素材文件清单；AI 文生视频计费确认机制实测一次 |
| P3 草稿档 | `iskill-video-clipper` 增 `--engine mpt`（草稿档），SKILL.md + 团队 MD 同步「mpt 档未过三道门禁须标注」 | 一条成片走通 `--video-script + --custom-audio-file + local 素材`，交付说明带档位标注 |
| P4 固化 | 团队主理人 MD 判别表加「mpt 引擎档位」；专家包重打包 | validate/register/package 全绿 |

> 接入姿势遵守项目约定：**MPT 是「一份真源」（不改它源码），我们只在 agent 侧写薄封装**；不 fork、不翻译第二份逻辑。
