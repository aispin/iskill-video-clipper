# iskill-video-clipper 双引擎方案：程序化合成 + AIGC 合成

> 状态：**已确认并实施（2026-09-30）**。决策：归属 A（dig-media 升级素材供给中心）+ 三档全做（local/aigc-mix/aigc-full）+ 锚帧优先 + 每次成本确认 + video-fx 进 roadmap。已落地至两仓 SKILL.md 并推送 GitHub。本文档留档需求分析过程。

## 一、需求整理

### 现状（程序化合成）
iskill-video-clipper 的产出方式是**素材拼接**：实拍/图库素材 → ffmpeg 管线（Ken Burns、xfade 转场、drawtext 字幕、配音、BGM 节拍卡点）。画面 100% 来自真实素材，**不产生任何新画面**。

### 用户诉求
- WorkBuddy 是否有 AIGC 视频能力？→ **有**（见下表）
- 给 clipper 加一个**分支命令**：用户可选「程序化合成」或「AIGC 合成」

### 隐含需求（分析得出）
1. 成本可控：AIGC 按 credit 计费，必须**生成前确认预算**，且**缓存生成结果**避免重复烧钱
2. 风格一致性：逐镜独立生成的 AI 画面容易风格漂移，需要风格锚点机制
3. 兼容既有契约：字幕来自定稿口播稿、BGM 卡点、产物目录、预检放行——这些**不应被 AIGC 模式绕过**
4. 分支边界清晰：AIGC 改变的只是「画面从哪来」，不是新的剪辑管线

## 二、WorkBuddy AIGC 能力盘点（实测工具）

| 能力 | 工具 | 成本 | 时延 | 适配度 |
|---|---|---|---|---|
| 文生视频（text-to-video） | VideoGen（内置工具） | **约 50-100 credits / 5 秒** | 1-3 分钟/条 | ⭐ 核心能力 |
| 图生视频（首帧/尾帧驱动） | VideoGen `image` / `last_image` | 同上 | 1-3 分钟 | ⭐ 让图动起来 |
| 文生图 / 图改图 | ImageGen | 5-10 credits/张 | 秒级 | ⭐ 风格锚帧、封面 |
| 模板图生视频（人物互动/风格化/连续故事 2-10 图） | buddy-multimodal-generation `video-fx` | credit | 1-5 分钟 | 特定场景（如 onestory 连续故事） |
| 实拍 + Pixabay 图库 | 本地 + iskill-dig-media | 免费 | 快 | 现有路径 |

VideoGen 参数要点：支持 720P/1080P、16:9/9:16/1:1、negative_prompt、`enable_audio`（**必须关**——AI 音轨会与配音/BGM 冲突，声音一律由我们的管线负责）。

## 三、关键分析

### 3.1 核心洞察：AIGC 不是新管线，是新的「素材供给层」
clipper 的管线（选片→分镜表→渲染→验收→交付）与素材来源天然解耦——素材决策树现在是 `用户目录 → raw/ → dig-media/ → dig-media 挖掘`。**AIGC 只需成为决策树的新一级供给源**，字幕、配音、BGM 卡点、产物目录全部契约原样复用。

### 3.2 成本测算（9:16 竖屏、1080P）
| 模式 | 30s 成片（6 镜） | 60s 成片（12 镜） | 说明 |
|---|---|---|---|
| local（现状） | 0 | 0 | 免费 |
| aigc-mix（混合） | ≈2-3 镜 AI ≈ **100-300 credits** | ≈200-600 | 只补缺的镜头 |
| aigc-mix 图驱动 | ≈**60-150 credits** | 更低 | ImageGen 锚帧(便宜)→图生视频 |
| aigc-full（全 AI） | ≈**300-600 credits** | ≈600-1200 | 全部镜头生成 |

### 3.3 三个技术决策点
1. **段长匹配**：VideoGen 单条约 5s，我们的分镜段 2-8s → 生成 5s 源片，段内用已有「慢平移/crop 微动效」截取所需时长，天然与节拍卡点兼容
2. **风格一致性**：统一 style 后缀（调性关键词 + 光影 + 色调写进每条 prompt）+ 关键镜用 ImageGen 先出锚帧再图生视频
3. **缓存**：生成镜头落 `成片/aigc-cache/`，分镜表记录 prompt→素材映射，重跑同选题不重复计费

## 四、AIGC 能力归属：dig-media vs clipper vs 新建（讨论中）

### 4.0 前置技术事实（决定设计的硬约束）
| 能力 | 调用机制 | skill 脚本可封装？ |
|---|---|---|
| VideoGen / ImageGen | 会话内置工具（宿主注入，agent 对话中调用） | ❌ 无命令行入口，只能 agent 按契约调用 |
| video-fx 模板特效 / 3D | Python 脚本 + clientTempToken | ✅ 可脚本化 |

→ **任何技能承载 AI 生成，形态都是「SKILL.md 调用契约 + agent 调工具 + 落盘约定」，没有可执行 scripts**。成本确认（工具方强制要求）也只能发生在 agent 对话层。

### 4.1 三个候选归属

**A. 扩展 iskill-dig-media 为「素材供给中心」（推荐）**
- dig-media 定位从「Pixabay 图库挖掘」升级为「素材供给：图库 + AI 生成」，AI 生成是它的第 3 种供给方式
- 提供 `ai-image` / `ai-video` 两条**协议级子命令**（SKILL.md 契约，非脚本）：何时调、参数怎么填（9:16、enable_audio=false、统一 style）、落盘 `dig-media/ai-<关键词slug>/` + manifest.json（含 prompt/credits 消耗记录）、**缓存查重**（同 prompt 已有产物直接复用，不重复计费）
- clipper 决策树末级从「dig-media 挖掘」变成「dig-media 供给（图库免费 → AI 生成付费）」，**clipper 不感知 VideoGen 细节**
- 优点：单一职责（画面从哪来=供给；怎么剪=clipper）；其他技能（封面、插图类）可复用；缓存/溯源/manifest 机制天然沿用 dig-media 既有约定
- 缺点：dig-media 的「免费」定位被打破（需在 description 标注 AI 生成消耗 credit）

