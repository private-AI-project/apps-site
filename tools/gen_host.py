#!/usr/bin/env python3
"""뽑기 한입 방장 모드 섹션·마지막 문구 — 로컬 LLM(Gemma). site_copy.json에 병합."""
import json, urllib.request, re
FACTS = """앱: 뽑기 한입(사다리타기·돌림판·제비뽑기 등 뽑기 게임 25가지).
방장 모드(Pro): 게임을 시작하기 전 대기 화면에서 게임 아이콘을 길게 누르면 숨은 패널이 열리고, 다음 한 판의 당첨자(또는 꼴찌)를 몰래 정할 수 있다. 화면 연출은 평소와 똑같아서 아무도 눈치채지 못한다. 돌림판·사다리타기·경마·풍선 터뜨리기 등 여러 게임에 적용.
블루투스 리모컨: 두 번째 아이폰이나 아이패드로 멀리서 결과를 조작할 수 있다.
용도 예: 생일인 친구가 걸리게 하는 깜짝 이벤트, 모임 진행자가 분위기를 이끌 때."""
RULE = ("모든 문장 끝은 반드시 ~해요/~돼요/~있어요/~보세요. 반말(~해, ~봐, ~보여, ~어)과 합니다체 금지. 제목도 반말 금지. 짧고 재치 있게, 한국 IT 서비스 소개 페이지 카피. 가격·Pro·유료·광고 언급 금지. 느낌표·이모지 금지. "
        "쉬운 우리말, 번역투·외래어 금지. '판넬' 아니라 '패널'. 출력은 JSON 하나만.")
ASK = """{"LB_HOST_K":"섹션 위 작은 라벨(6~10자, 예: 모임 진행자를 위한)","LB_HOST_T":"방장 모드 섹션 제목 두 줄, 줄 사이 ' / ', 줄마다 6~12자, 결과를 몰래 정할 수 있다는 재미",
"LB_HOST_B":"설명 한두 문장 40~70자","LB_H_S1":"1단계 짧은 제목(8~12자, 아이콘 길게 누르기)","LB_H_S2":"2단계 짧은 제목(8~12자, 다음 판 결과 고르기)","LB_H_S3":"3단계 짧은 제목(8~14자, 다른 아이폰을 리모컨으로)",
"LB_CTA":"페이지 맨 아래 다운로드 권유 제목(10~16자), '뽑기'나 '당첨'이라는 말을 반드시 넣고 설렘이 느껴지게, '결정'이라는 말 금지"}"""
body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "temperature": 0.4, "max_tokens": 600, "chat_template_kwargs": {"enable_thinking": False},
        "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": FACTS + "\n\n다음 JSON을 채워:\n" + ASK}]}
t = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900))["choices"][0]["message"]["content"]
d = json.loads(re.search(r"\{.*\}", t, re.S).group(0)); print(json.dumps(d, ensure_ascii=False, indent=1))
p = "tools/site_copy.json"; c = json.load(open(p)); c.update(d); json.dump(c, open(p, "w"), ensure_ascii=False, indent=1)
