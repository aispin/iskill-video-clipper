# HyperFrames 卡片模板库

配合 `--transitions gl` 档使用的 HTML→视频模板（HyperFrames 0.8.96 + GSAP，本地渲染）。三个模板各管一段画面：

| 模板 | 用途 | 时长 | 关键约定 |
|---|---|---|---|
| `cover-card/` | **封面卡**：首帧即封面，`ffmpeg -ss 0` 抽第 0 帧作封面图 | 3s | 封面元素**禁用 from()/fromTo()**，动效 0.8s 后用 `to()` 接管 |
| `hook-card/` | **片头卡**：钩子→卖点花字→CTA 三场景，逐词弹出/滑入/脉冲 | 10s | scene 切换走 data-start 边界硬切；要 shader 转场参照 gpu-transitions.md §2 加 HyperShader.init |
| `shader-transition-clip/` | **段间转场片段**：A尾帧→shader→B首帧，渲染独立 mp4 后 concat 回主链 | 1.2~2s（=整数拍） | 窗口内缩 0.15s；concat 前归一编码 |

## 使用流程（每个模板相同）

1. **拷贝模板到工作目录**：`cp -r <skill>/reference/templates/hook-card/ <工作目录>/hook/`
2. **改内容**：文案在 index.html 的 HTML 部分（有注释标记改动点）；时长改 `data-duration` + timeline 时间点
3. **渲染**：`cd <模板目录> && npm run render`（首次拉包需代理 `export https_proxy=http://127.0.0.1:10080`；assets 本地化后页面本身离线可渲染）
4. **产物**：`renders/<name>_<时间戳>.mp4`，标准 mp4 可直接进主剪辑链（concat/xfade 均可）

## 字体说明（重要）

- 模板通过相对路径 `../../../fonts/` 引用本 skill 的字体库（优设标题黑/站酷庆科黄油体等，免费可商用）
- **拷走模板必须同步处理字体**：要么把用到的 .ttf 复制进模板 `assets/` 并把 @font-face 的 src 改成 `assets/xxx.ttf`，要么保持相对层级
- **Hiragino Sans GB（系统字体）不入仓库**（版权原因）。如需常规正文黑体，自行从 `/System/Library/Fonts/Hiragino Sans GB.ttc` 复制并在 @font-face 用 `format("collection")` 声明
- lint 强制 @font-face：页面里用到的每个字体族必须有声明，否则 check/render 报错
- 优设标题黑、庆科黄油体均为单一 Regular 字重，**勿依赖 font-weight 700/900 变粗**（会触发 Chrome 伪粗发糊）

## 通用坑（全模板适用）

1. `window.__timelines["<compositionId>"] = tl` 必须手动注册，不注册渲染器 45s 超时后按静态帧出片
2. `tl.seek(0)` 结尾调用，保证 t=0 状态正确
3. 渲染需 Chrome：本机在 `/Volumes/...` 外置卷也行（puppeteer-core 找得到即可）
4. 渲染速度参考：10s@30fps ≈ 33s（GPU screenshot 模式）
