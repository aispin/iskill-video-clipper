#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""beat_selftest.py —— 卡点「咔哒自测版」生成器（Phase 5 人工耳测用）。
按 beats.json 的**实测节拍时刻**生成 30ms 咔哒音轨，与成片原声 amix 出自测版。
注意：咔哒必须用实测时刻而非理想网格——真实节拍有漂移（见 SKILL.md 卡点节）。
用法: python beat_selftest.py <成片.mp4> <beats.json> <输出.mp4> [--end 秒]
依赖: ffmpeg（默认 imageio 静态构建，可被环境变量 FF 覆盖）"""
import json, wave, math, struct, os, sys, argparse, subprocess

FF = os.environ.get("FF", "/Users/lv/.workbuddy/binaries/python/envs/default/lib/python3.13/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1")

def media_dur(p):
    r = subprocess.run([FF, "-i", p], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    h, mm, s = m.groups(); return int(h)*3600+int(mm)*60+float(s)

import re
ap = argparse.ArgumentParser()
ap.add_argument("film"); ap.add_argument("beats_json"); ap.add_argument("out")
ap.add_argument("--end", type=float, default=0, help="只生成到该秒（0=成片时长）")
ap.add_argument("--click-gain", type=float, default=0.75)
ap.add_argument("--src-gain", type=float, default=0.85)
a = ap.parse_args()

total = a.end or media_dur(a.film)
times = [b["t"] for b in json.load(open(a.beats_json))["beats"] if b["t"] <= total]
SR = 24000
buf = [0.0] * int(total * SR)
CLICK = int(0.030 * SR)
for t in times:
    s0 = int(t * SR)
    for i in range(CLICK):
        idx = s0 + i
        if idx >= len(buf): break
        buf[idx] += 0.65 * math.exp(-i / (CLICK / 6)) * math.sin(2 * math.pi * 1000 * i / SR)
click_wav = "/tmp/_beat_selftest_click.wav"
w = wave.open(click_wav, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(v * 32767)))) for v in buf))
w.close()
subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", a.film, "-i", click_wav,
    "-filter_complex", f"[0:a]volume={a.src_gain}[a0];[1:a]volume={a.click_gain}[a1];"
    "[a0][a1]amix=inputs=2:duration=first:normalize=0[aout]",
    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", a.out], check=True)
print(f"OK {a.out}（{len(times)} 个咔哒点 / {total:.2f}s）—— 戴耳机听：转场应压在「哒」上")
