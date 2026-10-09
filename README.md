# iskill-video-clipper

实拍素材短视频剪辑（照片+视频混合 → 15-60s 成片/剪映草稿），双引擎：--engine local 程序化合成（默认）/ aigc-mix 混合（缺镜 AI 补）/ aigc-full 全 AI；另有 --engine mpt 快速草稿档（MoneyPrinterTurbo 整片合成，未过门禁须标注）。两种入口：①独立剪辑——用户要求"剪视频/切条/做成片/活动视频剪辑"并给素材目录；②六步爆款工作流第 6 步——输入 viral-video-team-output/文案/ 下的定稿口播稿（v2）+ 预检通过的选题，字幕用定稿文案、按需配音对齐，产出成片或剪映工程。素材支持零输入：raw/ → dig-media/（图库）→ AIGC 补镜多级回退。有 BGM 时自动调 iskill-music-beats 分析节拍点，转场卡在节拍上。转场默认 gl 档（HyperFrames GPU shader 转场，详见 reference/gpu-transitions.md），xfade 为回退。全流程本地 ffmpeg，免费无付费环节（AIGC/MPT AI 源除外，计费且事前确认）。

完整用法见 [SKILL.md](SKILL.md)。

> 依赖同步：本仓库含 iskill 共享真源的 vendored 副本（清单见 `package.json` 的 `iskillDeps`），**不要手改**。使用前请同时安装 iskill-utils：对 agent 说「请帮我安装 Skill：aispin/iskill-utils」；用法见 SKILL.md「依赖同步」节。
