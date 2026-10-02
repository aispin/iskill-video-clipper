/* ============================================================================
 * iskill-video-clipper · 落地页内容
 * 只改这个文件就能换掉整页文案（外加 index.html 顶部那几行 meta）。
 * ==========================================================================*/
window.PROMO = {
  name: "ISKILL-VIDEO-CLIPPER",
  brand: "#f43f5e",
  brand2: "#fb923c",
  repo: "https://github.com/aispin/iskill-video-clipper",
  repoLabel: "aispin/iskill-video-clipper",

  /* 核心是 Python / Node + ffmpeg 多路径探测，两边可跑；
     只有剪映草稿的「自动导出」是 Windows 专属 —— 见 FAQ。 */
  platform: "mac-windows",
  license: "MIT",

  lang: {
    /* ── 中文 ───────────────────────────────────────────────────────── */
    zh: {
      meta: {
        title: "ISKILL-VIDEO-CLIPPER · 实拍素材剪成短视频",
        description: "照片 + 视频混合 → 15-60s 成片或剪映草稿：三档素材引擎 local / aigc-mix / aigc-full，有 BGM 自动分析节拍、转场卡点，内置免费商用字体，全流程本地 ffmpeg。"
      },
      a11y: { skip: "跳到主要内容" },
      ui: { copy: "复制", copied: "已复制", failed: "复制失败" },
      nav: { features: "能力", shots: "截图", how: "上手", faq: "问答" },

      hero: {
        badge: "AI 技能",
        titlePre: "把一堆素材",
        titleAccent: "剪成一条成片",
        titlePost: "",
        sub: "照片 + 视频混合，剪成带标题、字幕、LOGO、BGM 的 15–60s 短视频：先侦察素材再分镜，有 BGM 就卡节拍，一条分镜表同时出「快速版 + 剪映精修版」。",
        ctaPrimary: "复制安装提示词",
        ctaSecondary: "看源码",
        meta1: "全本地 ffmpeg",
        meta2: "BGM 卡节拍",
        meta3: "成片 / 剪映草稿"
      },
      terminal: {
        title: "zsh — iskill-video-clipper",
        lines: [
          [{ t: "$ ", c: "p" }, { t: "ffmpeg -hide_banner -filters | grep -E ' (drawtext|zoompan|xfade) '", c: "k" }],
          [{ t: "    ", c: "" }, { t: "drawtext  V->V  Draw text on top of video frames.", c: "c" }],
          [{ t: "    ", c: "" }, { t: "zoompan   V->V  Apply Zoom & Pan effect.", c: "c" }],
          [{ t: "$ ", c: "p" }, { t: "python .../beat_detect.py bgm.m4a --end 60 --json bgm.m4a.beats.json", c: "k" }],
          [{ t: "✓ ", c: "p" }, { t: "bpm 96 · 强拍 18 个 · 候选转场点 12 个", c: "s" }]
        ]
      },

      stats: [
        { value: "3 档", label: "素材引擎", note: "local 全免费 / aigc-mix 缺镜 AI 补 / aigc-full 纯 AI 生成" },
        { value: "15–60s", label: "成片时长", note: "照片 + 视频混合，分镜表驱动" },
        { value: "4 款", label: "内置免费商用字体", note: "优设标题黑 · 站酷酷黑 · 庞门正道 · 庆科黄油体" },
        { value: "≤0.1s", label: "卡点转场偏差验收线", note: "转场中点帧对照 beats.json 实测" }
      ],

      compare: {
        eyebrow: "对比",
        title: "以前 vs 现在",
        sub: "",
        before: {
          title: "手动一帧帧剪",
          items: [
            "几十条素材，得挨个看一遍才知道拍的是什么",
            "转场、字幕、卡点全手工对，节奏全靠感觉",
            "改了文案字幕要重对；封面截出来还带成片字幕，穿帮重做"
          ]
        },
        after: {
          title: "先侦察，再分镜表驱动",
          items: [
            "Phase 1 抽帧 + 照片看板，先产出「素材 → 主题」映射表再动手",
            "有 BGM 就自动分析节拍，段长取整到节拍、转场卡在强拍上",
            "分镜表一行改动即可复用；字幕用定稿文案，不自行创作",
            "封面优先用分镜原图裁切，避开成片字幕穿帮"
          ]
        }
      },

      features: {
        eyebrow: "能力",
        title: "它替你干的活",
        sub: "",
        items: [
          { icon: "camera", title: "先侦察，再剪辑", desc: "Phase 1 对每条视频抽 20%/50%/80% 三帧、照片拼 5×5 看板，先产出「素材 → 主题」映射表，绝不在没看过素材前动手。" },
          { icon: "layers", title: "三档素材引擎", desc: "<code>--engine local</code>（默认，全免费）/ <code>aigc-mix</code>（缺镜 AI 补，计费事前确认）/ <code>aigc-full</code>（无实拍全量 AI 生成）；素材从 raw/ → dig-media/ → AI 多级回退。" },
          { icon: "gauge", title: "BGM 卡点转场", desc: "有 BGM 时自动调 iskill-music-beats 出 <code>beats.json</code>：段长取整到节拍、边界对强拍，验收要求转场偏差 ≤ 0.1s。" },
          { icon: "bolt", title: "GPU shader 转场", desc: "默认 <code>gl</code> 档走 HyperFrames + WebGL 逐帧渲染独立转场片段；无 Chrome/WebGL 或要快速出片时按点降级到 <code>xfade</code>，单点降级不打回整片。" },
          { icon: "crop", title: "封面 + 内置字体", desc: "默认从分镜原图截帧（避开成片字幕）出 1080×1920 封面、可叠标题字；内置 4 款免费可商用字体，按气质选型。" },
          { icon: "monitor", title: "成片或剪映草稿", desc: "ffmpeg 直出快速档，或生成剪映专业版草稿（真转场 / 文本动画 / 曲库 / 关键帧）供人工精修；两条引擎共用同一份分镜表。" }
        ]
      },

      showcase: {
        eyebrow: "实拍",
        title: "看一眼真东西",
        sub: "",
        items: []
      },

      steps: {
        eyebrow: "上手",
        title: "三步跑起来",
        sub: "命令由 agent 跑，你只说要什么、看结果。",
        items: [
          { title: "交给 AI 装", desc: "把这句话粘进对话框，agent 会自己拉代码、读文档，再告诉你用法。", codeKey: "install" },
          { title: "给素材目录和时长", desc: "缺素材它会去挖，有 BGM 它会先对节拍；引擎怎么选交给它判断。", codeName: "prompt", code: "把 ~/素材/农场 这批照片和视频剪一条 30 秒的成片，节奏轻快。" },
          { title: "看成片", desc: "成片和剪映草稿都在输出目录，你看一遍节奏；不满意就说哪一段，它重剪那一段。" }
        ]
      },


      faq: {
        eyebrow: "问答",
        title: "常见问题",
        items: [
          { q: "生成的剪映草稿能自动导出吗？", a: "**自动导出仅 Windows**（靠 UI 自动化）。在 macOS 上，草稿会写进 <code>~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft</code>，但<b>最终导出要在剪映里手动完成</b>。另外草稿生成后剪映不会实时刷新，需重启剪映、或随便进出一个旧草稿才看得到。" },
          { q: "一定要装 ffmpeg 吗？", a: "是的，全流程走本地 ffmpeg。先按决策树探测：<code>command -v ffmpeg</code> → <code>/opt/homebrew/bin/ffmpeg</code> → <code>/usr/local/bin/ffmpeg</code>，再逐个验 <code>drawtext / zoompan / xfade</code> 滤镜。注意本机 Homebrew 公式默认<b>不带 freetype</b>（无 <code>drawtext</code>），缺就装 <code>imageio-ffmpeg</code> 静态构建兜底（含 libx264/aac，但不含 heic 解码）。" },
          { q: "要花钱吗？", a: "<code>--engine local</code>（默认）全免费，纯本地 ffmpeg。<code>aigc-mix</code> / <code>aigc-full</code> 会调用 AI 生成镜头，<b>计费且事前报 credits 估算、需你确认</b>；真实感选题会把 AI 镜头限定在空镜 / 氛围 / 转场镜。" },
          { q: "含视频素材的剪映草稿为什么失败？", a: "草稿的媒体解析链是 <code>pymediainfo → ffprobe</code>，缺 ffprobe 时<b>纯照片草稿能成、含视频的草稿直接失败</b>（Errno 2 'ffprobe'）。所以要先注入 <code>static_ffmpeg</code> 的 ffprobe；brew 装了 ffmpeg 就直接用它自带的 ffprobe。" },
          { q: "字幕文案能自己写吗？", a: "工作流模式下不能。字幕唯一来源是定稿口播稿 v2，按 <code>【钩子】</code> 等段落注释分段、逐句上字幕，<b>禁止自行创作或改写</b>；发现文案问题要退回 iskill-copy-deslop，不代改。" },
          { q: "能不能不用 AI，手动装？", a: "可以。把仓库 clone 进你的 agent 技能目录（如 <code>~/.workbuddy/skills/</code>）就行 —— 技能本身是纯文本加脚本。" }
        ]
      },

      cta: {
        title: "素材在硬盘里躺很久了",
        desc: "把「剪成片」这句话交给它，先侦察再动手。",
        primary: "去 GitHub 看看",
        secondary: "复制安装提示词"
      },
      footer: { license: "MIT 许可", madeWith: "由 iskill-promo-page 生成" }
    },

    /* ── English ────────────────────────────────────────────────────── */
    en: {
      meta: {
        title: "ISKILL-VIDEO-CLIPPER · Cut footage into a short video",
        description: "Photos plus video into a 15–60s cut or a JianYing draft: three source engines local / aigc-mix / aigc-full, automatic beat detection to land cuts on the beat, free commercial fonts bundled, all local ffmpeg."
      },
      a11y: { skip: "Skip to content" },
      ui: { copy: "Copy", copied: "Copied", failed: "Copy failed" },
      nav: { features: "Features", shots: "Screens", how: "Get started", faq: "FAQ" },

      hero: {
        badge: "AI skill",
        titlePre: "Turn a pile of footage into ",
        titleAccent: "one finished cut",
        titlePost: "",
        sub: "Mix photos and video into a 15–60s short with titles, subtitles, a logo and BGM: scout the footage first, storyboard second, land transitions on the beat when there is music, and get both a fast cut and a JianYing draft from the same storyboard.",
        ctaPrimary: "Copy install prompt",
        ctaSecondary: "View source",
        meta1: "All-local ffmpeg",
        meta2: "Cuts on the beat",
        meta3: "Cut or JianYing draft"
      },
      terminal: {
        title: "zsh — iskill-video-clipper",
        lines: [
          [{ t: "$ ", c: "p" }, { t: "ffmpeg -hide_banner -filters | grep -E ' (drawtext|zoompan|xfade) '", c: "k" }],
          [{ t: "    ", c: "" }, { t: "drawtext  V->V  Draw text on top of video frames.", c: "c" }],
          [{ t: "    ", c: "" }, { t: "zoompan   V->V  Apply Zoom & Pan effect.", c: "c" }],
          [{ t: "$ ", c: "p" }, { t: "python .../beat_detect.py bgm.m4a --end 60 --json bgm.m4a.beats.json", c: "k" }],
          [{ t: "✓ ", c: "p" }, { t: "bpm 96 · 18 strong beats · 12 cut candidates", c: "s" }]
        ]
      },

      stats: [
        { value: "3 engines", label: "where the footage comes from", note: "local (free) / aigc-mix (fill gaps with AI) / aigc-full (all AI)" },
        { value: "15–60s", label: "finished cut length", note: "photos and video mixed, driven by a storyboard" },
        { value: "4", label: "free commercial fonts bundled", note: "YouShe · ZCOOL KuHei · PangMen · ZCOOL QingKe HuangYou" },
        { value: "≤0.1s", label: "beat-alignment tolerance", note: "measured on transition mid-frames against beats.json" }
      ],

      compare: {
        eyebrow: "Comparison",
        title: "Before vs after",
        sub: "",
        before: {
          title: "Cutting frame by frame",
          items: [
            "Dozens of clips you have to watch one by one to learn what they show",
            "Transitions, subtitles and beats aligned by hand — rhythm by feel",
            "Change the copy and the subtitles must be redone; a cover grabbed from the cut still carries baked-in subtitles"
          ]
        },
        after: {
          title: "Scout first, then a storyboard",
          items: [
            "Phase 1 samples frames and builds a photo contact sheet into a footage→theme map before anything is edited",
            "With BGM it detects the beat and rounds segment lengths to it, landing transitions on strong beats",
            "One storyboard drives everything; subtitles come from the approved script, never invented",
            "Covers are cropped from the storyboard's source frames, avoiding baked-in subtitle clashes"
          ]
        }
      },

      features: {
        eyebrow: "Features",
        title: "What it takes off your plate",
        sub: "",
        items: [
          { icon: "camera", title: "Scout before you cut", desc: "Phase 1 samples three frames (20/50/80%) per clip and tiles photos into a 5×5 sheet, producing a footage→theme map so nothing is edited blind." },
          { icon: "layers", title: "Three source engines", desc: "<code>--engine local</code> (default, free) / <code>aigc-mix</code> (AI fills the gaps, cost confirmed up front) / <code>aigc-full</code> (all AI, no footage). Sources fall back raw/ → dig-media/ → AI." },
          { icon: "gauge", title: "Cuts that land on the beat", desc: "With BGM it calls iskill-music-beats for a <code>beats.json</code>: segment lengths round to the beat, boundaries snap to strong beats, and acceptance requires ≤ 0.1s deviation." },
          { icon: "bolt", title: "GPU shader transitions", desc: "The default <code>gl</code> tier renders standalone transition clips with HyperFrames + WebGL; fall back per-point to <code>xfade</code> when there is no Chrome/WebGL or when a fast cut is wanted — a single fallback never aborts the whole film." },
          { icon: "crop", title: "Covers and bundled fonts", desc: "Covers default to a 1080×1920 frame cropped from source stills (avoiding baked-in subtitles) with optional title text; four free commercial fonts ship in-repo." },
          { icon: "monitor", title: "Finished cut or JianYing draft", desc: "ffmpeg delivers a fast, fully automated cut, or it writes a JianYing Pro draft (real transitions, text animation, its music library, keyframes) for manual polish — both share one storyboard." }
        ]
      },

      showcase: {
        eyebrow: "Screens",
        title: "See the real thing",
        sub: "",
        items: []
      },

      steps: {
        eyebrow: "Get started",
        title: "Up and running in three steps",
        sub: "The agent runs the commands. You say what you want and check the result.",
        items: [
          { title: "Let your agent install it", desc: "Paste the line into the chat — it clones the repo, reads the docs, and tells you how to use it.", codeKey: "install" },
          { title: "Give the footage dir and length", desc: "Missing footage? It digs for more. Got a BGM? It beat-matches first. Engine choice is its call.", codeName: "prompt", code: "Cut a 30-second clip from the photos and videos in ~/footage/farm — upbeat pacing." },
          { title: "Watch the cut", desc: "The video and a JianYing draft land in the output dir — watch it once. Don't like a segment? Name it and it re-cuts just that part." }
        ]
      },


      faq: {
        eyebrow: "FAQ",
        title: "Frequently asked",
        items: [
          { q: "Can the JianYing draft be exported automatically?", a: "**Auto-export is Windows-only** (it relies on UI automation). On macOS the draft is written to <code>~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft</code>, but <b>the final export must be done by hand inside JianYing</b>. Also, JianYing does not refresh live after a draft is generated — restart it, or open and leave another draft first." },
          { q: "Is ffmpeg required?", a: "Yes — the whole pipeline runs on local ffmpeg. It probes in order (<code>command -v ffmpeg</code> → <code>/opt/homebrew/bin/ffmpeg</code> → <code>/usr/local/bin/ffmpeg</code>) then verifies the <code>drawtext / zoompan / xfade</code> filters. Note Homebrew's formula ships <b>without freetype</b> (no <code>drawtext</code>); if that is missing, install the <code>imageio-ffmpeg</code> static build (it has libx264/aac but no heic decoding)." },
          { q: "Does it cost money?", a: "<code>--engine local</code> (the default) is entirely free and local. <code>aigc-mix</code> / <code>aigc-full</code> generate shots with AI — <b>billable, with a credits estimate shown and your confirmation required up front</b>. For realistic topics, AI shots are limited to cutaways, atmosphere and transitions." },
          { q: "Why does a JianYing draft with video fail?", a: "Media resolution goes <code>pymediainfo → ffprobe</code>, and without ffprobe <b>a photos-only draft works while one containing video fails outright</b> (Errno 2 'ffprobe'). Inject static_ffmpeg's ffprobe first; if brew's ffmpeg is installed, its bundled ffprobe is preferred." },
          { q: "Can I write the subtitles myself?", a: "Not in workflow mode. Subtitles come solely from the approved v2 script, split on section markers like <code>【钩子】</code> and applied line by line — <b>rewriting or inventing them is forbidden</b>. If the copy is wrong, send it back to iskill-copy-deslop instead of patching it here." },
          { q: "Can I install it without an agent?", a: "Sure. Clone the repo into your agent's skills directory (e.g. <code>~/.workbuddy/skills/</code>) — plain text and scripts." }
        ]
      },

      cta: {
        title: "That footage has been sitting on your drive",
        desc: "Hand it the words \"cut this into a video\" and it scouts before it edits.",
        primary: "Open on GitHub",
        secondary: "Copy install prompt"
      },
      footer: { license: "MIT licensed", madeWith: "Built with iskill-promo-page" }
    }
  }
};
