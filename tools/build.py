#!/usr/bin/env python3
"""apps.importants-studio.com 정적 사이트 생성. 출시 앱은 App Store 공개 정보(lookup)를, 미출시 앱은 스토어 등록 문구 파일을 씀.
문구: 앱 설명은 각 앱 스토어 문구(모델 생성본), 사이트 공통 문구는 tools/site_copy.json(모델 생성본). 실행: python3 tools/build.py"""
import json, os, re, html, shutil, urllib.request, datetime
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
BASE = "https://apps.importants-studio.com"
C = json.load(open("tools/site_copy.json")); APPS = json.load(open("tools/apps.json"))
MAIL = "contact@importants-studio.com"
e = lambda s: html.escape(s or "", quote=True)
OUT = "docs"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)

def img_save(src, dst, width):
    im = Image.open(src).convert("RGB")
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)

def fetch(url, dst):
    with urllib.request.urlopen(url, timeout=60) as r, open(dst + ".tmp", "wb") as f: f.write(r.read())
    return dst + ".tmp"

def desc_html(text):
    out, items = [], []
    def flush():
        if items: out.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"); items.clear()
    for line in text.split("\n"):
        s = line.strip()
        if not s: flush(); continue
        m = re.match(r"^[•\-·]\s*(.+)", s)
        if m: items.append(m.group(1)); continue
        flush()
        if re.match(r"^■\s*", s) or (len(s) < 24 and not s.endswith((".", "요", "다"))): out.append(f"<h3>{e(re.sub(r'^■\s*', '', s))}</h3>")
        else: out.append(f"<p>{e(s)}</p>")
    flush(); return "\n".join(out)

