#!/usr/bin/env python3
"""소개 페이지 새 장면 문구 후보(gpt-5.5) — 2026-11-14 뽑기 한입 1.3.1·오피스킷 1.1.0 반영.
사실은 FACTS에 고정, 모델은 말만. 기존 장면 문구를 형식 예시로 줌. 출력 tools/_scenes_v2.json(후보), 고른 것은 marketing.json에 직접."""
import json, os, re, urllib.request
os.chdir(os.path.dirname(os.path.abspath(__file__)))
KEY = next(l.split("=", 1)[1].strip().strip('"') for l in open(os.path.expanduser("~/blog-automation/.env")) if l.startswith("OPENAI_API_KEY="))
M = json.load(open("marketing.json"))
JOBS = {
 "lucky-bite": {"app": "뽑기 한입 — 모임에서 당첨·순서·자리·팀을 정하는 뽑기 게임 앱(게임 30가지)", "scenes": [
   ["arena", "이름 배틀로얄: 참가자 캐릭터들이 원형 경기장에서 자동으로 싸우고, 마지막까지 남은 한 명이 당첨. 중계 자막이 흐르고 2배속·결과 바로 보기가 있음. 손으로 조작하지 않고 지켜보는 게임"],
   ["smile", "웃으면 탈락: 휴대폰 카메라에 모두 얼굴을 비추면 앱이 얼굴마다 번호를 붙이고, 먼저 웃은 사람을 탈락으로 표시하는 웃음 참기 대결. 카메라로 하는 게임(얼굴 룰렛·눈싸움)도 함께 있음"]]},
 "officekit": {"app": "오피스킷 — 문서 스캔, 사진·PDF 용량 줄이기, 변환을 한 앱에서 하는 문서 도구(도구 12가지)", "scenes": [
   ["stamp", "도장·서명: 이름을 입력하면 원형·사각형·타원형 도장이 만들어지고 글꼴(명조·고딕)과 색(빨강·파랑·검정)을 고름. 손가락으로 서명을 그리거나 종이에 찍은 도장을 사진으로 찍어 배경 없이 가져올 수 있음. 만든 도장을 PDF나 사진 위 원하는 자리에 찍고, 투명 PNG로도 저장"],
   ["lock", "PDF 암호: 암호가 걸린 PDF에 암호를 한 번 입력하면 암호 없이 열리는 사본을 만들어 줌. 반대로 보내기 전 PDF에 암호를 걸 수도 있음"]]}}
RULE = ("너는 한국 IT 서비스 소개 페이지(토스·당근 스타일) 카피라이터다. 해요체(~해요, ~돼요, ~있어요)만, 합니다체 금지. 혜택 중심, 짧고 또렷하게, 긍정형. "
        "금지: 가격·무료·유료·광고·구독·결제 언급, 개인정보·서버·로그인 언급, 'AI' 언급, 감탄사·느낌표·이모지, 과장(최고·완벽·1위), 주어진 사실에 없는 기능이나 약속. 출력은 JSON 하나만.")
out = {}
for slug, j in JOBS.items():
    ex = [{k: s[k] for k in ("kicker", "title", "body")} for s in M[slug]["scenes"]]
    for scr, fact in j["scenes"]:
        user = (f"앱: {j['app']}\n이 화면의 사실(이 범위 안에서만): {fact}\n\n같은 페이지에 이미 있는 장면 문구(형식·길이·말투를 맞출 것):\n{json.dumps(ex, ensure_ascii=False, indent=1)}\n\n"
                '후보 4개를 {"candidates":[{"kicker":"그 화면을 쓰는 상황 6~12자, ~때로 끝남","title":"혜택 제목 두 줄, 줄 사이 \' / \', 줄마다 5~13자","body":"30~60자 한두 문장"}]} 형식으로.')
        body = {"model": "gpt-5.5", "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": user}], "response_format": {"type": "json_object"}}
        r = urllib.request.urlopen(urllib.request.Request("https://api.openai.com/v1/chat/completions", json.dumps(body).encode(),
                                   {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"}), timeout=300)
        d = json.load(r); out[f"{slug}/{scr}"] = json.loads(d["choices"][0]["message"]["content"])["candidates"]
        print(slug, scr, d.get("usage", {}).get("total_tokens"))
json.dump(out, open("_scenes_v2.json", "w"), ensure_ascii=False, indent=1)
