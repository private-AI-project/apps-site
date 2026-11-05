#!/usr/bin/env python3
"""apps.importants-studio.com — 앱마다 성격에 맞춘 다른 레이아웃.
- 뽑기 한입: 놀이형(직접 돌리는 돌림판, 게임 이름 띠, 벤토 카드)
- 퀴즈 한입: 여정형(직접 푸는 문제, 스크롤 따라 그려지는 지도 길)
- 오피스킷: 도구형(줄어드는 용량 숫자·막대, 도구 8가지 벤토)
- 맺음: 에디토리얼형(명조, 여백, 시기별 타임라인, 움직임 최소)
문구: tools/marketing.json·site_copy.json(로컬 LLM 생성), 데모 데이터는 각 앱 원본(quiz_demo·lucky_games·office_tools).
실행: python3 tools/build.py → docs/"""
import json, os, html, shutil, urllib.request, datetime
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
BASE = "https://apps.importants-studio.com"; MAIL = "contact@importants-studio.com"
L = lambda f: json.load(open(f"tools/{f}"))
C, M, APPS = L("site_copy.json"), L("marketing.json"), L("apps.json")
QUIZ, GAMES, TOOLS = L("quiz_demo.json"), L("lucky_games.json"), L("office_tools.json")
OUT = "docs"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
e = lambda s: html.escape(str(s or ""), quote=True)
br = lambda s: "<br>".join(e(x.strip()) for x in (s or "").split("/"))
YEAR = datetime.date.today().year

def save(src, dst, width, fmt="WEBP"):
    im = Image.open(src); im = im.convert("RGBA" if fmt == "PNG" else "RGB")
    if im.width > width: im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    (im.save(dst, fmt, quality=88, method=6) if fmt == "WEBP" else im.save(dst, fmt)); return os.path.basename(dst)