apps = []
for a in APPS:
    d = os.path.join(OUT, a["slug"]); os.makedirs(d)
    if a["released"]:
        r = json.load(urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={a['id']}&country=kr"))["results"][0]
        name, desc = r["trackName"], r["description"]
        sub = ""  # lookup엔 부제가 없음 → 이름의 '-' 뒤를 부제로
        if " - " in name: name, sub = name.split(" - ", 1)
        img_save(fetch(r["artworkUrl512"], f"{d}/icon"), f"{d}/icon.jpg", 512)
        shots = []
        for i, u in enumerate(r.get("screenshotUrls", [])[:6], 1):
            img_save(fetch(u, f"{d}/s{i}"), f"{d}/s{i}.jpg", 600); shots.append(f"s{i}.jpg")
        promo, category, store = "", ("GameApplication" if r.get("primaryGenreName") == "Games" else "EntertainmentApplication"), r["trackViewUrl"].split("?")[0]
    else:
        L = a["local"]; j = json.load(open(L["store_json"]))
        name = L.get("name") or j.get("name", "").split(":")[0]
        sub = j.get("name", "").split(":", 1)[1].strip() if ":" in j.get("name", "") else j.get("subtitle", ""); promo = j.get("promotional_text") or j.get("promo", ""); desc = j.get("description", "")
        img_save(L["icon"], f"{d}/icon.jpg", 512); shots = []
        for i, p in enumerate(L["shots"], 1): img_save(p, f"{d}/s{i}.jpg", 600); shots.append(f"s{i}.jpg")
        category, store = L["category"], f"https://apps.apple.com/kr/app/id{a['id']}"
    for f in os.listdir(d):
        if f.endswith(".tmp"): os.remove(os.path.join(d, f))
    apps.append({**a, "name": name, "sub": sub, "promo": promo, "desc": desc, "shots": shots, "category": category, "store": store})


def sections(text):
    """설명을 (제목, [항목]) 묶음으로. 첫 덩어리(제목 없는 문단)는 소개문"""
    intro, secs, cur = [], [], None
    for line in text.split("\n"):
        t = line.strip()
        if not t: continue
        bullet = re.match(r"^[•\-·]\s*(.+)", t)
        heading = re.match(r"^■\s*(.+)", t) or (not bullet and len(t) < 26 and not t.endswith((".", "요", "다", "!")) and t)
        if heading:
            cur = [heading.group(1) if hasattr(heading, "group") else t, []]; secs.append(cur)
        elif cur is None: intro.append(t)
        else: cur[1].append(bullet.group(1) if bullet else t)
    return intro, [x for x in secs if x[1]]

def tint(hexc, k):
    h = hexc.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(round(255 - (255 - c) * k) for c in (r, g, b))

CSS = """@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;color:#191f28;background:#fff;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-x:hidden}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%}
.in{max-width:1120px;margin:0 auto;padding:0 24px}
nav{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.86);backdrop-filter:saturate(180%) blur(16px);-webkit-backdrop-filter:saturate(180%) blur(16px);border-bottom:1px solid rgba(0,0,0,.05)}
nav .in{display:flex;align-items:center;justify-content:space-between;height:60px}nav b{font-size:17px;letter-spacing:-.02em}nav .links{display:flex;gap:22px;font-size:15px;color:#4e5968}nav .links a:hover{color:#191f28}
.hero{padding:120px 0 96px}.hero h1{font-size:clamp(40px,7vw,76px);line-height:1.15;letter-spacing:-.04em;margin:0;font-weight:800}.hero p{font-size:clamp(17px,2vw,21px);color:#4e5968;margin:28px 0 0}
.app{padding:110px 0;background:var(--bg)}.app .in{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center}.app.rev .copy{order:2}
.app .icon{width:76px;height:76px;border-radius:19px;box-shadow:0 8px 24px rgba(0,0,0,.10)}.app .name{font-size:17px;font-weight:700;color:var(--c);margin:22px 0 10px}
.app h2{font-size:clamp(30px,4.2vw,48px);line-height:1.22;letter-spacing:-.035em;margin:0 0 18px;font-weight:800}.app .lead{font-size:18px;line-height:1.7;color:#4e5968;margin:0 0 30px}
.btns{display:flex;gap:10px;flex-wrap:wrap}.btn{display:inline-flex;align-items:center;height:52px;padding:0 22px;border-radius:14px;font-weight:700;font-size:16px;transition:transform .15s}.btn:active{transform:scale(.97)}
.btn.main{background:var(--c);color:#fff}.btn.sub{background:#fff;color:#191f28;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}.soon{display:inline-flex;align-items:center;height:52px;padding:0 18px;border-radius:14px;background:rgba(0,0,0,.05);color:#6b7684;font-weight:600}
.phones{position:relative;height:560px}.phones img{position:absolute;width:250px;border-radius:30px;box-shadow:0 24px 60px rgba(0,0,0,.16)}
.phones img:nth-child(1){left:8%;top:40px;z-index:1}.phones img:nth-child(2){left:42%;top:0;z-index:2}
.dhero{padding:96px 0 40px;background:var(--bg)}.dhero .in{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:end}.dhero .icon{width:96px;height:96px;border-radius:24px;box-shadow:0 10px 30px rgba(0,0,0,.12)}
.dhero h1{font-size:clamp(34px,5vw,56px);line-height:1.18;letter-spacing:-.04em;margin:26px 0 16px;font-weight:800}.dhero .lead{font-size:19px;color:#4e5968;line-height:1.7;margin:0 0 30px}
.dhero .shot{justify-self:center;width:300px;border-radius:34px;box-shadow:0 30px 70px rgba(0,0,0,.18);margin-bottom:-120px}
.feat{padding:110px 0}.feat:first-of-type{padding-top:200px}.feat .in{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}.feat.rev .txt{order:2}
.feat .k{font-size:15px;font-weight:700;color:var(--c);margin-bottom:12px}.feat h3{font-size:clamp(26px,3.4vw,38px);line-height:1.28;letter-spacing:-.03em;margin:0 0 22px;font-weight:800}
.feat ul{list-style:none;padding:0;margin:0}.feat li{font-size:17px;line-height:1.7;color:#4e5968;padding-left:20px;position:relative;margin:8px 0}.feat li:before{content:"";position:absolute;left:2px;top:.72em;width:6px;height:6px;border-radius:3px;background:var(--c)}
.feat.solo{padding:64px 0}.feat.solo .in{grid-template-columns:1fr;max-width:760px}.feat .shot{justify-self:center;width:290px;border-radius:32px;box-shadow:0 24px 60px rgba(0,0,0,.14)}
.cta{padding:110px 0;text-align:center;background:var(--bg)}.cta h2{font-size:clamp(28px,4vw,44px);letter-spacing:-.035em;margin:18px 0 28px;font-weight:800}.cta .icon{width:84px;height:84px;border-radius:21px;margin:0 auto}
footer{padding:48px 0 64px;background:#f9fafb;color:#6b7684;font-size:14px}footer .in{display:flex;gap:20px;flex-wrap:wrap;justify-content:space-between}footer .links{display:flex;gap:18px}
.r{opacity:0;transform:translateY(28px);transition:opacity .8s cubic-bezier(.2,.7,.2,1),transform .8s cubic-bezier(.2,.7,.2,1)}.r.on{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.r{opacity:1;transform:none;transition:none}}
@media(max-width:600px){nav .links{display:none}}
@media(max-width:820px){.app .in,.feat .in,.dhero .in{grid-template-columns:1fr;gap:36px}.app.rev .copy,.feat.rev .txt{order:0}.phones{height:440px}.phones img{width:200px}.phones img:nth-child(1){left:2%}.phones img:nth-child(2){left:40%}
.hero{padding:80px 0 64px}.app,.feat{padding:80px 0}.feat:first-of-type{padding-top:160px}.dhero .shot{width:240px;margin-bottom:-100px}.feat .shot{width:250px}}"""
open(f"{OUT}/style.css", "w").write(CSS)
JS = "document.addEventListener('DOMContentLoaded',()=>{const o=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('on');o.unobserve(x.target)}}),{threshold:.15});document.querySelectorAll('.r').forEach(n=>o.observe(n))})"
open(f"{OUT}/app.js", "w").write(JS)

def page(title, desc, path, body, extra=""):
    nav = "".join(f'<a href="/{a["slug"]}/">{e(a["name"])}</a>' for a in apps)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Importants Studio"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}">
<link rel="stylesheet" href="/style.css"><script src="/app.js" defer></script>{extra}</head><body>
<nav><div class="in"><a href="/"><b>Importants Studio</b></a><div class="links">{nav}</div></div></nav>
{body}
<footer><div class="in"><span>© {datetime.date.today().year} Importants Studio</span><div class="links"><a href="/">{e(C['LINK_ALL'])}</a><a href="mailto:{MAIL}">{e(C['LINK_CONTACT'])}</a></div></div></footer>
</body></html>"""

def store_btn(a, cls="main"):
    return f'<a class="btn {cls}" href="{e(a["store"])}">{e(C["BTN_STORE"])}</a>' if a["released"] else f'<span class="soon">{e(C["SOON"])}</span>'

for a in apps:
    intro, secs = sections(a["desc"])
    a["intro"] = intro; a["secs"] = secs
    a["headline"] = a["promo"] or (intro[0] if intro else a["sub"])
    a["bg"] = tint(a["color"], 0.07)

# 메인
blocks = []
for i, a in enumerate(apps):
    ph = "".join(f'<img src="/{a["slug"]}/{s}" alt="" loading="lazy">' for s in a["shots"][:2])
    blocks.append(f"""<section class="app{' rev' if i % 2 else ''}" style="--c:{a['color']};--bg:{a['bg']}"><div class="in">
<div class="copy r"><img class="icon" src="/{a['slug']}/icon.jpg" alt="{e(a['name'])} 아이콘"><div class="name">{e(a['name'])}</div><h2>{e(a['sub'])}</h2><p class="lead">{e(a['headline'])}</p>
<div class="btns"><a class="btn main" href="/{a['slug']}/">{e(C['BTN_MORE'])}</a>{store_btn(a, 'sub')}</div></div>
<div class="phones r">{ph}</div></div></section>""")
hl = "<br>".join(e(x.strip()) for x in C["STUDIO_HEADLINE"].split("/"))
open(f"{OUT}/index.html", "w").write(page("Importants Studio", C["STUDIO_SUB"], "/",
    f'<header class="hero"><div class="in r"><h1>{hl}</h1><p>{e(C["STUDIO_SUB"])}</p></div></header>' + "".join(blocks)))

# 앱 상세
for a in apps:
    title = f"{a['name']} - {a['sub']}" if a["sub"] else a["name"]
    meta = (a["headline"])[:150]
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": a["name"], "operatingSystem": "iOS", "applicationCategory": a["category"],
          "description": meta, "image": f"{BASE}/{a['slug']}/icon.jpg", "url": f"{BASE}/{a['slug']}/", "author": {"@type": "Organization", "name": "Importants Studio"}}
    if a["released"]: ld.update({"downloadUrl": a["store"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}})
    extra = f'\n<meta property="og:image" content="{BASE}/{a["slug"]}/icon.jpg"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    if a["released"]: extra += f'\n<meta name="apple-itunes-app" content="app-id={a["id"]}">'
    shots = a["shots"]
    feats = []
    k = 0
    for i, (h, items) in enumerate(a["secs"][:7]):
        n = a["pair"][i] if i < len(a["pair"]) else 0
        shot = shots[n - 1] if n and n <= len(shots) else ""
        rev = k % 2 == 1; k += 1 if shot else 0
        li = "".join(f"<li>{e(x)}</li>" for x in items[:5])
        feats.append(f"""<section class="feat{' rev' if rev else ''}{'' if shot else ' solo'}"><div class="in"><div class="txt r"><div class="k">{i + 1:02d}</div><h3>{e(h)}</h3><ul>{li}</ul></div>
{f'<img class="shot r" src="{shot}" alt="{e(a["name"])} {e(h)} 화면" loading="lazy">' if shot else ''}</div></section>""")
    body = f"""<main style="--c:{a['color']};--bg:{a['bg']}">
<section class="dhero"><div class="in"><div class="r"><img class="icon" src="icon.jpg" alt="{e(a['name'])} 아이콘"><h1>{e(a['name'])}<br><span style="color:var(--c)">{e(a['sub'])}</span></h1><p class="lead">{e(a['headline'])}</p><div class="btns">{store_btn(a)}</div></div>
{f'<img class="shot r" src="{shots[0]}" alt="{e(a["name"])} 대표 화면">' if shots else ''}</div></section>
{''.join(feats)}
<section class="cta"><div class="in r"><img class="icon" src="icon.jpg" alt=""><h2>{e(a['name'])}</h2><div class="btns" style="justify-content:center">{store_btn(a)}<a class="btn sub" href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></div></div></section></main>"""
    open(f"{OUT}/{a['slug']}/index.html", "w").write(page(title, meta, f"/{a['slug']}/", body, extra))

today = datetime.date.today().isoformat()
open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>" for p in ["/"] + [f"/{a['slug']}/" for a in apps]) + "</urlset>\n")
open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(f"{OUT}/CNAME", "w").write("apps.importants-studio.com\n")
open(f"{OUT}/.nojekyll", "w").write("")
print("built", [(a["slug"], len(a["secs"])) for a in apps])
