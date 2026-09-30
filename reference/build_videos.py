#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
溪田花境 · 中秋活动短视频构建脚本
管线: 分镜表 -> 逐镜头渲染(Ken Burns/裁剪/字幕) -> concat -> LOGO叠加 -> BGM混音 -> cuts/
风格: 竖屏 9:16 1080x1920@25fps, 温馨纪实体字幕, 样片BGM循环
"""
import subprocess, os, sys, shutil

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = subprocess.check_output([sys.executable, "-c",
    "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"]).decode().strip()
RAW = os.path.join(WS, "260926 中秋 活动", "raw")
SAMPLES = os.path.join(WS, "samples")
BGM_DIR = os.path.join(WS, ".recon", "bgm")
LOGO = os.path.join(WS, "260923LOGO", "溪田花境logo-无文案.png")
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
BUILD = os.path.join(WS, ".build", "shots")
TXT = os.path.join(WS, ".build", "txt")
CUTS = os.path.join(WS, "cuts")

W, H, FPS = 1080, 1920, 25

# ---------- 分镜表 ----------
# kind: photo|video  mode: fill(满屏裁切)|blur(模糊垫底)  kb: in|out(照片推拉方向)
# title=True 大标题  end=True 落款收尾  unsharp=True 轻锐化(低清源)
VIDEOS = {
    "1_打糍粑": {
        "bgm": "sample1.m4a",
        "shots": [
            dict(kind="video", src="2026-09-27 222718.mp4", ss=1.0, dur=3.0, mode="fill",
                 unsharp=True, kb=None, title="中秋，来溪田打一次糍粑", fade_in=True),
            dict(kind="photo", src="2026-09-27 221756.jpg", dur=3.2, mode="fill", kb="out",
                 text="刚蒸好的糯米，倒进石臼"),
            dict(kind="photo", src="2026-09-27 221753.jpg", dur=3.2, mode="fill", kb="in",
                 text="你一槌，我一槌"),
            dict(kind="photo", src="2026-09-27 221805.jpg", dur=3.2, mode="fill", kb="out",
                 text="打出糯米的韧劲"),
            dict(kind="video", src="2026-09-27 222706.mp4", ss=36.0, dur=5.0, mode="fill",
                 lift=True, text="压成饼，团圆就有了形状"),
            dict(kind="photo", src="2026-09-27 221803.jpg", dur=3.5, mode="fill", kb="in",
                 end="溪田花境 · 2026中秋", fade_out=True),
        ],
    },
    "2_做灯笼": {
        "bgm": "sample2.m4a",
        "shots": [
            dict(kind="video", src="2026-09-27 222718.mp4", ss=6.0, dur=3.0, mode="fill",
                 unsharp=True, title="一盏花灯，慢慢做", fade_in=True),
            dict(kind="photo", src="2026-09-27 221926.jpg", dur=3.0, mode="fill", kb="out",
                 text="大人小孩，围坐一桌"),
            dict(kind="photo", src="2026-09-27 222000.jpg", dur=3.0, mode="fill", kb="in",
                 text="刷上浆糊"),
            dict(kind="photo", src="2026-09-27 221917.jpg", dur=3.0, mode="fill", kb="out",
                 text="把整个秋天，贴上去"),
            dict(kind="photo", src="2026-09-27 222424.jpg", dur=3.0, mode="fill", kb="in",
                 text="最认真的那一个"),
            dict(kind="photo", src="2026-09-27 222457.jpg", dur=3.2, mode="fill", kb="out",
                 text="但愿人长久"),
            dict(kind="video", src="2026-09-27 221935.mp4", ss=0.5, dur=3.5, mode="blur",
                 end="溪田花境 · 2026中秋", fade_out=True),
        ],
    },
    "3_放花灯": {
        "bgm": "sample2.m4a",
        "shots": [
            dict(kind="photo", src="2026-09-27 222110.jpg", dur=3.0, mode="fill", kb="in",
                 title="把心愿，放进水里", fade_in=True),
            dict(kind="photo", src="2026-09-27 222043.jpg", dur=3.0, mode="fill", kb="out",
                 text="莲花灯，一瓣一瓣"),
            dict(kind="photo", src="2026-09-27 222103.jpg", dur=3.2, mode="fill", kb="in",
                 text="轻轻地，推出去"),
            dict(kind="photo", src="2026-09-27 222122.jpg", dur=3.0, mode="fill", kb="out",
                 text="心愿顺水，慢慢走远"),
            dict(kind="photo", src="2026-09-27 222127.jpg", dur=3.5, mode="fill", kb="in",
                 text="姐妹俩看着，谁也没说话"),
            dict(kind="photo", src="2026-09-27 222306.jpg", dur=3.8, mode="blur",
                 end="中秋快乐 · 溪田花境", fade_out=True),
        ],
    },
}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        print("  CMD:", " ".join(args)[:400])
        print("  ERR:", r.stderr[-600:])
        raise SystemExit(1)

def txtfile(content, idx):
    os.makedirs(TXT, exist_ok=True)
    p = os.path.join(TXT, f"{idx:02d}.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p

def drawtext(tf, style):
    if style == "title":
        return (f"drawtext=fontfile='{FONT}':textfile='{tf}':fontsize=88:fontcolor=white:"
                f"box=1:boxcolor=black@0.30:boxborderw=26:x=(w-text_w)/2:y=h*0.30:"
                f"shadowx=2:shadowy=2:shadowcolor=black@0.5")
    if style == "end":
        return (f"drawtext=fontfile='{FONT}':textfile='{tf}':fontsize=64:fontcolor=white:"
                f"box=1:boxcolor=black@0.32:boxborderw=22:x=(w-text_w)/2:y=h*0.42")
    return (f"drawtext=fontfile='{FONT}':textfile='{tf}':fontsize=54:fontcolor=white:"
            f"box=1:boxcolor=black@0.34:boxborderw=18:x=(w-text_w)/2:y=h-360:"
            f"shadowx=1:shadowy=1:shadowcolor=black@0.5")

def kb_expr(direction, frames):
    if direction == "in":
        z = f"min(1+0.14*on/{frames},1.14)"
    else:
        z = f"max(1.14-0.14*on/{frames},1.0)"
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS}"

def render_shot(shot, out_path, ti):
    dur = shot["dur"]; frames = int(round(dur * FPS))
    src = os.path.join(RAW, shot["src"])
    fades = ""
    if shot.get("fade_in"):
        fades += ",fade=t=in:st=0:d=0.5"
    if shot.get("fade_out"):
        fades += f",fade=t=out:st={max(0,dur-0.9):.2f}:d=0.9"
    texts = []
    if shot.get("title"):
        texts.append(("title", shot["title"], 0.3, dur - 0.3))
    elif shot.get("end"):
        texts.append(("end", shot["end"], 0.3, dur - 0.3))
    if shot.get("text"):
        texts.append(("sub", shot["text"], 0.3, dur - 0.3))
    dt = ""
    for style, content, a, b in texts:
        tf = txtfile(content, ti); ti += 1
        dt += "," + drawtext(tf, style) + f":enable='between(t,{a},{b})'"
    sharp = ",unsharp=5:5:0.6:5:5:0.0" if shot.get("unsharp") else ""
    lift = ",eq=brightness=0.05:gamma=1.08:saturation=1.05" if shot.get("lift") else ""

    if shot["kind"] == "video":
        vf = (f"fps={FPS},scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
              f"crop={W*2}:{H*2}{sharp}{lift},scale={W}:{H}{fades}{dt},format=yuv420p")
        run([FFMPEG, "-y", "-ss", f"{shot['ss']}", "-i", src, "-t", f"{dur}",
             "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", out_path])
    else:
        if shot["mode"] == "fill":
            pre = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
                   f"crop={W*2}:{H*2}[k];[k]{kb_expr(shot['kb'], frames)}")
        else:  # blur
            pre = (f"[0:v]split[a][b];"
                   f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                   f"boxblur=24:2,eq=brightness=-0.05[bg];"
                   f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
                   f"[bg][fg]overlay=(W-w)/2:(H-h)/2,scale={W*2}:{H*2}[k];"
                   f"[k]{kb_expr(shot.get('kb') or 'in', frames)}")
        vf_chain = pre + f",format=yuv420p{fades}{dt},format=yuv420p[v]"
        run([FFMPEG, "-y", "-loop", "1", "-i", src, "-t", f"{dur}",
             "-filter_complex", vf_chain, "-map", "[v]", "-an",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", out_path])

def build_video(name, spec):
    print(f"== {name} ==")
    vdir = os.path.join(BUILD, name)
    shutil.rmtree(vdir, ignore_errors=True); os.makedirs(vdir)
    segs = []
    ti = 0
    for i, shot in enumerate(spec["shots"]):
        seg = os.path.join(vdir, f"shot{i:02d}.mp4")
        print(f"  shot{i:02d}: {shot['src']} {shot['dur']}s")
        render_shot(shot, seg, ti)
        ti += 1
        segs.append(seg)
    lst = os.path.join(vdir, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    total = sum(s["dur"] for s in spec["shots"])
    bgm = os.path.join(BGM_DIR, spec["bgm"])
    out = os.path.join(CUTS, f"{name}.mp4")
    fc = (f"[0:v][lg]overlay=x=W-w-36:y=36,format=yuv420p[v];"
          f"[1:v]scale=150:150,colorchannelmixer=aa=0.78[lg];"
          f"[2:a]atrim=0:{total},afade=t=in:st=0:d=0.6,"
          f"afade=t=out:st={total-1.8:.2f}:d=1.8,volume=0.9[a]")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-i", LOGO, "-stream_loop", "50", "-i", bgm,
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-t", f"{total}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", out])
    print(f"  => {out} ({total:.1f}s)")

def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    os.makedirs(CUTS, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    for name, spec in VIDEOS.items():
        if only and not any(o in name for o in only):
            continue
        build_video(name, spec)

if __name__ == "__main__":
    main()
