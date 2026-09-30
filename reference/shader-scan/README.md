# shader-scan — GPU Shader 黑名单扫描工程

对 `@hyperframes/shader-transitions` 全部内置 shader 做逐帧亮度校验，产出黑场相位黑名单。
**结果与结论看 `../gpu-transitions.md` §1「shader 行为黑名单」**（本目录是可复跑的工具与基准数据）。

## 复跑（新 shader 上架 / 换素材档）

```bash
# 1. 换素材：把待测场景的亮/暗代表帧放进 assets/frameA.jpg、frameB.jpg（明亮实景为基准档）
# 2. 跑扫描（需代理；已有 clips/ 自动跳过，断点续跑）
export https_proxy=http://127.0.0.1:10080
bash scan_loop.sh
# 3. 结果：scan-result.json + 终端表格，人工誊入 gpu-transitions.md
```

## 结构

- `gen_index.py` — 生成单 shader 转场片段 index.html（已验证契约：`time:0.15 / duration:1.7` / 总长 2s）
- `scan_loop.sh` — 渲染循环（逐 shader 单片段，勿合并长链：多转场长链截图捕获会 stall）+ 逐帧 YAVG 分析（<20 黑帧 / <48 暗带）+ 相位归类（head/dip/tail）
- `assets/frameA|B.jpg` — 2026-10-01 扫描基准素材（明亮实景）
- `scan-result.json` — 2026-10-01 全量扫描原始数据（14 款）
