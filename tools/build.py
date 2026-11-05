#!/usr/bin/env python3
"""apps.importants-studio.com 정적 사이트(서비스 소개형). 문구: tools/marketing.json·site_copy.json(로컬 LLM 생성), 화면: 각 앱 원본 캡처(raw_dir).
출시 앱은 App Store 주소·아이콘을 lookup으로. 실행: python3 tools/build.py → docs/"""
import json, os, html, shutil, urllib.request, datetime
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
BASE = "https://apps.importants-studio.com"; MAIL = "contact@importants-studio.com"
C = json.load(open("tools/site_copy.json")); M = json.load(open("tools/marketing.json")); APPS = json.load(open("tools/apps.json"))
OUT = "docs"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
e = lambda s: html.escape(s or "", quote=True)
br = lambda s: "<br>".join(e(x.strip()) for x in (s or "").split("/"))

def save(src, dst, width, fmt="WEBP"):
    im = Image.open(src); im = im.convert("RGBA" if fmt == "PNG" else "RGB")
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, fmt, quality=88, method=6) if fmt == "WEBP" else im.save(dst, fmt)
    return os.path.basename(dst)

def tint(hexc, k):
    h = hexc.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(round(255 - (255 - c) * k) for c in (r, g, b))

apps = []
for a in APPS:
    d = os.path.join(OUT, a["slug"]); os.makedirs(d)
    if a["released"]:
        r = json.load(urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={a['id']}&country=kr"))["results"][0]
        tmp = os.path.join(d, "_icon")
        with urllib.request.urlopen(r["artworkUrl512"].replace("512x512bb", "1024x1024bb"), timeout=60) as f: open(tmp, "wb").write(f.read())
        save(tmp, f"{d}/icon.png", 512, "PNG"); os.remove(tmp)
        store = r["trackViewUrl"].split("?")[0]; cat = "GameApplication" if r.get("primaryGenreName") == "Games" else "EntertainmentApplication"
    else:
        save(a["icon"], f"{d}/icon.png", 512, "PNG"); store = f"https://apps.apple.com/kr/app/id{a['id']}"
        cat = "UtilitiesApplication" if a["slug"] == "officekit" else "LifestyleApplication"
    m = M[a["slug"]]
    shots = {}
    for s in [x["screen"] for x in m["scenes"]] + a["hero"]:
        shots[s] = save(os.path.join(a["raw_dir"], s + ".png"), f"{d}/{s}.webp", 900)
    apps.append({**a, "m": m, "store": store, "cat": cat, "shots": shots, "bg": tint(a["color"], 0.08), "bg2": tint(a["color"], 0.16)})

CSS = """@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;color:#191f28;background:#fff;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-x:hidden}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%}.in{max-width:1140px;margin:0 auto;padding:0 24px}
nav{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.82);backdrop-filter:saturate(180%) blur(18px);-webkit-backdrop-filter:saturate(180%) blur(18px)}
nav .in{display:flex;align-items:center;justify-content:space-between;height:62px}nav b{font-size:17px;letter-spacing:-.02em}nav .links{display:flex;gap:24px;font-size:15px;color:#4e5968}nav .links a:hover{color:#191f28}
.phone{position:relative;width:var(--w,290px);aspect-ratio:1320/2868;border-radius:calc(var(--w,290px)*.16);background:#0b0b0d;padding:calc(var(--w,290px)*.035);box-shadow:0 30px 80px rgba(17,24,39,.22),0 8px 20px rgba(17,24,39,.10)}
.phone img{width:100%;height:100%;object-fit:cover;border-radius:calc(var(--w,290px)*.13)}
.btn{display:inline-flex;align-items:center;justify-content:center;height:56px;padding:0 26px;border-radius:16px;font-weight:700;font-size:17px;transition:transform .15s,opacity .15s}.btn:active{transform:scale(.97)}
.btn.main{background:var(--c);color:#fff}.btn.ghost{background:#fff;box-shadow:inset 0 0 0 1px rgba(0,0,0,.09)}.soon{display:inline-flex;align-items:center;height:56px;padding:0 22px;border-radius:16px;background:rgba(0,0,0,.06);color:#6b7684;font-weight:700}
.chip{display:inline-flex;align-items:center;gap:10px;font-weight:700;font-size:16px}.chip img{width:44px;height:44px;border-radius:11px;box-shadow:0 4px 12px rgba(0,0,0,.12)}
/* 메인 */
.shero{padding:130px 0 90px}.shero h1{font-size:clamp(42px,7.4vw,84px);line-height:1.12;letter-spacing:-.045em;margin:0;font-weight:800}.shero p{font-size:clamp(17px,2vw,21px);color:#4e5968;margin:28px 0 0}
.tile{margin:0 24px 24px;border-radius:40px;background:var(--bg);overflow:hidden}.tile .in{display:grid;grid-template-columns:1.05fr .95fr;gap:40px;align-items:center;padding-top:90px;padding-bottom:0}
.tile h2{font-size:clamp(34px,4.6vw,56px);line-height:1.15;letter-spacing:-.04em;margin:22px 0 18px;font-weight:800}.tile p{font-size:19px;color:#4e5968;line-height:1.65;margin:0 0 30px}
.tile .stage{display:flex;gap:18px;justify-content:center;align-items:flex-end;height:520px;overflow:hidden}.tile .stage .phone{--w:240px;margin-bottom:-90px}.tile .stage .phone:last-child{--w:260px;margin-bottom:-40px}
.tile .copy{padding-bottom:90px}.btns{display:flex;gap:10px;flex-wrap:wrap}
/* 상세 */
.hero{background:var(--bg);overflow:hidden}.hero .in{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center;padding-top:96px}
.hero h1{font-size:clamp(40px,6vw,72px);line-height:1.13;letter-spacing:-.045em;margin:26px 0 20px;font-weight:800}.hero p{font-size:clamp(17px,1.9vw,21px);color:#4e5968;line-height:1.65;margin:0 0 34px}.hero .copy{padding-bottom:110px}
.hero .stage{position:relative;height:640px}.hero .stage .phone:first-child{--w:280px;position:absolute;left:4%;top:120px;transform:rotate(-6deg)}.hero .stage .phone:last-child{--w:300px;position:absolute;right:2%;top:40px}
.stats{padding:72px 0;border-bottom:1px solid #f2f4f6}.stats .in{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;text-align:center}.stats b{display:block;font-size:clamp(40px,5vw,60px);letter-spacing:-.04em;color:var(--c);font-weight:800}.stats span{font-size:16px;color:#4e5968}
.scene{padding:130px 0}.scene .in{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center}.scene.rev .txt{order:2}.scene .vis{display:flex;justify-content:center}
.scene .k{display:inline-block;font-size:15px;font-weight:700;color:var(--c);background:var(--bg);padding:7px 14px;border-radius:999px;margin-bottom:22px}
.scene h3{font-size:clamp(32px,4.2vw,52px);line-height:1.2;letter-spacing:-.04em;margin:0 0 22px;font-weight:800}.scene p{font-size:19px;line-height:1.7;color:#4e5968;margin:0;max-width:440px}
.scene.alt{background:#f9fafb}
.why{padding:120px 0}.why h2{font-size:clamp(30px,4vw,44px);letter-spacing:-.04em;margin:0 0 40px;font-weight:800;text-align:center}.why .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.why .card{background:var(--bg);border-radius:28px;padding:34px 30px}.why .n{font-size:15px;font-weight:800;color:var(--c)}.why h4{font-size:22px;letter-spacing:-.03em;margin:14px 0 10px}.why .card p{font-size:16px;color:#4e5968;line-height:1.6;margin:0}
.end{padding:120px 0 130px;text-align:center;background:var(--bg)}.end img.icon{width:96px;height:96px;border-radius:24px;margin:0 auto 26px;box-shadow:0 10px 30px rgba(0,0,0,.14)}.end h2{font-size:clamp(30px,4.2vw,48px);letter-spacing:-.04em;margin:0 0 34px;font-weight:800}.end .btns{justify-content:center}
.end small{display:block;margin-top:22px;font-size:14px;color:#8b95a1}.end small a{text-decoration:underline}
footer{padding:44px 0 60px;color:#8b95a1;font-size:14px}footer .in{display:flex;gap:20px;flex-wrap:wrap;justify-content:space-between}footer .links{display:flex;gap:18px}
.r{opacity:0;transform:translateY(36px);transition:opacity .9s cubic-bezier(.2,.7,.2,1),transform .9s cubic-bezier(.2,.7,.2,1)}.r.on{opacity:1;transform:none}.d1{transition-delay:.12s}.d2{transition-delay:.24s}
@media(prefers-reduced-motion:reduce){.r{opacity:1;transform:none;transition:none}}
@media(max-width:600px){nav .links{display:none}}
@media(max-width:860px){.tile{margin:0 12px 16px;border-radius:28px}.tile .in,.hero .in,.scene .in{grid-template-columns:1fr;gap:36px}.scene.rev .txt{order:0}
.tile .in{padding-top:56px}.tile .copy{padding-bottom:10px}.tile .stage{height:430px}.tile .stage .phone{--w:190px}.tile .stage .phone:last-child{--w:205px}
.hero .in{padding-top:64px}.hero .copy{padding-bottom:0}.hero .stage{height:520px}.hero .stage .phone:first-child{--w:210px;left:2%;top:90px}.hero .stage .phone:last-child{--w:230px;right:0;top:20px}
.scene{padding:84px 0}.scene .phone{--w:250px}.why .grid,.stats .in{grid-template-columns:1fr}.shero{padding:84px 0 60px}}"""
open(f"{OUT}/style.css", "w").write(CSS)
open(f"{OUT}/app.js", "w").write("document.addEventListener('DOMContentLoaded',()=>{const o=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('on');o.unobserve(x.target)}}),{threshold:.12});document.querySelectorAll('.r').forEach(n=>o.observe(n))})")

def phone(src, alt, cls=""): return f'<div class="phone {cls}"><img src="{src}" alt="{e(alt)}" loading="lazy"></div>'
def store_btn(a, cls="main"): return f'<a class="btn {cls}" href="{e(a["store"])}">{e(C["BTN_STORE"])}</a>' if a["released"] else f'<span class="soon">{e(C["SOON"])}</span>'
def page(title, desc, path, body, extra="", style=""):
    nav = "".join(f'<a href="/{a["slug"]}/">{e(a["ko_name"])}</a>' for a in apps)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Importants Studio"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}">
<link rel="stylesheet" href="/style.css"><script src="/app.js" defer></script>{extra}</head><body{style}>
<nav><div class="in"><a href="/"><b>Importants Studio</b></a><div class="links">{nav}</div></div></nav>
{body}
<footer><div class="in"><span>© {datetime.date.today().year} Importants Studio</span><div class="links"><a href="/">{e(C['LINK_ALL'])}</a><a href="mailto:{MAIL}">{e(C['LINK_CONTACT'])}</a></div></div></footer></body></html>"""

# 메인
tiles = []
for a in apps:
    m = a["m"]; s0 = m["scenes"][0]["screen"]
    tiles.append(f"""<section class="tile" style="--c:{a['color']};--bg:{a['bg']}"><div class="in">
<div class="copy r"><a class="chip" href="/{a['slug']}/"><img src="/{a['slug']}/icon.png" alt="">{e(a['ko_name'])}</a><h2>{br(m['hero_title'])}</h2><p>{e(m['hero_sub'])}</p>
<div class="btns"><a class="btn main" href="/{a['slug']}/">{e(C['BTN_MORE'])}</a>{store_btn(a, 'ghost')}</div></div>
<div class="stage r d1">{"".join(phone(f"/{a['slug']}/{a['shots'][h]}", a['ko_name']) for h in a['hero'])}</div></div></section>""")
open(f"{OUT}/index.html", "w").write(page("Importants Studio", C["STUDIO_SUB"], "/",
    f'<header class="shero"><div class="in r"><h1>{br(C["STUDIO_HEADLINE"])}</h1><p>{e(C["STUDIO_SUB"])}</p></div></header>' + "".join(tiles),
    f'\n<meta property="og:image" content="{BASE}/{apps[0]["slug"]}/icon.png">'))

# 상세
for a in apps:
    m = a["m"]; name = a["ko_name"]
    title = f"{name} - {m['hero_title'].replace(' / ', ' ')}"
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": name, "operatingSystem": "iOS", "applicationCategory": a["cat"],
          "description": m["hero_sub"], "image": f"{BASE}/{a['slug']}/icon.png", "url": f"{BASE}/{a['slug']}/", "author": {"@type": "Organization", "name": "Importants Studio"}}
    if a["released"]: ld.update({"downloadUrl": a["store"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}})
    extra = f'\n<meta property="og:image" content="{BASE}/{a["slug"]}/icon.png"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    if a["released"]: extra += f'\n<meta name="apple-itunes-app" content="app-id={a["id"]}">'
    s0 = m["scenes"][0]["screen"]
    hero = f"""<section class="hero"><div class="in"><div class="copy r"><span class="chip"><img src="icon.png" alt="">{e(name)}</span><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p><div class="btns">{store_btn(a)}</div></div>
<div class="stage r d1">{"".join(phone(a['shots'][h], name) for h in a['hero'])}</div></div></section>"""
    stats = '<section class="stats"><div class="in">' + "".join(f'<div class="r d{i}"><b>{e(n)}</b><span>{e(l)}</span></div>' for i, (n, l) in enumerate(m["stats"])) + "</div></section>"
    scenes = "".join(f"""<section class="scene{' rev' if i % 2 else ''}{' alt' if i % 2 else ''}"><div class="in"><div class="txt r"><span class="k">{e(s.get('kicker',''))}</span><h3>{br(s['title'])}</h3><p>{e(s['body'])}</p></div>
<div class="vis r d1">{phone(a['shots'][s['screen']], name + ' ' + s.get('kicker',''))}</div></div></section>""" for i, s in enumerate(m["scenes"]))
    why = '<section class="why"><div class="in"><h2 class="r">' + e(name) + '</h2><div class="grid">' + "".join(f'<div class="card r d{i}"><div class="n">{i+1:02d}</div><h4>{e(w["title"])}</h4><p>{e(w["body"])}</p></div>' for i, w in enumerate(m["why"])) + "</div></div></section>"
    end = f"""<section class="end"><div class="in r"><img class="icon" src="icon.png" alt=""><h2>{e(m['cta'])}</h2><div class="btns">{store_btn(a)}</div><small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></div></section>"""
    open(f"{OUT}/{a['slug']}/index.html", "w").write(page(title, m["hero_sub"], f"/{a['slug']}/", hero + stats + scenes + why + end, extra, f' style="--c:{a["color"]};--bg:{a["bg"]}"'))

today = datetime.date.today().isoformat()
open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>" for p in ["/"] + [f"/{a['slug']}/" for a in apps]) + "</urlset>\n")
open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(f"{OUT}/CNAME", "w").write("apps.importants-studio.com\n"); open(f"{OUT}/.nojekyll", "w").write("")
print("built", [a["slug"] for a in apps])