apps = []
for a in APPS:
    d = os.path.join(OUT, a["slug"]); os.makedirs(d)
    if a["released"]:
        r = json.load(urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={a['id']}&country=kr"))["results"][0]
        tmp = os.path.join(d, "_i")
        with urllib.request.urlopen(r["artworkUrl512"].replace("512x512bb", "1024x1024bb"), timeout=60) as f: open(tmp, "wb").write(f.read())
        save(tmp, f"{d}/icon.png", 512, "PNG"); os.remove(tmp); store = r["trackViewUrl"].split("?")[0]
    else:
        save(a["icon"], f"{d}/icon.png", 512, "PNG"); store = f"https://apps.apple.com/kr/app/id{a['id']}"
    m = M[a["slug"]]
    need = set(x["screen"] for x in m["scenes"]) | set(a["hero"]) | set(a.get("extra_shots", []))
    shots = {s: save(os.path.join(a["raw_dir"], s + ".png"), f"{d}/{s}.webp", 1600 if Image.open(os.path.join(a["raw_dir"], s + ".png")).width > Image.open(os.path.join(a["raw_dir"], s + ".png")).height else 900) for s in need}
    apps.append({**a, "m": m, "store": store, "shots": shots})
A = {a["slug"]: a for a in apps}

def phone(src, alt="", cls="", style=""): return f'<div class="phone {cls}" style="{style}"><img src="{src}" alt="{e(alt)}" loading="lazy"></div>'
def land(src, alt="", cls=""): return f'<div class="phone land {cls}"><img src="{src}" alt="{e(alt)}" loading="lazy"></div>'
def store_btn(a, cls="main"): return f'<a class="btn {cls}" href="{e(a["store"])}">{e(C["BTN_STORE"])}</a>' if a["released"] else f'<span class="btn soon">{e(C["SOON"])}</span>'

BASE_CSS = """*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-x:hidden}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%}.in{max-width:1200px;margin:0 auto;padding:0 clamp(20px,5vw,56px)}
nav{position:sticky;top:0;z-index:30;backdrop-filter:saturate(180%) blur(18px);-webkit-backdrop-filter:saturate(180%) blur(18px)}
nav .in{display:flex;align-items:center;justify-content:space-between;height:62px}nav b{font-size:17px;letter-spacing:-.02em}nav .links{display:flex;gap:24px;font-size:15px;opacity:.75}
.phone{position:relative;width:var(--w,280px);height:auto!important;align-self:flex-start;justify-self:center;aspect-ratio:1320/2868;border-radius:calc(var(--w,280px)*.16);background:#0b0b0d;padding:calc(var(--w,280px)*.034);box-shadow:0 30px 80px rgba(17,24,39,.22),0 8px 20px rgba(17,24,39,.10);flex:none}
.phone img{width:100%;height:100%;object-fit:cover;border-radius:calc(var(--w,280px)*.13)}.phone.land{aspect-ratio:2868/1320;border-radius:calc(var(--w,280px)*.075);padding:calc(var(--w,280px)*.016)}.phone.land img{border-radius:calc(var(--w,280px)*.06)}.phone:before{content:"";position:absolute;inset:0;border-radius:inherit;box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.14);pointer-events:none}.fade{-webkit-mask-image:linear-gradient(#000 70%,transparent);mask-image:linear-gradient(#000 70%,transparent)}
.btn{display:inline-flex;align-items:center;justify-content:center;height:56px;padding:0 26px;border-radius:16px;font-weight:700;font-size:17px;transition:transform .15s;cursor:pointer;border:0;font-family:inherit}.btn:active{transform:scale(.96)}
.btn.soon{background:rgba(0,0,0,.07);color:#6b7684;cursor:default}
footer{padding:44px 0 60px;font-size:14px;opacity:.6}footer .in{display:flex;gap:20px;flex-wrap:wrap;justify-content:space-between}footer .links{display:flex;gap:18px}
.r{opacity:0;transform:translateY(36px);transition:opacity .9s cubic-bezier(.2,.7,.2,1),transform .9s cubic-bezier(.2,.7,.2,1)}.r.on{opacity:1;transform:none}.d1{transition-delay:.12s}.d2{transition-delay:.24s}.d3{transition-delay:.36s}
@media(prefers-reduced-motion:reduce){.r{opacity:1;transform:none;transition:none}*{animation:none!important}}
@media(max-width:640px){nav .links{display:none}}@media(min-width:1700px){body{zoom:1.15}}@media(min-width:1950px){body{zoom:1.3}}@media(min-width:2250px){body{zoom:1.5}}@media(min-width:2800px){body{zoom:1.75}}"""
REVEAL_JS = "const o=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('on');o.unobserve(x.target)}}),{threshold:.12});document.querySelectorAll('.r').forEach(n=>o.observe(n));"
PRETENDARD = "@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');"

def page(path, title, desc, css, body, js="", extra="", navcls=""):
    navlinks = "".join(f'<a href="/{a["slug"]}/">{e(a["ko_name"])}</a>' for a in apps)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Importants Studio"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}">{extra}
<style>{BASE_CSS}{css}</style></head><body>
<nav class="{navcls}"><div class="in"><a href="/"><b>Importants Studio</b></a><div class="links">{navlinks}</div></div></nav>
{body}
<footer><div class="in"><span>© {YEAR} Importants Studio</span><div class="links"><a href="/">{e(C['LINK_ALL'])}</a><a href="mailto:{MAIL}">{e(C['LINK_CONTACT'])}</a></div></div></footer>
<script>document.addEventListener('DOMContentLoaded',()=>{{{REVEAL_JS}{js}}})</script></body></html>"""

def app_meta(a):
    m = a["m"]; cat = {"lucky-bite": "EntertainmentApplication", "quiz-bite": "GameApplication", "officekit": "UtilitiesApplication", "maejeum": "LifestyleApplication", "reckoner": "SportsApplication", "floorlog": "UtilitiesApplication"}[a["slug"]]
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": a["ko_name"], "operatingSystem": "iOS", "applicationCategory": cat,
          "description": m["hero_sub"], "image": f"{BASE}/{a['slug']}/icon.png", "url": f"{BASE}/{a['slug']}/", "author": {"@type": "Organization", "name": "Importants Studio"}}
    if a["released"]: ld.update({"downloadUrl": a["store"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}})
    x = f'\n<meta property="og:image" content="{BASE}/{a["slug"]}/icon.png"><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    if a["released"]: x += f'\n<meta name="apple-itunes-app" content="app-id={a["id"]}">'
    return x
def write(a, css, body, js="", navcls=""):
    m = a["m"]; title = f"{a['ko_name']} - {m['hero_title'].replace(' / ', ' ')}"
    open(f"{OUT}/{a['slug']}/index.html", "w").write(page(f"/{a['slug']}/", title, m["hero_sub"], css, body, js, app_meta(a), navcls))

# ───────────────────────── 뽑기 한입: 놀이형 ─────────────────────────
a = A["lucky-bite"]; m = a["m"]; S = a["shots"]; sc = {x["screen"]: x for x in m["scenes"]}
NAMES = ["민준", "서연", "도윤", "하은", "지호", "유나"]  # 데모용 가상 이름
SEG = ["#FF7A3D", "#4F7CFF", "#2BC48A", "#FFC233", "#B26BFF", "#FF5C8A"]
wheel = "".join(f'<path d="M100 100 L{100+95*__import__("math").cos(__import__("math").radians(i*60-90)):.2f} {100+95*__import__("math").sin(__import__("math").radians(i*60-90)):.2f} A95 95 0 0 1 {100+95*__import__("math").cos(__import__("math").radians((i+1)*60-90)):.2f} {100+95*__import__("math").sin(__import__("math").radians((i+1)*60-90)):.2f} Z" fill="{SEG[i]}"/>'
                f'<text x="{100+60*__import__("math").cos(__import__("math").radians(i*60-60)):.1f}" y="{100+60*__import__("math").sin(__import__("math").radians(i*60-60)):.1f}" fill="#fff" font-size="15" font-weight="800" text-anchor="middle" dominant-baseline="middle" transform="rotate({i*60+30} {100+60*__import__("math").cos(__import__("math").radians(i*60-60)):.1f} {100+60*__import__("math").sin(__import__("math").radians(i*60-60)):.1f})">{n}</text>' for i, n in enumerate(NAMES))
row1 = "".join(f"<span>{e(g)}</span>" for g in GAMES[:13]) * 2; row2 = "".join(f"<span>{e(g)}</span>" for g in GAMES[12:]) * 2
stickers = "".join(f'<span class="st s{i}">{e(g)}</span>' for i, g in enumerate(["돌림판", "사다리타기", "경마 레이스", "폭탄 돌리기", "AI 법정"]))
bento = f"""<div class="bento">
<div class="cell big r" style="background:#FFE7D6"><div class="t"><span class="k">{e(sc['race']['kicker'])}</span><h3>{br(sc['race']['title'])}</h3><p>{e(sc['race']['body'])}</p></div>{phone(S['race'],'경마 레이스','tilt-r')}</div>
<div class="cell tall r d1" style="background:#E6EEFF"><div class="t"><span class="k">{e(sc['court']['kicker'])}</span><h3>{br(sc['court']['title'])}</h3><p>{e(sc['court']['body'])}</p></div>{phone(S['court'],'AI 법정','sm')}</div>
<div class="cell wide r" style="background:#E3F7EE"><div class="t"><span class="k">{e(sc['seats']['kicker'])}</span><h3>{br(sc['seats']['title'])}</h3><p>{e(sc['seats']['body'])}</p></div>{phone(S['seats'],'자리 배치','sm tilt-l')}</div>
<div class="cell r d1" style="background:#FFF3C9"><div class="t"><span class="k">{e(sc['home']['kicker'])}</span><h3>{br(sc['home']['title'])}</h3><p>{e(sc['home']['body'])}</p></div></div>
</div>"""
css = PRETENDARD + """body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#FFF8F1;color:#2A1A10}nav{background:rgba(255,248,241,.85)}
.hero{position:relative;padding:clamp(40px,6vh,80px) 0 24px;overflow:hidden}.hero .in{display:grid;grid-template-columns:1.1fr .9fr;align-items:center;gap:20px}
.hero h1{font-size:clamp(44px,5.8vw,80px);line-height:1.08;letter-spacing:-.045em;font-weight:900;margin:24px 0 20px}.hero p{font-size:clamp(17px,1.4vw,20px);line-height:1.6;opacity:.75;margin:0 0 34px;max-width:440px}
.chip{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:16px;line-height:1;background:#fff;padding:6px 16px 6px 6px;border-radius:16px;box-shadow:0 6px 18px rgba(255,122,61,.14)}.chip img{width:36px;height:36px;border-radius:10px}
.btn.main{background:#FF7A3D;color:#fff;box-shadow:0 10px 24px rgba(255,122,61,.35)}
.stage{position:relative;height:clamp(520px,78vh,640px)}.stage .phone{position:absolute}.stage .p1{--w:clamp(220px,min(21vw,33vh),270px);left:4%;top:12%;transform:rotate(-8deg)}.stage .p2{--w:clamp(236px,min(22vw,35vh),288px);right:4%;top:2%;transform:rotate(6deg)}
.st{position:absolute;z-index:3;font-weight:800;font-size:16px;padding:10px 16px;border-radius:999px;background:#fff;box-shadow:0 8px 20px rgba(0,0,0,.10);animation:bob 4s ease-in-out infinite}
.s0{left:40%;top:4%;background:#FF7A3D;color:#fff}.s1{left:50%;top:80%;animation-delay:.6s}.s2{right:0;top:90%;background:#2BC48A;color:#fff;animation-delay:1.2s}.s3{left:0;top:84%;background:#4F7CFF;color:#fff;animation-delay:1.8s}.s4{right:0;top:16%;background:#B26BFF;color:#fff;animation-delay:2.4s}
@keyframes bob{0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-10px) rotate(3deg)}}
.stats{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;padding-top:40px;padding-bottom:90px}.stats div{background:#fff;border-radius:28px;padding:22px 30px;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,.05)}.stats b{display:block;font-size:46px;font-weight:900;color:#FF7A3D;letter-spacing:-.04em}.stats span{font-size:15px;opacity:.7}
.hstats{display:flex;gap:clamp(20px,3vw,40px);margin-top:clamp(32px,5vh,52px);padding-top:24px;border-top:1px solid rgba(42,26,16,.12)}.hstats b{display:block;font-size:clamp(28px,2.6vw,38px);font-weight:900;color:#FF7A3D;letter-spacing:-.04em;line-height:1.1}.hstats span{font-size:14px;opacity:.65}.how{padding:clamp(80px,10vw,130px) 0 0;background:#2A1A10;color:#fff;margin-top:clamp(40px,6vw,80px);overflow:hidden}.how h2{text-align:center;font-size:clamp(32px,4vw,52px);font-weight:900;letter-spacing:-.045em;margin:0 0 clamp(48px,6vw,72px)}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(20px,3vw,40px)}.step{display:flex;flex-direction:column}.step .shot{background:#3A2618;border-radius:32px;padding:36px 0 0;height:clamp(380px,34vw,460px);overflow:hidden;display:flex;justify-content:center;margin-bottom:28px}.step .phone{--w:clamp(190px,17vw,236px);box-shadow:0 20px 50px rgba(0,0,0,.45)}.step .no{display:inline-flex;width:34px;height:34px;border-radius:17px;background:#FF7A3D;font-weight:900;align-items:center;justify-content:center;font-size:16px}.step h3{font-size:clamp(22px,2vw,26px);font-weight:900;letter-spacing:-.035em;margin:14px 0 8px}.step p{margin:0 0 clamp(80px,10vw,130px);font-size:16px;line-height:1.65;opacity:.72}.demo .in{display:grid;grid-template-columns:1fr 1fr;gap:clamp(40px,6vw,96px);align-items:center}.demo h2{font-size:clamp(34px,4.2vw,56px);line-height:1.15;font-weight:900;letter-spacing:-.045em;margin:0}.demo .side{display:flex;flex-direction:column;align-items:flex-start}
.wheel{position:relative;width:min(440px,84vw,62vh);margin:0 auto}.wheel svg{width:100%;display:block;transition:transform 4.2s cubic-bezier(.12,.75,.12,1);filter:drop-shadow(0 20px 40px rgba(0,0,0,.4))}
.wheel:after{content:"";position:absolute;left:50%;top:-14px;transform:translateX(-50%);border:16px solid transparent;border-top:28px solid #fff}
.demo .btn{margin-top:40px;background:#FF7A3D;color:#fff;height:62px;padding:0 44px;font-size:19px}.res{height:56px;margin-top:24px;font-size:clamp(26px,2.6vw,34px);color:#FFB48A;font-weight:900;opacity:0;transform:scale(.6);transition:all .4s cubic-bezier(.3,1.6,.5,1)}.res.on{opacity:1;transform:none}
.marq{padding:90px 0 20px;overflow:hidden}.marq h2{text-align:center;font-size:clamp(30px,4.4vw,52px);font-weight:900;letter-spacing:-.045em;margin:0 0 40px}
.row{display:flex;gap:12px;width:max-content;animation:mq 40s linear infinite;margin-bottom:12px}.row.rev{animation-direction:reverse}.row span{font-size:20px;font-weight:800;padding:16px 26px;border-radius:999px;background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.06);white-space:nowrap}
.row span:nth-child(4n+1){background:#FF7A3D;color:#fff}.row span:nth-child(4n+3){background:#FFE07A}@keyframes mq{to{transform:translateX(-50%)}}
.bento{display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:300px;gap:20px;padding:clamp(56px,7vw,96px) 0 clamp(80px,10vw,140px)}.cell{border-radius:36px;padding:34px;position:relative;overflow:hidden}
.cell .t{position:relative;z-index:2;max-width:330px}.cell .k{font-weight:800;color:#FF7A3D;font-size:15px}.cell h3{font-size:30px;line-height:1.22;letter-spacing:-.04em;margin:10px 0 12px;font-weight:900}.cell p{margin:0;font-size:16px;opacity:.75;line-height:1.6}
.cell .phone{position:absolute;right:30px;bottom:-200px;--w:240px}.cell .phone.sm{--w:200px;bottom:-160px}.tilt-r{transform:rotate(8deg)}.tilt-l{transform:rotate(-7deg)}
.big{grid-column:span 2;grid-row:span 2}.big .phone{--w:300px;right:60px;bottom:-120px}.tall{grid-row:span 2}.tall .phone{right:50%;margin-right:-100px;bottom:-60px}.wide{grid-column:span 2}.wide .phone{bottom:-260px}
.end{background:#FF7A3D;color:#fff;text-align:center;padding:clamp(72px,9vw,120px) 24px;border-radius:clamp(32px,4vw,48px);margin:0 auto 30px;max-width:1088px;width:calc(100% - 2*clamp(20px,5vw,56px))}.end img{width:100px;height:100px;border-radius:26px;margin:0 auto 26px;box-shadow:0 14px 30px rgba(0,0,0,.2)}
.end h2{font-size:clamp(32px,5vw,58px);font-weight:900;letter-spacing:-.045em;margin:0 0 34px}.end .btn.main{background:#fff;color:#FF7A3D;box-shadow:none}.end small{display:block;margin-top:20px;opacity:.8}.end small a{text-decoration:underline}
@media(max-width:900px){.hero .in,.steps{grid-template-columns:1fr}.step p{margin-bottom:48px}.step:last-child p{margin-bottom:80px}.step .shot{height:400px}.stage{height:520px}.stage .p1{--w:210px}.stage .p2{--w:230px}.st{font-size:14px}.bento{grid-template-columns:1fr;grid-auto-rows:auto}.big,.wide,.tall{grid-column:auto;grid-row:auto}.cell{padding:30px 26px 0;display:flex;flex-direction:column}.cell:last-child{padding-bottom:30px}.cell h3{font-size:26px}.cell .phone,.big .phone,.tall .phone,.wide .phone,.cell .phone.sm{position:relative;right:auto;bottom:auto;margin:28px auto -170px;--w:220px}.stage .p1{left:2%}.stage .p2{right:2%}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.stats div{padding:18px 8px;border-radius:22px}.stats b{font-size:34px}.stats span{font-size:13px}}"""
body = f"""<header class="hero"><div class="in"><div class="r"><span class="chip"><img src="icon.png" alt="">{e(a['ko_name'])}</span><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p>{store_btn(a)}<div class="hstats">{''.join(f'<div><b>{e(n)}</b><span>{e(l)}</span></div>' for n,l in m['stats'])}</div></div>
<div class="stage r d1">{stickers}{phone(S['roulette'],'돌림판','p1')}{phone(S['ladder'],'사다리타기','p2')}</div></div></header>
<section class="how"><div class="in"><h2 class="r">{e(C['LB_HOW_T'])}</h2><div class="steps">{''.join(f'<div class="step r d{k}"><div class="shot">{phone(S[sh], C[f"LB_H{k+1}"])}</div><span class="no">{k+1}</span><h3>{e(C[f"LB_H{k+1}"])}</h3><p>{e(C[f"LB_H{k+1}_B"])}</p></div>' for k, sh in enumerate(["home", "draw", "records"]))}</div></div></section>
<section class="marq"><h2 class="r">{e(C['LB_GAMES_T'])}</h2><div class="row">{row1}</div><div class="row rev">{row2}</div></section>
<div class="in">{bento}</div>
<section class="end r"><img src="icon.png" alt=""><h2>{e(C['LB_CTA'])}</h2>{store_btn(a)}<small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></section>"""
js = ""
write(a, css, body, js)

# ───────────────────────── 퀴즈 한입: 여정형 ─────────────────────────
a = A["quiz-bite"]; m = a["m"]; S = a["shots"]
css = PRETENDARD + """body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#F4F7FF;color:#1B2440}nav{background:rgba(244,247,255,.85)}
.hero{padding:clamp(40px,6vh,80px) 0 clamp(56px,8vw,96px)}.hero .in{display:grid;grid-template-columns:1.05fr .95fr;gap:40px;align-items:center}.hero h1{font-size:clamp(42px,5.6vw,78px);line-height:1.1;letter-spacing:-.045em;font-weight:850;margin:24px 0 20px}
.hero p{font-size:clamp(17px,1.4vw,20px);line-height:1.6;opacity:.72;margin:0 0 34px;max-width:440px}.chip{display:inline-flex;align-items:center;gap:10px;font-weight:800}.chip img{width:44px;height:44px;border-radius:12px}
.btn.main{background:#4F7CFF;color:#fff;box-shadow:0 12px 26px rgba(79,124,255,.35)}.stage{position:relative;display:flex;justify-content:center}.stage .phone{--w:clamp(240px,min(24vw,36vh),300px)}
.qcard{position:absolute;left:-10px;bottom:70px;background:#fff;border-radius:22px;padding:16px 18px;box-shadow:0 20px 40px rgba(27,36,64,.16);width:240px;font-size:14px;animation:fl 5s ease-in-out infinite}
.qcard b{display:block;font-size:13px;color:#4F7CFF;margin-bottom:6px}@keyframes fl{50%{transform:translateY(-12px)}}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding-top:10px;padding-bottom:100px}.stats div{background:#fff;border-radius:26px;padding:30px;text-align:center}.stats b{display:block;font-size:52px;font-weight:850;color:#4F7CFF;letter-spacing:-.04em}.stats span{opacity:.65}
.play{padding:110px 0;background:#1B2440;color:#fff}.play h2{text-align:center;font-size:clamp(32px,5vw,56px);font-weight:850;letter-spacing:-.045em;margin:0 0 44px}
.qz{max-width:560px;margin:0 auto;background:#fff;color:#1B2440;border-radius:32px;padding:34px;box-shadow:0 30px 60px rgba(0,0,0,.35)}.qz .cat{display:inline-block;font-size:14px;font-weight:800;color:#4F7CFF;background:#EEF3FF;padding:6px 12px;border-radius:999px}
.qz .q{font-size:23px;font-weight:800;line-height:1.45;letter-spacing:-.02em;margin:18px 0 24px;min-height:66px}.qz .ch{display:grid;gap:10px}.qz .ch.two{grid-template-columns:1fr 1fr}
.qz button.o{height:64px;border-radius:18px;border:0;background:#F1F4FA;font-size:20px;font-weight:800;cursor:pointer;font-family:inherit;transition:transform .12s,background .2s}.qz button.o:active{transform:scale(.97)}
.qz button.o.ok{background:#2BC48A;color:#fff}.qz button.o.no{background:#FF6B6B;color:#fff}.qz .ox{font-size:34px}
.qz .ans{margin-top:20px;padding:18px;border-radius:18px;background:#F6F8FD;display:none;line-height:1.6}.qz .ans.on{display:block;animation:pop .35s}.qz .ans b{display:block;margin-bottom:4px;font-size:17px}
.qz .nx{margin-top:18px;width:100%;background:#1B2440;color:#fff;display:none}.qz .nx.on{display:flex}.dots{display:flex;gap:6px;justify-content:center;margin-top:18px}.dots i{width:8px;height:8px;border-radius:4px;background:#D5DCEB}.dots i.on{background:#4F7CFF;width:22px}
@keyframes pop{from{transform:scale(.96);opacity:0}}
.journey{position:relative;padding:120px 0 60px}.journey h2{text-align:center;font-size:clamp(30px,4.6vw,52px);font-weight:850;letter-spacing:-.045em;margin:0 0 80px}
.path{position:absolute;left:50%;top:260px;bottom:80px;width:300px;transform:translateX(-50%);z-index:0}.path svg{width:100%;height:100%}
.stop{position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;gap:70px;align-items:center;margin-bottom:120px}.stop.rev .tx{order:2}.stop .vis{display:flex;justify-content:center}.stop .phone{--w:clamp(220px,min(22vw,38vh),270px)}
.stop .n{display:inline-flex;width:44px;height:44px;border-radius:22px;background:#4F7CFF;color:#fff;font-weight:900;align-items:center;justify-content:center;font-size:18px;box-shadow:0 0 0 8px #DCE6FF}
.stop .k{display:block;margin:20px 0 8px;font-weight:800;color:#4F7CFF}.stop h3{font-size:clamp(28px,3.6vw,42px);line-height:1.22;letter-spacing:-.04em;margin:0 0 14px;font-weight:850}.stop p{font-size:18px;line-height:1.7;opacity:.72;margin:0;max-width:420px}
.end{text-align:center;padding:110px 24px 120px}.end img{width:96px;height:96px;border-radius:26px;margin:0 auto 24px;box-shadow:0 14px 30px rgba(79,124,255,.3)}.end h2{font-size:clamp(30px,4.6vw,52px);font-weight:850;letter-spacing:-.045em;margin:0 0 30px}.end small{display:block;margin-top:20px;opacity:.6}.end small a{text-decoration:underline}
@media(max-width:860px){.hero .in,.stop{grid-template-columns:1fr}.stop.rev .tx{order:0}.qcard{left:0}.stats{gap:10px}.stats div{padding:20px 6px;border-radius:20px}.stats b{font-size:34px}.stats span{font-size:13px}.qz{padding:26px 22px}.qz .q{font-size:20px}.path{display:none}.stop .phone{--w:230px}}"""
stops = "".join(f"""<div class="stop{' rev' if i % 2 else ''}"><div class="tx r"><span class="n">{i+1}</span><span class="k">{e(s['kicker'])}</span><h3>{br(s['title'])}</h3><p>{e(s['body'])}</p></div><div class="vis r d1">{phone(S[s['screen']], s['kicker'])}</div></div>""" for i, s in enumerate(m["scenes"]))
body = f"""<header class="hero"><div class="in"><div class="r"><span class="chip"><img src="icon.png" alt="">{e(a['ko_name'])}</span><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p>{store_btn(a)}</div>
<div class="stage r d1">{phone(S['home'],'퀴즈 목록')}<div class="qcard"><b>{e(QUIZ[1]['cat'])}</b>{e(QUIZ[1]['q'])}</div></div></div></header>
<div class="in stats">{''.join(f'<div class="r d{i}"><b data-n="{e(n)}">{e(n)}</b><span>{e(l)}</span></div>' for i,(n,l) in enumerate(m['stats']))}</div>
<section class="play"><div class="in"><h2 class="r">{e(C['QB_DEMO_T'])}</h2><div class="qz r d1" id="qz"></div></div></section>
<section class="journey"><div class="in"><h2 class="r">{e(C['QB_MAP_T'])}</h2>{stops}</div></section>
<section class="end r"><img src="icon.png" alt=""><h2>{e(m['cta'])}</h2>{store_btn(a)}<small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></section>"""
js = f"""const Q={json.dumps(QUIZ, ensure_ascii=False)},T={json.dumps({k: C[k] for k in ['QB_RIGHT','QB_WRONG','QB_NEXT','QB_SHOW']}, ensure_ascii=False)};let qi=0;const box=document.getElementById('qz');
function esc(s){{return s.replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c])}}
function draw(){{const q=Q[qi];let ch='';if(q.type==='ox')ch='<div class="ch two"><button class="o ox" data-v="1">O</button><button class="o ox" data-v="0">X</button></div>';
else if(q.type==='nonsense')ch='<div class="ch"><button class="o" data-v="show">'+T.QB_SHOW+'</button></div>';else ch='<div class="ch two">'+q.c.map((c,i)=>'<button class="o" data-v="'+i+'">'+esc(c)+'</button>').join('')+'</div>';
box.innerHTML='<span class="cat">'+q.cat+'</span><div class="q">'+esc(q.q)+'</div>'+ch+'<div class="ans"></div><button class="btn nx">'+T.QB_NEXT+'</button><div class="dots">'+Q.map((_,i)=>'<i class="'+(i===qi?'on':'')+'"></i>').join('')+'</div>';
box.querySelectorAll('button.o').forEach(b=>b.onclick=()=>{{if(box.dataset.done)return;box.dataset.done=1;const v=b.dataset.v;let ok=true,ans='';
if(q.type==='ox'){{ok=(v==='1')===q.o;box.querySelector('[data-v="'+(q.o?'1':'0')+'"]').classList.add('ok');ans=q.o?'O':'X'}}else if(q.type==='mcq'){{ok=+v===q.i;box.querySelectorAll('button.o')[q.i].classList.add('ok');ans=q.c[q.i]}}else{{ans=q.a}}
if(!ok)b.classList.add('no');const a=box.querySelector('.ans');a.innerHTML='<b>'+(q.type==='nonsense'?esc(ans):(ok?T.QB_RIGHT:T.QB_WRONG)+' · '+esc(ans))+'</b>'+esc(q.exp);a.classList.add('on');box.querySelector('.nx').classList.add('on')}});
box.querySelector('.nx').onclick=()=>{{qi=(qi+1)%Q.length;delete box.dataset.done;draw()}}}}draw();"""
write(a, css, body, js)

# ───────────────────────── 오피스킷: 도구형 ─────────────────────────
a = A["officekit"]; m = a["m"]; S = a["shots"]; sc = {x["screen"]: x for x in m["scenes"]}
ICON = {"scan": '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3M4 12h16"/>',
        "pdfCompress": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M12 11v7m-3-3 3 3 3-3"/>', "imageCompress": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 16 5-5 4 4 3-3 6 6M12 3v6m-2-2 2 2 2-2"/>',
        "imageConvert": '<path d="M4 7h13l-3-3M20 17H7l3 3"/>', "photoToPDF": '<rect x="3" y="4" width="10" height="10" rx="2"/><path d="M11 10h10v10H11zM15 14h2"/>',
        "pdfMerge": '<path d="M6 3h6v8H6zM12 13h6v8h-6zM9 11v3a2 2 0 0 0 2 2h1"/>', "pdfPages": '<rect x="4" y="3" width="7" height="9" rx="1"/><rect x="13" y="12" width="7" height="9" rx="1"/><path d="M14 6h5m-2-2 2 2-2 2M10 18H5m2 2-2-2 2-2"/>',
        "pdfToImage": '<path d="M7 3h7l5 5v13H7z"/><path d="m9 18 3-3 2 2 2-2 1 1"/>'}
tiles = "".join(f"""<div class="tool r d{i%3}"><svg viewBox="0 0 24 24">{ICON[k]}</svg><b>{e(t)}</b><span>{e(s)}</span></div>""" for i, (k, t, s) in enumerate(TOOLS))
css = PRETENDARD + """body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#fff;color:#0F1424}nav{background:rgba(255,255,255,.85);border-bottom:1px solid #EEF0F4}
.hero{padding:clamp(40px,7vh,88px) 0 0;text-align:center;overflow:hidden}.hero .chip{display:inline-flex;align-items:center;gap:10px;font-weight:700;color:#315DFE}.hero .chip img{width:40px;height:40px;border-radius:10px}
.hero h1{font-size:clamp(40px,5.4vw,76px);line-height:1.1;letter-spacing:-.05em;font-weight:800;margin:22px 0 18px}.hero p{font-size:clamp(17px,1.4vw,20px);line-height:1.6;color:#5B6478;margin:0 auto 30px;max-width:560px}
.btn.main{background:#315DFE;color:#fff}.hero .stage{display:flex;justify-content:center;gap:clamp(16px,2.4vw,32px);margin-top:clamp(0px,2vh,24px);padding-top:48px;height:clamp(408px,calc(46vh + 48px),518px);overflow:hidden}.hero .stage .phone{--w:clamp(230px,22vw,290px)}.hero .stage .phone:first-child{--w:clamp(200px,19vw,250px);margin-top:70px}
.size{padding:clamp(80px,11vw,140px) 0;background:#0F1424;color:#fff}.size .in{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center}.size h2{font-size:clamp(32px,4.6vw,54px);letter-spacing:-.05em;line-height:1.15;margin:0 0 40px;font-weight:800}
.num{font-size:clamp(64px,10vw,124px);font-weight:800;letter-spacing:-.06em;font-variant-numeric:tabular-nums;color:#7EA0FF;line-height:1}.num small{font-size:.4em;color:#9AA4BA;margin-left:6px}
.bars{margin-top:34px;display:grid;gap:14px}.bar{display:grid;grid-template-columns:70px 1fr;gap:14px;align-items:center;font-size:15px;color:#9AA4BA}.bar i{display:block;height:16px;border-radius:8px;background:#2A3350;position:relative;overflow:hidden}
.bar i:after{content:"";position:absolute;inset:0;width:var(--p);background:var(--c);border-radius:8px;transition:width 1.6s cubic-bezier(.2,.7,.2,1)}.size:not(.go) .bar.after i:after{width:100%}
.size .vis{display:flex;gap:24px;justify-content:center;align-items:flex-start}.size .phone{--w:clamp(200px,min(19vw,34vh),250px)}.size .phone:last-child{margin-top:64px}
.tools{padding:clamp(80px,11vw,140px) 0}.tools h2{text-align:center;font-size:clamp(32px,4.6vw,54px);letter-spacing:-.05em;margin:0 0 50px;font-weight:800}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.tool{background:#F5F7FB;border-radius:26px;padding:28px 24px;min-height:190px;display:flex;flex-direction:column;transition:transform .2s,background .2s}.tool:hover{transform:translateY(-4px);background:#EDF1FF}
.tool svg{width:34px;height:34px;fill:none;stroke:#315DFE;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;margin-bottom:auto}.tool b{font-size:19px;letter-spacing:-.02em;margin-top:30px}.tool span{font-size:14px;color:#5B6478;margin-top:6px}
.tool:first-child{grid-column:span 2;grid-row:span 2;background:#315DFE;color:#fff}.tool:last-child{grid-column:span 2}.tool:first-child svg{stroke:#fff;width:52px;height:52px}.tool:first-child b{font-size:30px}.tool:first-child span{color:#C9D5FF;font-size:17px}
.feat{padding:clamp(72px,10vw,120px) 0;border-top:1px solid #EEF0F4}.feat .in{display:grid;grid-template-columns:1fr 1fr;gap:70px;align-items:center}.feat.rev .tx{order:2}.feat .vis{display:flex;justify-content:center}.feat .phone{--w:clamp(220px,min(22vw,38vh),280px)}
.feat .k{color:#315DFE;font-weight:700}.feat h3{font-size:clamp(30px,4vw,48px);letter-spacing:-.05em;line-height:1.18;margin:14px 0 18px;font-weight:800}.feat p{font-size:18px;color:#5B6478;line-height:1.7;margin:0;max-width:430px}
.end{padding:120px 24px;text-align:center;background:#F5F7FB}.end img{width:96px;height:96px;border-radius:24px;margin:0 auto 24px}.end h2{font-size:clamp(30px,4.6vw,52px);letter-spacing:-.05em;margin:0 0 30px;font-weight:800}.end small{display:block;margin-top:20px;color:#8A93A6}.end small a{text-decoration:underline}
@media(max-width:900px){.size .in,.feat .in{grid-template-columns:1fr}.feat.rev .tx{order:0}.size .in,.feat .in{grid-template-columns:minmax(0,1fr)}.grid{grid-template-columns:1fr 1fr;gap:10px}.tool{min-height:160px;padding:22px 18px}.tool:first-child,.tool:last-child{grid-column:span 2;grid-row:auto}.tool:first-child{min-height:200px}.hero .stage{height:340px;gap:14px;margin-top:50px}.hero .stage .phone{--w:175px}.hero .stage .phone:first-child{--w:150px;margin-top:60px}.size .vis{gap:14px}.size .phone{--w:150px}.size .phone:last-child{margin-top:40px}.bar{grid-template-columns:60px minmax(0,1fr)}}"""
feats = "".join(f"""<section class="feat{' rev' if i % 2 else ''}"><div class="in"><div class="tx r"><span class="k">{e(sc[k]['kicker'])}</span><h3>{br(sc[k]['title'])}</h3><p>{e(sc[k]['body'])}</p></div><div class="vis r d1">{phone(S[k], sc[k]['kicker'])}</div></div></section>""" for i, k in enumerate(["scan", "redact"]))
body = f"""<header class="hero"><div class="in r"><span class="chip"><img src="icon.png" alt="">{e(a['ko_name'])}</span><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p>{store_btn(a)}</div>
<div class="stage fade r d1">{phone(S['library'],'보관함')}{phone(S['home'],'홈')}</div></header>
<section class="size" id="size"><div class="in"><div class="r"><h2>{e(C['OK_COMPARE_T'])}</h2><div class="num"><span id="kb">3,200</span><small>KB</small></div>
<div class="bars"><div class="bar"><span>{e(C['OK_BEFORE'])}</span><i style="--p:100%;--c:#5B6478"></i></div><div class="bar after"><span>{e(C['OK_AFTER'])}</span><i style="--p:15%;--c:#7EA0FF"></i></div></div></div>
<div class="vis r d1">{phone(S['compress'],'용량 줄이기 결과')}{phone(S['compare'],'화질 비교')}</div></div></section>
<section class="tools"><div class="in"><h2 class="r">{e(C['OK_TOOLS_T'])}</h2><div class="grid">{tiles}</div></div></section>
{feats}
<section class="end r"><img src="icon.png" alt=""><h2>{e(m['cta'])}</h2>{store_btn(a)}<small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></section>"""
js = """const sz=document.getElementById('size'),kb=document.getElementById('kb');new IntersectionObserver((es,ob)=>{if(!es[0].isIntersecting)return;ob.disconnect();sz.classList.add('go');const t0=performance.now();
const f=t=>{const p=Math.min(1,(t-t0)/1600),v=Math.round(3200-(3200-480)*(1-Math.pow(1-p,3)));kb.textContent=v.toLocaleString();if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)},{threshold:.4}).observe(sz);"""
write(a, css, body, js)

# ───────────────────────── 맺음: 에디토리얼형 ─────────────────────────
a = A["maejeum"]; m = a["m"]; S = a["shots"]
steps = [("MJ_S1", "web"), ("MJ_S2", "money"), ("MJ_S3", "settle"), ("MJ_S4", None), ("MJ_S5", "tasks"), ("MJ_S6", None)]
tl = "".join(f"""<li class="r"><div class="when">{e(C[k])}</div><div class="what"><p>{e(C[k + '_B'])}</p>{phone(S[s], C[k]) if s else ''}</div></li>""" for k, s in steps)
css = """@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap');""" + PRETENDARD + """
body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#F7F5F0;color:#2B2B2D}nav{background:rgba(247,245,240,.88)}.serif{font-family:"Nanum Myeongjo",serif}
.r{transform:translateY(14px);transition-duration:1.3s}
.hero{padding:clamp(40px,7vh,96px) 0 0;text-align:center;overflow:hidden}.hero img.knot{width:72px;height:72px;border-radius:18px;margin:0 auto 26px}.hero .eyebrow{letter-spacing:.3em;font-size:13px;color:#4A5C52}
.hero h1{font-family:"Nanum Myeongjo",serif;font-weight:800;font-size:clamp(36px,4.8vw,64px);line-height:1.32;letter-spacing:-.02em;margin:20px 0 20px}.hero p{font-size:clamp(16px,1.3vw,19px);line-height:1.7;color:#6E6A63;margin:0 auto 32px;max-width:520px}
.btn.main{background:#4A5C52;color:#fff}.hero .rule{width:1px;height:48px;background:#BDB6A8;margin:44px auto 0}
.hero .stage{display:flex;justify-content:center;gap:clamp(16px,2.6vw,36px);margin-top:0;padding-top:40px;height:clamp(380px,calc(44vh + 40px),500px);overflow:hidden}.hero .stage .phone{--w:clamp(210px,20vw,262px);box-shadow:0 24px 60px rgba(60,55,45,.18)}.hero .stage .phone:first-child{margin-top:56px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);margin-top:0;border-top:1px solid #DDD7CB;border-bottom:1px solid #DDD7CB}.stats div{padding:clamp(36px,4vw,52px) 20px;text-align:center}.stats div+div{border-left:1px solid #DDD7CB}
.stats b{display:block;font-family:"Nanum Myeongjo",serif;font-weight:800;font-size:clamp(40px,5vw,58px);color:#4A5C52}.stats span{font-size:15px;color:#6E6A63}
.tl{padding:clamp(88px,11vw,140px) 0 clamp(56px,7vw,90px)}.tl h2{font-family:"Nanum Myeongjo",serif;font-weight:800;text-align:center;font-size:clamp(30px,4.4vw,48px);margin:0 0 90px}
.tl ol{list-style:none;margin:0 auto;padding:0;max-width:860px;position:relative}.tl ol:before{content:"";position:absolute;left:170px;top:8px;bottom:8px;width:1px;background:#CFC8BA}
.tl li{display:grid;grid-template-columns:170px 1fr;gap:56px;margin-bottom:clamp(56px,7vw,96px);position:relative}.tl li:before{content:"";position:absolute;left:165px;top:10px;width:11px;height:11px;border-radius:6px;background:#4A5C52;box-shadow:0 0 0 7px #F7F5F0}
.tl .when{font-family:"Nanum Myeongjo",serif;font-weight:800;font-size:22px;text-align:right;padding-right:10px;color:#4A5C52;padding-top:2px}.tl .what{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:clamp(32px,5vw,64px);align-items:start}.tl .what p{font-size:clamp(17px,1.4vw,19px);line-height:1.85;margin:0;color:#3C3B3A;max-width:380px}.tl .phone{--w:clamp(200px,17vw,230px);box-shadow:0 20px 50px rgba(60,55,45,.16)}
.why{padding:100px 0;background:#EFECE5}.why .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:50px}.why h4{font-family:"Nanum Myeongjo",serif;font-size:22px;font-weight:800;margin:0 0 14px;color:#4A5C52}.why p{margin:0;line-height:1.8;color:#5D5A55}
.end{padding:130px 24px;text-align:center}.end img{width:80px;height:80px;border-radius:20px;margin:0 auto 30px}.end h2{font-family:"Nanum Myeongjo",serif;font-weight:800;font-size:clamp(28px,4vw,44px);margin:0 0 34px}.end small{display:block;margin-top:20px;color:#8E887D}.end small a{text-decoration:underline}
@media(max-width:820px){.tl .what{grid-template-columns:1fr}.tl .what p{margin-bottom:24px}.tl ol:before{left:8px}.tl li{grid-template-columns:1fr;gap:12px;padding-left:36px}.tl li:before{left:3px}.tl .when{text-align:left}.why .grid,.stats{grid-template-columns:1fr}.stats div+div{border-left:0;border-top:1px solid #DDD7CB}.stats div{padding:34px 20px}.hero .stage{gap:14px;height:400px}.hero .stage .phone{--w:165px}.hero .stage .phone:first-child{margin-top:44px}.tl .phone{--w:210px}}"""
body = f"""<header class="hero"><div class="in r"><img class="knot" src="icon.png" alt="{e(a['ko_name'])}"><div class="eyebrow">{e(a['ko_name'])}</div><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p>{store_btn(a)}<div class="rule"></div></div>
<div class="stage fade r d1">{phone(S['funeral'],'장례 정보')}{phone(S['obit_app'],'부고 보내기')}</div></header>
<div class="in"><div class="stats">{''.join(f'<div class="r d{i}"><b>{e(n)}</b><span>{e(l)}</span></div>' for i,(n,l) in enumerate(m['stats']))}</div></div>
<section class="tl"><div class="in"><h2 class="r">{e(C['MJ_TL_T'])}</h2><ol>{tl}</ol></div></section>
<section class="why"><div class="in grid">{''.join(f'<div class="r d{i}"><h4>{e(w["title"])}</h4><p>{e(w["body"])}</p></div>' for i,w in enumerate(m['why']))}</div></section>
<section class="end r"><img src="icon.png" alt=""><h2>{e(m['cta'])}</h2>{store_btn(a)}<small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></section>"""
write(a, css, body)

# ───────────────────────── Reckoner: 전광판형 ─────────────────────────
a = A["reckoner"]; m = a["m"]; S = a["shots"]; sc = {x["screen"]: x for x in m["scenes"]}
SPORTS = [("탁구", "11", "RK_TT"), ("배드민턴", "21", "RK_BD"), ("피클볼", "11", "RK_PB"), ("라켓볼", "15", "RK_RB")]
tabs = "".join(f'<button class="tab{" on" if i == 0 else ""}" data-i="{i}">{e(n)}</button>' for i, (n, _, _) in enumerate(SPORTS))
css = PRETENDARD + """body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#F1EEE7;color:#141414}nav{background:rgba(241,238,231,.86)}
.chip{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:16px;line-height:1;background:#fff;padding:6px 16px 6px 6px;border-radius:16px;box-shadow:0 6px 18px rgba(20,20,20,.06)}.chip img{width:36px;height:36px;border-radius:10px}
.btn.main{background:#FF5B14;color:#fff}
.hero{padding:clamp(40px,6vh,80px) 0 clamp(56px,7vw,96px);overflow:hidden}.hero .in{display:grid;grid-template-columns:1fr 1.05fr;gap:40px;align-items:center}
.hero h1{font-size:clamp(42px,5.4vw,76px);line-height:1.1;letter-spacing:-.05em;font-weight:900;margin:24px 0 20px}.hero p{font-size:clamp(17px,1.4vw,20px);line-height:1.6;color:#5d5a55;margin:0 0 34px;max-width:440px}
.hstats{display:flex;gap:clamp(20px,3vw,40px);margin-top:clamp(32px,5vh,52px);padding-top:24px;border-top:1px solid rgba(20,20,20,.12)}.hstats b{display:block;font-size:clamp(26px,2.4vw,34px);font-weight:900;letter-spacing:-.04em;color:#FF5B14;line-height:1.1}.hstats span{font-size:14px;color:#6c6862}
.stage{position:relative;height:clamp(300px,34vw,420px)}.stage .land{--w:clamp(440px,48vw,700px);position:absolute;left:0;top:50%;transform:translateY(-50%) rotate(-4deg)}
.rules{background:#141414;color:#fff;padding:clamp(80px,10vw,130px) 0}.rules h2{font-size:clamp(32px,4vw,52px);font-weight:900;letter-spacing:-.045em;margin:0 0 36px;text-align:center}
.tabs{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:clamp(36px,5vw,56px)}.tab{font-family:inherit;font-size:16px;font-weight:800;padding:12px 22px;border-radius:999px;border:1px solid #3a3a3a;background:transparent;color:#bdbdbd;cursor:pointer;transition:all .2s}.tab.on{background:#FF5B14;border-color:#FF5B14;color:#fff}
.board{display:grid;grid-template-columns:auto 1fr;gap:clamp(32px,5vw,72px);align-items:center;max-width:940px;margin:0 auto}
.flip{display:flex;gap:10px}.flip span{width:clamp(96px,10vw,140px);height:clamp(132px,13.6vw,190px);background:#232323;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:clamp(84px,9vw,128px);font-weight:900;letter-spacing:-.04em;position:relative;font-variant-numeric:tabular-nums;box-shadow:inset 0 -2px 0 rgba(255,255,255,.04)}
.flip span:after{content:"";position:absolute;left:0;right:0;top:50%;height:2px;background:#141414}.flip span.go{animation:flip .45s cubic-bezier(.3,.7,.3,1)}@keyframes flip{0%{transform:rotateX(70deg);opacity:.2}100%{transform:none;opacity:1}}
.board .lbl{font-size:14px;font-weight:800;color:#FF5B14;letter-spacing:.04em;margin-bottom:12px}.board p{font-size:clamp(19px,1.8vw,24px);line-height:1.6;margin:0;color:#e9e9e9}
.modes{padding:clamp(80px,10vw,130px) 0}.modes h2{font-size:clamp(32px,4vw,52px);font-weight:900;letter-spacing:-.045em;margin:0 0 clamp(40px,5vw,64px);text-align:center}
.mgrid{display:grid;grid-template-columns:minmax(0,.75fr) minmax(0,1.6fr);gap:clamp(16px,2.4vw,28px)}.mstack{display:grid;gap:clamp(16px,2.4vw,28px)}.mode{background:#fff;border-radius:32px;padding:clamp(24px,3vw,36px);display:flex;flex-direction:column}.mode .vis{flex:1;display:flex;align-items:center;justify-content:center}.mode .vis .phone{align-self:center}.mode.wide{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:clamp(20px,3vw,36px);align-items:center}.mode.wide h3{margin-top:0}
.mode .phone{--w:clamp(170px,15vw,220px)}.mode .land{--w:clamp(260px,30vw,420px)}.mode h3{font-size:22px;font-weight:900;letter-spacing:-.03em;margin:26px 0 6px}.mode p{margin:0;color:#6c6862;line-height:1.6}
.feat{padding:clamp(40px,6vw,80px) 0 clamp(80px,10vw,120px)}.feat .in{display:grid;grid-template-columns:1fr 1fr;gap:clamp(40px,6vw,80px);align-items:center}.feat .vis{display:flex;justify-content:center}.feat .phone{--w:clamp(220px,min(22vw,38vh),280px)}
.feat .k{color:#FF5B14;font-weight:800}.feat h3{font-size:clamp(30px,3.8vw,46px);letter-spacing:-.05em;line-height:1.18;margin:14px 0 18px;font-weight:900}.feat p{font-size:18px;color:#5d5a55;line-height:1.7;margin:0;max-width:430px}
.remote{margin:0 auto clamp(80px,10vw,120px);max-width:1088px;width:calc(100% - 2*clamp(20px,5vw,56px));background:#FF5B14;color:#fff;border-radius:clamp(28px,3.4vw,40px);padding:clamp(40px,5vw,64px);text-align:center}.remote h3{font-size:clamp(28px,3.4vw,42px);font-weight:900;letter-spacing:-.04em;margin:0 0 10px}.remote p{margin:0 0 clamp(36px,5vw,56px);font-size:18px;opacity:.92}.rv{display:flex;align-items:center;justify-content:center;gap:clamp(12px,2.4vw,32px)}.rv figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:14px}.rv figcaption{font-size:14px;font-weight:800;opacity:.85}.rv .phone{--w:clamp(160px,15vw,210px);box-shadow:0 30px 60px rgba(0,0,0,.28)}.watch{--w:clamp(130px,12vw,170px);width:var(--w);aspect-ratio:422/514;background:#111;border-radius:calc(var(--w)*.3);padding:calc(var(--w)*.075);box-shadow:0 30px 60px rgba(0,0,0,.28),inset 0 0 0 2px #333}.watch img{width:100%;height:100%;object-fit:cover;border-radius:calc(var(--w)*.2)}.link{display:flex;align-items:center;gap:10px}.link i{width:clamp(16px,3vw,48px);border-top:2px dashed rgba(255,255,255,.6)}.code{display:flex;gap:6px}.code b{width:clamp(34px,3.6vw,46px);height:clamp(44px,4.6vw,58px);border-radius:12px;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-size:clamp(22px,2.4vw,30px);font-weight:900}.why{padding:0 0 clamp(80px,10vw,120px)}.why .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.why .grid div{border-top:3px solid #141414;padding-top:22px}.why h4{font-size:21px;font-weight:900;margin:0 0 10px;letter-spacing:-.03em}.why p{margin:0;color:#5d5a55;line-height:1.7}
.end{text-align:center;padding:clamp(80px,10vw,120px) 24px;background:#141414;color:#fff}.end img{width:92px;height:92px;border-radius:24px;margin:0 auto 24px}.end h2{font-size:clamp(30px,4.4vw,52px);font-weight:900;letter-spacing:-.045em;margin:0 0 30px}.end small{display:block;margin-top:20px;opacity:.6}.end small a{text-decoration:underline}
@media(max-width:900px){.hero .in,.board,.feat .in,.mgrid,.why .grid,.remote{grid-template-columns:1fr}.stage{height:240px}.stage .land{--w:min(96%,420px);left:50%;transform:translate(-50%,-50%) rotate(-4deg)}.rv{flex-direction:column}.link{flex-direction:column}.link i{width:0;height:24px;border-top:0;border-left:2px dashed rgba(255,255,255,.6)}.board{justify-items:center;text-align:center}.mode .vis{min-height:0;padding:12px 0}.mode.wide{grid-template-columns:1fr}.mode .land{--w:min(100%,420px)}.feat.rev .tx{order:0}}"""
modes = f"""<div class="mgrid"><div class="mode tall r"><div class="vis">{phone(S['live'], C['RK_M1'])}</div><h3>{e(C['RK_M1'])}</h3><p>{e(C['RK_M1_B'])}</p></div>
<div class="mstack"><div class="mode wide r d1"><div class="vis">{land(S['farview'], C['RK_M2'])}</div><div class="t"><h3>{e(C['RK_M2'])}</h3><p>{e(C['RK_M2_B'])}</p></div></div>
<div class="mode wide r d2"><div class="vis">{land(S['facing'], C['RK_M3'])}</div><div class="t"><h3>{e(C['RK_M3'])}</h3><p>{e(C['RK_M3_B'])}</p></div></div></div></div>"""
rec = sc['record']
body = f"""<header class="hero"><div class="in"><div class="r"><span class="chip"><img src="icon.png" alt="">{e(a['ko_name'])}</span><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p>{store_btn(a)}
<div class="hstats">{''.join(f'<div><b>{e(n)}</b><span>{e(l)}</span></div>' for n,l in m['stats'])}</div></div>
<div class="stage r d1">{land(S['farview'], '가로 멀리 보기')}</div></div></header>
<section class="rules"><div class="in"><h2 class="r">{e(C['RK_RULE_T'])}</h2><div class="tabs r">{tabs}</div>
<div class="board r"><div class="flip" id="flip"><span>1</span><span>1</span></div><div><div class="lbl" id="rl">{e(SPORTS[0][0])} · {SPORTS[0][1]}점</div><p id="rt">{e(C[SPORTS[0][2]])}</p></div></div></div></section>
<section class="modes"><div class="in"><h2 class="r">{e(C['RK_MODE_T'])}</h2>{modes}</div></section>
<section class="feat"><div class="in"><div class="tx r"><span class="k">{e(rec['kicker'])}</span><h3>{br(rec['title'])}</h3><p>{e(rec['body'])}</p></div><div class="vis r d1">{phone(S['record'], rec['kicker'])}</div></div></section>
<section class="remote r"><div class="rt"><h3>{e(C['RK_REMOTE_T'])}</h3><p>{e(C['RK_REMOTE_B'])}</p></div>
<div class="rv"><figure>{phone(S['remote'], '다른 폰')}<figcaption>iPhone</figcaption></figure><div class="link"><i></i><div class="code"><b>4</b><b>2</b><b>7</b><b>1</b></div><i></i></div><figure><div class="watch"><img src="{S['watch']}" alt="Apple Watch" loading="lazy"></div><figcaption>Apple Watch</figcaption></figure></div></section>
<section class="why"><div class="in grid">{''.join(f'<div class="r d{i}"><h4>{e(w["title"])}</h4><p>{e(w["body"])}</p></div>' for i,w in enumerate(m['why']))}</div></section>
<section class="end r"><img src="icon.png" alt=""><h2>{e(m['cta'])}</h2>{store_btn(a)}<small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></section>"""
js = f"""const SP={json.dumps([[n, p, C[k]] for n, p, k in SPORTS], ensure_ascii=False)};const fl=document.getElementById('flip');
function show(i){{const [n,p,t]=SP[i];const d=p.padStart(2,' ').split('');fl.innerHTML=d.map(c=>'<span class="go">'+c+'</span>').join('');document.getElementById('rl').textContent=n+' · '+p+'점';document.getElementById('rt').textContent=t;
document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('on',+b.dataset.i===i))}}
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>show(+b.dataset.i));"""
write(a, css, body, js)

# ───────────────────────── FloorLog: 기록장형 ─────────────────────────
a = A["floorlog"]; m = a["m"]; S = a["shots"]
css = PRETENDARD + """body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#F3F6F5;color:#1D2B2B}nav{background:rgba(243,246,245,.86)}
.chip{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:16px;line-height:1;background:#fff;padding:6px 16px 6px 6px;border-radius:16px;box-shadow:0 6px 18px rgba(29,43,43,.06)}.chip img{width:36px;height:36px;border-radius:10px}
.btn.main{background:#2C6A68;color:#fff}
.hero{padding:clamp(40px,6vh,80px) 0 clamp(64px,8vw,110px);overflow:hidden}.hero .in{display:grid;grid-template-columns:1.05fr .95fr;gap:40px;align-items:center}
.hero h1{font-size:clamp(40px,5.2vw,72px);line-height:1.14;letter-spacing:-.045em;font-weight:800;margin:24px 0 20px}.hero p{font-size:clamp(17px,1.4vw,20px);line-height:1.65;color:#566463;margin:0 0 34px;max-width:440px}
.hstats{display:flex;gap:clamp(20px,3vw,40px);margin-top:clamp(32px,5vh,52px);padding-top:24px;border-top:1px solid rgba(29,43,43,.12)}.hstats b{display:block;font-size:clamp(24px,2.2vw,32px);font-weight:800;color:#2C6A68;line-height:1.1}.hstats span{font-size:14px;color:#6b7877}
.stage{position:relative;display:flex;justify-content:center;padding:30px 0}.stage .phone{--w:clamp(240px,min(23vw,38vh),300px);z-index:1}
.ring{position:absolute;left:50%;top:42%;width:clamp(240px,24vw,320px);aspect-ratio:1;border-radius:50%;border:1.5px solid rgba(44,106,104,.35);transform:translate(-50%,-50%) scale(.6);opacity:0;animation:wave 4.5s cubic-bezier(.2,.6,.3,1) infinite}.ring.b{animation-delay:1.5s}.ring.c{animation-delay:3s}
@keyframes wave{0%{transform:translate(-50%,-50%) scale(.6);opacity:0}15%{opacity:1}100%{transform:translate(-50%,-50%) scale(2.1);opacity:0}}
.flow{padding:clamp(80px,10vw,130px) 0;background:#fff}.flow h2{font-size:clamp(30px,3.8vw,48px);font-weight:800;letter-spacing:-.045em;margin:0 0 clamp(48px,6vw,80px);text-align:center}
.fl{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(16px,2.4vw,32px);position:relative}.fl:before{content:"";position:absolute;left:12.5%;right:12.5%;top:13px;height:2px;background:#D5E2E0}
.fs{display:flex;flex-direction:column;align-items:center;text-align:center;position:relative}.fs .dot{width:28px;height:28px;border-radius:14px;background:#2C6A68;color:#fff;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 7px #fff}
.fs h3{font-size:20px;font-weight:800;letter-spacing:-.03em;margin:18px 0 6px}.fs p{margin:0 0 28px;font-size:15px;line-height:1.6;color:#566463;max-width:220px}.fs .phone{--w:clamp(170px,15vw,220px);box-shadow:0 24px 50px rgba(29,43,43,.14)}
.note{padding:clamp(72px,9vw,110px) 0}.note .card{max-width:760px;margin:0 auto;background:#E3EDEB;border-radius:28px;padding:clamp(28px,4vw,44px);display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:start}
.note svg{width:30px;height:30px;stroke:#2C6A68;fill:none;stroke-width:1.8;stroke-linecap:round}.note h3{margin:0 0 8px;font-size:20px;font-weight:800}.note p{margin:0;line-height:1.7;color:#3e4f4e}
.why{padding:0 0 clamp(80px,10vw,120px)}.why .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(20px,3vw,40px)}.why h4{font-size:20px;font-weight:800;margin:0 0 10px;color:#2C6A68}.why p{margin:0;color:#566463;line-height:1.7}
.end{text-align:center;padding:clamp(80px,10vw,120px) 24px;background:#1D2B2B;color:#fff}.end img{width:92px;height:92px;border-radius:24px;margin:0 auto 24px}.end h2{font-size:clamp(30px,4.2vw,50px);font-weight:800;letter-spacing:-.045em;margin:0 0 30px}.end .btn.main{background:#fff;color:#1D2B2B}.end small{display:block;margin-top:20px;opacity:.6}.end small a{text-decoration:underline}
@media(max-width:900px){.hero .in,.why .grid{grid-template-columns:1fr}.fl{grid-template-columns:1fr 1fr;row-gap:56px}.fl:before{display:none}}@media(max-width:560px){.fl{grid-template-columns:1fr}}"""
flow = "".join(f'<div class="fs r d{i%3}"><span class="dot">{i+1}</span><h3>{e(C[f"FL_F{i+1}"])}</h3><p>{e(C[f"FL_F{i+1}_B"])}</p>{phone(S[s], C[f"FL_F{i+1}"])}</div>' for i, s in enumerate(["record", "timeline", "pattern", "pdf"]))
body = f"""<header class="hero"><div class="in"><div class="r"><span class="chip"><img src="icon.png" alt="">{e(a['ko_name'])}</span><h1>{br(m['hero_title'])}</h1><p>{e(m['hero_sub'])}</p>{store_btn(a)}
<div class="hstats">{''.join(f'<div><b>{e(n)}</b><span>{e(l)}</span></div>' for n,l in m['stats'])}</div></div>
<div class="stage r d1"><i class="ring"></i><i class="ring b"></i><i class="ring c"></i>{phone(S['record'], '소음 기록')}</div></div></header>
<section class="flow"><div class="in"><h2 class="r">{e(C['FL_FLOW_T'])}</h2><div class="fl">{flow}</div></div></section>
<section class="why"><div class="in grid">{''.join(f'<div class="r d{i}"><h4>{e(w["title"])}</h4><p>{e(w["body"])}</p></div>' for i,w in enumerate(m['why']))}</div></section>
<section class="end r"><img src="icon.png" alt=""><h2>{e(m['cta'])}</h2>{store_btn(a)}<small><a href="{e(a['privacy'])}">{e(C['LINK_PRIVACY'])}</a></small></section>"""
write(a, css, body)

# ───────────────────────── 메인(스튜디오) ─────────────────────────
TONE = {"reckoner": ("#F1EEE7", "#141414", "#FF5B14"), "floorlog": ("#E3EDEB", "#1D2B2B", "#2C6A68"), "lucky-bite": ("#FFF1E6", "#2A1A10", "#FF7A3D"), "quiz-bite": ("#EAF0FF", "#1B2440", "#4F7CFF"), "officekit": ("#0F1424", "#FFFFFF", "#7EA0FF"), "maejeum": ("#EFECE5", "#2B2B2D", "#4A5C52")}
cards = ""
for i, a in enumerate(apps):
    bg, fg, ac = TONE[a["slug"]]; m = a["m"]; hs = (a["hero"] + [x["screen"] for x in a["m"]["scenes"] if x["screen"] not in a["hero"]])[:2]
    font = ' style="font-family:\'Nanum Myeongjo\',serif"' if a["slug"] == "maejeum" else ""
    cards += f"""<a class="card c{i} k-{a['slug']} r" href="/{a['slug']}/" style="--bg:{bg};--fg:{fg};--ac:{ac}"><div class="tx"><span class="nm"><img src="/{a['slug']}/icon.png" alt="">{e(a['ko_name'])}</span><h2{font}>{br(m['hero_title'])}</h2><span class="go">{e(C['BTN_MORE'])} →</span></div>
<div class="ph">{''.join(phone(f"/{a['slug']}/{a['shots'][h]}", a['ko_name']) for h in hs[:2])}</div></a>"""
css = """@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@800&display=swap');""" + PRETENDARD + """
body{font-family:"Pretendard Variable",Pretendard,sans-serif;background:#FAFAF8;color:#16181D}nav{background:rgba(250,250,248,.85)}
.hero{padding:clamp(64px,12vh,128px) 0 clamp(48px,7vh,80px)}.hero h1{font-size:clamp(44px,6.4vw,92px);line-height:1.06;letter-spacing:-.055em;font-weight:900;margin:0}.hero p{font-size:clamp(17px,1.4vw,20px);color:#5E6370;margin:26px 0 0}
.wall{display:grid;grid-template-columns:repeat(2,1fr);gap:20px;padding-bottom:90px}.card{position:relative;border-radius:40px;background:var(--bg);color:var(--fg);overflow:hidden;min-height:620px;display:flex;flex-direction:column;transition:transform .35s cubic-bezier(.2,.7,.2,1)}
.card:hover{transform:translateY(-6px)}.card .tx{padding:clamp(32px,3.6vw,48px) clamp(28px,3.6vw,48px) 0}.nm{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:16px}.nm img{width:40px;height:40px;border-radius:10px}
.card h2{font-size:clamp(30px,3.4vw,44px);line-height:1.15;letter-spacing:-.045em;margin:22px 0 14px;font-weight:900}.go{font-weight:800;color:var(--ac)}
.ph{margin-top:auto;display:flex;justify-content:center;align-items:flex-start;gap:18px;height:340px;padding-top:36px}.ph .phone{--w:200px;transition:transform .5s cubic-bezier(.2,.7,.2,1)}.ph .phone:first-child{margin-top:44px}
.k-lucky-bite .ph .phone{transition:transform .55s cubic-bezier(.34,1.7,.5,1)}.k-lucky-bite:hover .ph .phone:first-child{transform:rotate(-9deg) translateY(-12px)}.k-lucky-bite:hover .ph .phone:last-child{transform:rotate(7deg) translateY(-20px)}.k-quiz-bite .ph .phone{transition:transform .35s cubic-bezier(.3,1.4,.5,1)}.k-quiz-bite .ph .phone:last-child{transition-delay:.12s}.k-quiz-bite:hover .ph .phone{transform:translateY(-26px)}.k-officekit .ph .phone{transition:transform .5s cubic-bezier(.2,.8,.2,1)}.k-officekit .ph .phone:last-child{z-index:1}.k-officekit:hover .ph .phone:first-child{transform:translateX(42px) scale(.9)}.k-officekit:hover .ph .phone:last-child{transform:translateX(-42px) scale(.96)}.k-maejeum .ph .phone{transition:transform 1.4s cubic-bezier(.2,.6,.2,1)}.k-maejeum:hover .ph .phone{transform:translateY(-10px)}.k-maejeum:hover .ph .phone:last-child{transition-delay:.15s}.card:hover{transform:translateY(-4px)}.k-reckoner .ph .phone{transition:transform .22s cubic-bezier(.3,1.8,.5,1)}.k-reckoner:hover .ph .phone:first-child{transform:translateY(-14px)}.k-reckoner:hover .ph .phone:last-child{transform:translateY(-14px) scale(1.04)}.k-floorlog .ph .phone{transition:transform .9s cubic-bezier(.2,.7,.2,1)}.k-floorlog:hover .ph .phone{transform:translateY(-12px)}.k-floorlog:hover .ph .phone:last-child{transition-delay:.25s}
.c0,.c3{grid-column:span 2;min-height:0;height:clamp(480px,62vh,560px);flex-direction:row}.c0 .tx,.c3 .tx{flex:1;padding:clamp(40px,5vw,64px);align-self:center}.c0 h2,.c3 h2{font-size:clamp(34px,3.6vw,50px)}.c0 .ph,.c3 .ph{flex:1;height:100%;padding-top:clamp(40px,6vh,64px)}.c0 .ph .phone,.c3 .ph .phone{--w:clamp(180px,16vw,220px)}.c0 .ph,.c3 .ph{gap:clamp(14px,2vw,24px);flex:0 0 50%}.c0 .tx,.c3 .tx{min-width:0}.c3{flex-direction:row-reverse}
@media(max-width:860px){.wall{grid-template-columns:1fr}.c0,.c3{grid-column:auto;flex-direction:column}.c0 .tx,.c3 .tx{padding:40px 30px 0}.card .tx{padding:36px 30px 0}.ph .phone,.c0 .ph .phone,.c3 .ph .phone{--w:140px}.ph{gap:12px;height:300px}.c0 .ph,.c3 .ph{height:300px;padding-top:30px;flex:none}.card{min-height:0}}"""
open(f"{OUT}/index.html", "w").write(page("/", "Importants Studio", C["STUDIO_SUB"], css,
    f'<header class="hero"><div class="in r"><h1>{br(C["STUDIO_HEADLINE"])}</h1><p>{e(C["STUDIO_SUB"])}</p></div></header><div class="in wall">{cards}</div>',
    extra=f'\n<meta property="og:image" content="{BASE}/{apps[0]["slug"]}/icon.png">'))

today = datetime.date.today().isoformat()
open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>" for p in ["/"] + [f"/{a['slug']}/" for a in apps]) + "</urlset>\n")
open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nDisallow: /review/\nSitemap: {BASE}/sitemap.xml\n")
shutil.copytree("review", f"{OUT}/review")  # 앱 심사관용 견본 파일(목록·검색 노출 안 함)
open(f"{OUT}/CNAME", "w").write("apps.importants-studio.com\n"); open(f"{OUT}/.nojekyll", "w").write("")
print("built", [a["slug"] for a in apps])
