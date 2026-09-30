# 封面标题字体库（全部免费可商用）

预览：`preview.png`（同一句标题三字体实渲染对比）

## 字体清单与来源

| 文件 | 字体 | 授权 | 来源 |
|---|---|---|---|
| `YouSheBiaoTiHei.ttf` (1.4MB) | 优设标题黑 YouSheBiaoTiHei v1.00 | 免费可商用（优设 Uisdc 发布，7194 字形） | github.com/wordshub/free-font |
| `ZCOOLKuHei.ttf` (2.1MB) | 站酷酷黑 ZCOOL KuHei | 免费可商用（站酷 ZCOOL 发布） | github.com/wordshub/free-font |
| `PangMenZhengDaoBiaoTiTi.ttf` (3.0MB) | 庞门正道标题体 | 免费可商用（庞门正道发布） | github.com/wordshub/free-font |
| `ZCOOLQingKeHuangYou.ttf` (9.7MB) | 站酷庆科黄油体 ZCOOL QingKe HuangYou | 免费可商用（站酷 ZCOOL 发布） | github.com/wordshub/free-font |

> 注：庆科黄油体不同渠道构建的内部命名不同（`zcoolqingkehuangyouti` / `ZCOOL QingKe HuangYou`），字形一致，均已实测渲染正常。

## 选型建议（短视频封面场景）

1. **优设标题黑 = 爆款封面默认首选**：前倾斜切、超粗、自带速度感与力量感；短视频封面圈使用率最高，对参考爆款图的还原度最好（2026-09-30 对标视频号 AvCWTArjmS 首帧验证，气质高度吻合）。
2. **站酷酷黑**：正体里的最重量级，大字报式标题/关键词强调冲击力最强；Latin 为宽扁几何风，中英混排时注意与中文风格统一。
3. **庞门正道标题体**：端正现代，适合正式感选题、正文标题；斜体违和时用它兜底。
4. **站酷庆科黄油体**：圆头 butter 风、活泼亲和，轻松/趣味选题、生活类内容首选；也是当前封面 PoC（/tmp/hf-poc/cover-demo）实际使用的字体。

## 使用注意

- 三款均为**单字重**，粗细对比靠字号分级 + 描边（-webkit-text-stroke）+ 3D 挤出（text-shadow 步进）实现
- HTML/HyperFrames：`@font-face` 声明后引用；**file:// 页面加载 web font 会被 CORS 拦截**（字体资源强制跨域校验），须走本地 HTTP 服务或 base64 内联
- ffmpeg drawtext：`fontfile=/.../fonts/YouSheBiaoTiHei.ttf`（路径含大写与长名，注意转义）
- 更换/补充字体时保持「免费可商用」底线，并同步更新 preview.png 与 SKILL.md 选型表