**B. AIGC 留在 clipper 内**
- clipper SKILL.md 直接写缺镜时调 VideoGen
- 优点：改动最小
- 缺点：clipper 越来越胖；AI 素材无法被别的技能复用；缓存约定要另起炉灶

**C. 新建 iskill-ai-media 第三技能**
- 与 dig-media 并列的「AI 素材生成」专责技能
- 优点：免费/付费供给分家最干净
- 缺点：技能数量 +1，clipper 决策树要挂两个供给技能；dig-media 的 manifest/目录约定要复制一份

### 4.2 推荐：A + clipper 仍持 engine 分支
- **dig-media 管「供给」**：图库挖掘（脚本化、免费）+ AI 生成（协议级、计费），统一落 `dig-media/` + manifest 溯源 + prompt 缓存
- **clipper 管「策略」**：`--engine` 三档本质是「允许动用哪级供给 + 成本意愿」——local=只走免费级；aigc-mix=免费级优先、缺镜允许 AI 级（事前报成本）；aigc-full=直接 AI 级全量
- 两技能契约互相引用：clipper 写「AIGC 供给按 iskill-dig-media 的 ai-image/ai-video 协议」，dig-media 写「clipper 是主要消费方」

### 4.3 video-fx 模板特效的归属
video-fx（模板图生视频：人物互动/风格化/onestory 连续故事）可脚本化、面向人物照片，与实拍素材强相关 → **归 clipper 的 Phase 7 精修扩展**（用户照片+模板=成片创意镜），不进 dig-media（dig-media 管通用供给，不管人物向特效）。首版可不做，列入 roadmap。

## 五、方案：`--engine` 三档分支

```
--engine local      程序化合成（默认，现状不变）
--engine aigc-mix   混合模式：raw/dig-media 优先，缺的镜头才 AIGC 补
--engine aigc-full  全 AI：无实拍素材，每段镜头都生成
```

### 触发方式（三层）
1. 显式参数：用户说「AIGC 出片」「AI 生成镜头」「混合模式」「全 AI 出片」
2. SKILL.md 决策树：命中关键词 → 对应 engine；用户没表态但有 AIGC 关键词 → AskUserQuestion 二选一并**报成本测算**
3. 硬约束：aigc-full 与任何 AIGC 生成动作前，**必须先报 credit 估算并获用户确认**（工具本身的要求）

### 各引擎下的素材决策树变化
```
aigc-mix: 用户目录 → raw/ → dig-media/ → dig-media 挖掘 → AIGC 补镜（ImageGen 锚帧 → VideoGen）
aigc-full: 口播稿逐段 prompt 化 → ImageGen 风格锚帧（可选）→ VideoGen 逐镜生成 → 进既有渲染管线
```

### SKILL.md 改动面（预期）
1. 顶部描述 + 新增「双引擎选择」节（engine 三档定义/触发/成本确认）
2. 素材决策树加 AIGC 层
3. 新增「AIGC 分镜 prompt 化」节：口播稿段落 → 英文视觉 prompt（统一 style 后缀 + negative_prompt + enable_audio=false + 9:16）
4. Phase 5 验收加：AI 镜头风格一致性抽帧检查
5. 产物目录：`成片/aigc-cache/<选题>/` 缓存 + 分镜表记 prompt 映射
6. `--audio` 级联不变；BGM 卡点对 AI 镜头同样生效（生成 5s 源片裁切对齐）

### 风险与边界
- **credit 消耗不可预览余额**，只能事前估算→确认；生成失败重试会重复计费，最多重试 1 次
- AI 画面有「AI 感」，真实感选题（晒秋/打糍粑类）**不推荐 aigc-full**，混合档把 AI 镜头限定在空镜/氛围/转场镜
- VideoGen 生成内容受平台内容审核，敏感词画面可能被拒——预检（第 5 步）放行仍可能生成失败，失败时降级 dig-media 补镜并在交付说明

## 六、实施步骤（确认后执行）

1. 改 `iskill-dig-media/SKILL.md`：定位升级「素材供给中心」，新增 ai-image / ai-video 协议节（调用契约、参数规范、落盘 dig-media/ai-<slug>/、manifest 记 prompt+credits、缓存查重、成本确认要求）
2. 改 `iskill-video-clipper/SKILL.md`：双引擎契约（--engine 三档）+ 决策树末级指向 dig-media AI 供给 + AIGC 镜头验收加项
3. （可选增强）clipper 加 reference/aigc_storyboard.py 模板：分镜表 → 批量生成调度（agent 调工具时对照）
4. 两仓 git commit + push，核远端作者
5. 更新工作区记忆与每日日志

### 待确认清单
- [ ] 归属：A（dig-media 扩展）/ B（clipper 内）/ C（新建 iskill-ai-media）
- [ ] 引擎档位：三档全做 / 只 local+aigc-mix / 只 aigc-mix
- [ ] 默认生成方式：锚帧优先 / 全文生 / agent 自行判断
- [ ] 成本策略：每次确认 / 估算+上限兜底 / 信任模式
- [ ] video-fx 是否首版纳入（建议 roadmap 不做）
