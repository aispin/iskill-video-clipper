#!/usr/bin/env python3
"""生成单 shader 转场片段 index.html（shader-transition-clip 已验证契约）。

用法: python3 gen_index.py <shader名>   # 在本目录运行，写 ./index.html
契约: scenes=[sa,sb]，单转场 {time:0.15, duration:1.7}，总长 2s，bgColor #000000。
"""
import sys

shader = sys.argv[1]
HTML = f'''<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <script src="assets/shader-transitions.global.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      .scene {{ position: absolute; inset: 0; }}
      .scene img {{ width: 1080px; height: 1920px; object-fit: cover; display: block; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="2"
         data-width="1080" data-height="1920">
      <div id="sa" class="scene"><img src="assets/frameA.jpg" /></div>
      <div id="sb" class="scene"><img src="assets/frameB.jpg" /></div>
      <script>
        const tl = gsap.timeline({{ paused: true }});
        window.__timelines = window.__timelines || {{}};
        window.__timelines["main"] = HyperShader.init({{
          bgColor: "#000000",
          scenes: ["sa", "sb"],
          transitions: [ {{ time: 0.15, shader: "{shader}", duration: 1.7, ease: "none" }} ],
          timeline: tl,
        }});
        tl.seek(0);
      </script>
    </div>
  </body>
</html>
'''
open("index.html", "w").write(HTML)
print("gen ok:", shader)
