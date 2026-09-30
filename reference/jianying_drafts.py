#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
溪田花境 · 中秋短视频 —— 剪映精修草稿生成
基于 jianying-editor-skill (JyWrapper/pyJianYingDraft)：
生成带转场、文本动画、BGM 的剪映专业版草稿，打开剪映即可预览/精修/导出。
用法: python jianying_drafts.py [1|2|3|all]
"""
import os
import sys

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_ROOT = os.path.expanduser("~/.workbuddy/skills/jianying-editor")
os.environ["JY_SKILL_ROOT"] = SKILL_ROOT
# 注入 ffprobe/ffmpeg（static_ffmpeg pip 包自带，媒体归一化探测需要）
from static_ffmpeg import run as _sf_run  # noqa: E402
_ff, _fp = _sf_run.get_or_fetch_platform_executables_else_raise()
os.environ["PATH"] = os.path.dirname(_ff) + os.pathsep + os.environ.get("PATH", "")
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))
from jy_wrapper import JyProject  # noqa: E402

RAW = os.path.join(WS, "260926 中秋 活动", "raw")
BGM_DIR = os.path.join(WS, ".recon", "bgm")

# ---------- 分镜表（与 .build/build_videos.py 同源，剪映版增强） ----------
# kind: video|photo; source_start 仅 video 有效
VIDEOS = {
    "1_打糍粑": {
        "bgm": "sample1.m4a",
        "shots": [
            dict(kind="video", src="2026-09-27 222718.mp4", ss="1s", dur="3s",
                 title="中秋，来溪田打一次糍粑"),
            dict(kind="photo", src="2026-09-27 221756.jpg", dur="3.2s", text="刚蒸好的糯米，倒进石臼"),
            dict(kind="photo", src="2026-09-27 221753.jpg", dur="3.2s", text="你一槌，我一槌"),
            dict(kind="photo", src="2026-09-27 221805.jpg", dur="3.2s", text="打出糯米的韧劲"),
            dict(kind="video", src="2026-09-27 222706.mp4", ss="36s", dur="5s",
                 text="压成饼，团圆就有了形状"),
            dict(kind="photo", src="2026-09-27 221803.jpg", dur="3.5s", end="溪田花境 · 2026中秋"),
        ],
    },
    "2_做灯笼": {
        "bgm": "sample2.m4a",
        "shots": [
            dict(kind="video", src="2026-09-27 222718.mp4", ss="6s", dur="3s",
                 title="一盏花灯，慢慢做"),
            dict(kind="photo", src="2026-09-27 221926.jpg", dur="3s", text="大人小孩，围坐一桌"),
            dict(kind="photo", src="2026-09-27 222000.jpg", dur="3s", text="刷上浆糊"),
            dict(kind="photo", src="2026-09-27 221917.jpg", dur="3s", text="把整个秋天，贴上去"),
            dict(kind="photo", src="2026-09-27 222424.jpg", dur="3s", text="最认真的那一个"),
            dict(kind="photo", src="2026-09-27 222457.jpg", dur="3.2s", text="但愿人长久"),
            dict(kind="video", src="2026-09-27 221935.mp4", ss="0.5s", dur="3.5s",
                 end="溪田花境 · 2026中秋"),
        ],
    },
    "3_放花灯": {
        "bgm": "sample2.m4a",
        "shots": [
            dict(kind="photo", src="2026-09-27 222110.jpg", dur="3s",
                 title="把心愿，放进水里"),
            dict(kind="photo", src="2026-09-27 222043.jpg", dur="3s", text="莲花灯，一瓣一瓣"),
            dict(kind="photo", src="2026-09-27 222103.jpg", dur="3.2s", text="轻轻地，推出去"),
            dict(kind="photo", src="2026-09-27 222122.jpg", dur="3s", text="心愿顺水，慢慢走远"),
            dict(kind="photo", src="2026-09-27 222127.jpg", dur="3.5s", text="姐妹俩看着，谁也没说话"),
            dict(kind="photo", src="2026-09-27 222306.jpg", dur="3.8s", end="中秋快乐 · 溪田花境"),
        ],
    },
}

# 镜头间转场（按序循环取用，剪映内置转场名）
TRANSITIONS = ["叠化", "亮点模糊", "叠化", "轻微抖动"]


def hms_to_sec(t):
    t = str(t)
    if t.endswith("s"):
        return float(t[:-1])
    return float(t)


def build(name, spec):
    proj = JyProject(project_name=f"溪田中秋-{name}-精修",
                     width=1080, height=1920, overwrite=True)
    print(f"== {name} ==")
    cursor = 0.0
    segments = []
    for shot in spec["shots"]:
        src = os.path.join(RAW, shot["src"])
        d = hms_to_sec(shot["dur"])
        seg = proj.add_media_safe(src, start_time=f"{cursor}s", duration=shot["dur"],
                                  source_start=(shot.get("ss", "0s") if shot["kind"] == "video" else "0s"),
                                  track_name="主轨")
        if seg is None:
            print(f"  ❌ add failed: {shot['src']}")
            return
        segments.append(seg)
        # 文本：标题 / 过程字幕 / 落款
        if shot.get("title"):
            proj.add_text_simple(shot["title"], start_time=f"{cursor + 0.3}s",
                                 duration=f"{d - 0.6}s", track_name="文本")
        elif shot.get("end"):
            proj.add_text_simple(shot["end"], start_time=f"{cursor + 0.3}s",
                                 duration=f"{d - 0.6}s", track_name="文本")
        elif shot.get("text"):
            proj.add_text_simple(shot["text"], start_time=f"{cursor + 0.3}s",
                                 duration=f"{d - 0.6}s", track_name="文本")
        print(f"  + {shot['src']} @{cursor:.1f}s ({d}s)")
        cursor += d
    # 转场
    for i, seg in enumerate(segments[:-1]):
        tname = TRANSITIONS[i % len(TRANSITIONS)]
        try:
            proj.add_transition_simple(tname, video_segment=seg, duration="0.6s")
            print(f"  ~ 转场 {tname} after shot{i}")
        except Exception as e:
            print(f"  ⚠️ 转场 {tname} 失败: {e}")
    # BGM：循环铺满全片
    bgm = os.path.join(BGM_DIR, spec["bgm"])
    bgm_dur = 11.5
    t = 0.0
    while t < cursor - 0.5:
        remain = cursor - t
        proj.add_audio_safe(bgm, start_time=f"{t}s",
                            duration=f"{min(bgm_dur, remain):.2f}s", track_name="BGM")
        t += bgm_dur
    proj.save()
    print(f"  => 草稿已保存: 溪田中秋-{name}-精修 ({cursor:.1f}s)")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, spec in VIDEOS.items():
        if which != "all" and which not in name:
            continue
        try:
            build(name, spec)
        except Exception as e:
            print(f"❌ {name} 生成失败: {e}")
            import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
