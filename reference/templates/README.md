# HyperFrames 卡片模板库

配合 `--transitions gl` 档使用的 HTML→视频模板（HyperFrames 0.8.96 + GSAP，本地渲染）。三个模板各管一段画面：

| 模板 | 用途 | 时长 | 关键约定 |
|---|---|---|---|
| `cover-card/` | **封面卡**：三段式（冲击力标题 + 5张编号卖点卡弧形半包围 + 出镜主体羽化），首帧即封面，`ffmpeg -ss 0` 抽第 0 帧作封面图 | 3s | 封面元素**禁用 from()/fromTo()**，动效 0.8s 后用 `to()` 接管；设计规范与验收清单见 `reference/cover-style-guide.md` |
| `hook-card/` | **片头卡**：钩子→卖点花字→CTA 三场景，逐词弹出/滑入/脉冲 | 10s | scene 切换走 data-start 边界硬切；要 shader 转场参照 gpu-transitions.md §2 加 HyperShader.init |
| `shader-transition-clip/` | **段间转场片段**：A尾帧→shader→B首帧，渲染独立 mp4 后 concat 回主链 | 1.2~2s（=整数拍） | 窗口内缩 0.15s；concat 前归一编码 |

## 使用流程（每个模板相同）

1. **拷贝模板到工作目录**：`cp -r <skill>/reference/templates/hook-card/ <工作目录>/hook/`
2. **改内容**：文案在 index.html 的 HTML 部分（有注释标记改动点）；时长改 `data-duration` + timeline 时间点
3. **渲染**：`cd <模板目录> && npm run render`（首次拉包需代理 `export https_proxy=http://127.0.0.1:10080`；assets 本地化后页面本身离线可渲染）
4. **产物**：`renders/<name>_<时间戳>.mp4`，标准 mp4 可直接进主剪辑链（concat/xfade 均可）

## 字体说明（重要）

- **两个卡片模板的字体已本地化进各自 `assets/`**（优设标题黑/庞门正道，免费商用），模板自包含，拷走即用，check 的 StaticGuard 也要求路径不越级（禁 `../`）
- **Hiragino Sans GB（系统字体）不入仓库**（版权原因）。cover-card 的字体栈里以 `local()` 声明兜底；如需还原 v14 定稿卡文案字形，从 `/System/Library/Fonts/Hiragino Sans GB.ttc` 复制进模板 `assets/` 并改 @font-face 为 `format("collection")`
- 单一 Regular 字重的字体（优设标题黑/庞门正道/庆科黄油体）**勿依赖 font-weight 700/900 变粗**（会触发 Chrome 伪粗发糊）
- lint 强制 @font-face：页面里用到的每个字体族必须有声明（系统字体用 `src: local(...)` 即可满足），否则 check/render 报错

## 通用坑（全模板适用）

1. `window.__timelines["<compositionId>"] = tl` 必须手动注册，不注册渲染器 45s 超时后按静态帧出片
2. `tl.seek(0)` 结尾调用，保证 t=0 状态正确
3. 渲染需 Chrome：本机在 `/Volumes/...` 外置卷也行（puppeteer-core 找得到即可）
4. 渲染速度参考：10s@30fps ≈ 33s（GPU screenshot 模式）
