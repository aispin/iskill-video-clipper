#!/bin/bash
# shader 黑名单扫描：逐 shader 渲染 2s 转场片段 → 逐帧 YAVG 亮度分析 → 归类 head/dip/tail 黑场相位。
# 用法: bash scan_loop.sh            # 在本目录运行；clips/ 已有的片自动跳过（断点续跑）
# 依赖: hyperframes CLI（渲染需代理 export https_proxy=http://127.0.0.1:10080）、ffmpeg/ffprobe、python3
# 产物: clips/<shader>.mp4 + scan-result.json；结果表人工誊入 ../gpu-transitions.md §1 黑名单
#
# ⚠️ 为什么逐片段渲染：多转场长链（scenes=transitions+1 也满足时）单 composition 截图捕获会
#    stall（no frame progress），必须一个 shader 一个 2s 片段。
# 新 shader / 新素材档（暗场景）复跑：换 assets/frameA.jpg frameB.jpg 后删 clips/ 重扫。
set -u
cd "$(dirname "$0")"
FFPROBE="${FFPROBE:-/opt/homebrew/bin/ffprobe}"
SHADERS="${SHADERS:-chromatic-split cinematic-zoom cross-warp-morph domain-warp flash-through-white glitch gravitational-lens light-leak ridged-burn ripple-waves sdf-iris swirl-vortex thermal-distortion whip-pan}"
mkdir -p clips
for S in $SHADERS; do
  OUT="clips/$S.mp4"
  if [ -s "$OUT" ]; then echo "[skip] $S"; continue; fi
  python3 gen_index.py "$S" || { echo "[gen-fail] $S"; continue; }
  npx --yes hyperframes@0.8.96 render > "clips/$S.render.log" 2>&1
  NEWEST=$(ls -t renders/*.mp4 2>/dev/null | head -1)
  if [ -n "$NEWEST" ] && [ -s "$NEWEST" ]; then
    cp "$NEWEST" "$OUT"; rm -f renders/*.mp4
    echo "[ok] $S"
  else
    echo "[render-fail] $S (see clips/$S.render.log)"
  fi
done

python3 - "$FFPROBE" << 'EOF'
import subprocess, json, glob, os, sys
FP = sys.argv[1]
T0, DUR, BLACK_T, DIM_T = 0.15, 1.7, 20.0, 48.0  # 转场窗口 / 判黑 / 判暗 阈值(YAVG 0-255)

def merge(ps):
    if not ps: return []
    rs, s, e = [], ps[0], ps[0]
    for p in ps[1:]:
        if p - e <= 0.06: e = p
        else: rs.append((s, e)); s = e = p
    rs.append((s, e)); return rs

out = []
for mp4 in sorted(glob.glob("clips/*.mp4")):
    name = os.path.basename(mp4)[:-4]
    fps_txt = subprocess.run([FP, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", mp4],
        capture_output=True, text=True).stdout.strip()
    try:
        n, d = fps_txt.split("/"); fps = float(n) / float(d)
    except Exception:
        out.append({"shader": name, "class": "PROBE-FAIL"}); continue
    # 注意：lavfi movie= 滤镜已含输入路径，不能再追加 mp4 位置参数
    ytxt = subprocess.run([FP, "-v", "error", "-f", "lavfi",
        f"movie={mp4},signalstats", "-show_entries",
        "frame_tags=lavfi.signalstats.YAVG", "-of", "csv=p=0"],
        capture_output=True, text=True).stdout
    yavgs = [float(x.strip().rstrip(",")) for x in ytxt.splitlines() if x.strip()]
    frames = [(k / fps, y) for k, y in enumerate(yavgs)]
    win = [(t, y) for t, y in frames if T0 - 0.5/fps <= t <= T0 + DUR + 0.5/fps]
    if not win: out.append({"shader": name, "class": "NO-FRAMES"}); continue
    blacks = [(t - T0) / DUR for t, y in win if y < BLACK_T]
    dims   = [(t - T0) / DUR for t, y in win if y < DIM_T]
    ymin = min(y for _, y in win)
    if not blacks: cls = "clean"
    else:
        head = any(p <= 0.25 for p in blacks)
        tail = any(p >= 0.75 for p in blacks)
        mid  = any(0.25 < p < 0.75 for p in blacks)
        parts = [x for x in ("head" if head else "", "dip" if mid else "", "tail" if tail else "") if x]
        cls = "+".join(parts) if parts else "clean"
    out.append({"shader": name, "class": cls, "n_black": len(blacks),
        "black_p": [f"{a:.2f}-{b:.2f}" for a, b in merge(blacks)],
        "n_dim": len(dims), "dim_p": [f"{a:.2f}-{b:.2f}" for a, b in merge(dims)],
        "ymin": round(ymin, 1)})

print(f"{'shader':<22} {'class':<12} {'ymin':>6}  detail")
for r in out:
    det = f"BLACK {r['black_p']}" if r.get("n_black") else (f"dim {r['dim_p']}" if r.get("n_dim") else "")
    print(f"{r['shader']:<22} {r['class']:<12} {r.get('ymin','-'):>6}  {det}")
json.dump(out, open("scan-result.json", "w"), ensure_ascii=False, indent=2)
print("saved scan-result.json")
EOF
