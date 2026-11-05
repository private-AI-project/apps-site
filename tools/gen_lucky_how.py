#!/usr/bin/env python3
"""뽑기 한입 '이렇게 써요' 3단계·마지막 문구 — 로컬 LLM(Gemma, 127.0.0.1:8088). 결과는 site_copy.json에 병합."""
import json, urllib.request, re
FACTS = """앱: 뽑기 한입(아이폰). 여럿 중 당첨자·순서·자리를 공정하게 정하는 뽑기 게임 25가지.
1단계 화면(홈): 저장해 둔 명단(예: '금요일 회식' 6명)을 한 번에 불러오고, 돌림판·사다리타기·제비뽑기·동전 던지기·스크래치 복권·인형뽑기 등에서 게임을 고른다. 분류: 당첨 뽑기, 순위 정하기, 모여 뽑기.
2단계 화면(제비뽑기): 참가자가 차례로 막대를 뽑고, 끝이 빨간 막대를 뽑은 사람이 당첨.
3단계 화면(기록): 명단별로 누가 몇 번 당첨·1위·꼴찌였는지 쌓인다. 공정 모드를 켜면 최근 자주 걸린 사람은 당첨 확률이 줄어든다."""
RULE = ("모든 문장은 해요체로 끝내. 합니다체 금지. 한국 IT 서비스 소개 페이지(토스·당근) 카피라이터처럼 짧고 또렷하게. "
        "요금·광고·무료·개인정보 이야기 금지. '모임을 시작' 같은 말 금지 — 이 앱은 모임을 여는 앱이 아니라 정할 것을 뽑는 앱이다. "
        "섹션을 설명하는 말('~하는 섹션이에요') 금지, 방문자에게 바로 건네는 말로.")
ASK = """다음 JSON만 출력해:
{"LB_HOW_T":"세 단계 사용법 섹션 제목(18자 이내)",
 "LB_H1":"1단계 제목(12자 이내)","LB_H1_B":"1단계 설명 한 문장(40자 이내)",
 "LB_H2":"2단계 제목","LB_H2_B":"2단계 설명","LB_H3":"3단계 제목","LB_H3_B":"3단계 설명",
 "LB_CTA":"페이지 맨 아래 다운로드 유도 제목(16자 이내, 뽑기·결정에 대한 말)"}"""
body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "temperature": 0.6, "max_tokens": 900, "chat_template_kwargs": {"enable_thinking": False},
        "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": FACTS + "\n\n" + ASK}]}
r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900)
t = json.load(r)["choices"][0]["message"]["content"]
d = json.loads(re.search(r"\{.*\}", t, re.S).group(0))
print(json.dumps(d, ensure_ascii=False, indent=1))
p = "tools/site_copy.json"; c = json.load(open(p)); c.update(d); json.dump(c, open(p, "w"), ensure_ascii=False, indent=1)
