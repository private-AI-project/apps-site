#!/usr/bin/env python3
"""앱 소개 페이지 분위기 이미지(OpenAI gpt-image-2, 1536x1024 high). 키는 ~/blog-automation/.env OPENAI_API_KEY(화면에 찍지 않음).
사람 얼굴·글자·로고 없음. 결과 raw/ai/<slug>.png. 실행: python3 tools/gen_images.py [slug...]"""
import json, os, sys, base64, urllib.request
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = next(l.split("=", 1)[1].strip().strip('"') for l in open(os.path.expanduser("~/blog-automation/.env")) if l.startswith("OPENAI_API_KEY="))
COMMON = "No people, no faces, no text, no letters, no numbers, no logos, no screens with content. Soft natural light, shallow depth of field, premium editorial product-website photography, calm composition with empty space on one side."
P = {
 "reckoner": "A quiet community sports hall in the evening: a blue table tennis table with a white net and two red paddles resting on it, a badminton shuttlecock nearby, warm overhead gym lights, polished wooden floor. Off-white and orange accent tones.",
 "floorlog": "A calm modern Korean apartment living room at night seen from the floor level, soft warm lamp light, wooden floor, a small notebook and a smartphone face-down on a low table, quiet atmosphere, deep teal and warm beige tones.",
 "maejeum": "A serene still life on traditional Korean hanji paper: a few white chrysanthemums, a small celadon incense holder with a thin wisp of smoke, muted beige and deep green tones, minimal and respectful, top-down soft light.",
 "officekit": "A tidy bright desk seen from above: neatly stacked white paper documents, a clipboard, a pen, a paper clip, and a plain smartphone face-down, clean white and soft blue tones, minimal modern office.",
 "lucky-bite": "Playful 3D clay-style objects floating on a warm cream background: an orange ladder, red dice with white dots, wooden drawing sticks in a paper cup with one red tip, a gold coin, small confetti, soft shadows, cute toy-like render.",
 "quiz-bite": "Playful 3D clay-style objects on a soft sky-blue background: a glossy orange question mark, a stack of colorful books, a small owl figurine, a winding map path with tiny trees, soft shadows, cute toy-like render.",
}
for slug in (sys.argv[1:] or P):
    out = f"raw/ai/{slug}.png"
    if os.path.exists(out): print("skip", slug); continue
    body = {"model": "gpt-image-2", "prompt": P[slug] + " " + COMMON, "size": "1536x1024", "quality": "high", "n": 1}
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + KEY})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    open(out, "wb").write(base64.b64decode(d["data"][0]["b64_json"])); print("ok", slug)
