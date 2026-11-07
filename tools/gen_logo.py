#!/usr/bin/env python3
"""스튜디오 로고 시안(OpenAI gpt-image-2, 1024x1024 high). 키는 ~/blog-automation/.env OPENAI_API_KEY(화면에 찍지 않음).
결과 raw/logo/<id>.png. 실행: python3 tools/gen_logo.py [id...]"""
import json, os, sys, base64, urllib.request
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = next(l.split("=", 1)[1].strip().strip('"\'') for l in open(os.path.expanduser("~/blog-automation/.env")) if l.startswith("OPENAI_API_KEY="))
COMMON = ("App-icon style logo mark for a small software studio named 'Importants Studio' that makes iPhone apps and free web tools. "
          "Single centered symbol on a rounded-square tile, flat vector, bold simple geometry, must stay recognizable at 16x16 favicon size, "
          "no text, no letters other than the mark itself, no gradients overload, no 3D clutter, plain light background around the tile, premium and modern like Toss, Linear, Notion app icons.")
P = {
 "1": "Concept: the letter I that doubles as an exclamation mark (important). A tall rounded white bar with a vivid orange dot below it on a near-black tile.",
 "2": "Concept: an exclamation mark made of two stacked rounded shapes, warm orange tile, deep charcoal mark, playful but minimal.",
 "3": "Concept: a stylized bookmark / pin shape that hints at 'important', combined with a small spark, charcoal and orange palette.",
 "4": "Concept: a monogram 'i' whose dot is a glowing orange circle like a notification badge, on a near-black tile.",
 "5": "Concept: abstract asterisk / star mark meaning 'important', geometric rounded strokes, orange on deep charcoal.",
 "6": "Concept: three small app tiles stacked to form an exclamation mark, the bottom tile orange, others off-white, on a charcoal tile.",
}
os.makedirs("raw/logo", exist_ok=True)
for k in (sys.argv[1:] or P):
    out = f"raw/logo/{k}.png"
    if os.path.exists(out): print("skip", k); continue
    body = {"model": "gpt-image-2", "prompt": P[k] + " " + COMMON, "size": "1024x1024", "quality": "high", "n": 1}
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    open(out, "wb").write(base64.b64decode(d["data"][0]["b64_json"])); print("ok", k)
