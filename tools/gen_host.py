#!/usr/bin/env python3
"""뽑기 한입 방장 모드 섹션·마지막 문구 — 로컬 LLM(Gemma). site_copy.json에 병합."""
import json, urllib.request, re
FACTS = """앱: 뽑기 한입(사다리타기·돌림판·제비뽑기 등 뽑기 게임 25가지).
방장 모드: 게임 시작 전 대기 화면에서 게임 아이콘을 길게 누르면 숨은 패널이 열리고, 다음 한 판의 당첨자(또는 1등·꼴찌)를 몰래 정할 수 있다. 다음 한 판에만 적용되고 끝나면 지워진다. 화면 연출은 평소와 똑같아서 아무도 눈치채지 못한다. 돌림판·사다리타기·제비뽑기·경마·폭탄 돌리기·악어 룰렛 등에 적용.
리모컨·다른 기기 조작 기능은 없다(절대 언급 금지).
용도 예: 생일인 친구가 걸리게 하는 깜짝 이벤트, 벌칙을 정해 둔 사람에게 몰아주기."""
RULE = ("모든 문장 끝은 반드시 ~해요/~돼요/~있어요/~보세요. 반말(~해, ~봐, ~보여, ~어)과 합니다체 금지. 제목도 반말 금지. 짧고 재치 있게, 한국 IT 서비스 소개 페이지 카피. 가격·Pro·유료·광고 언급 금지. 느낌표·이모지 금지. "
        "쉬운 우리말, 번역투·외래어 금지. '판넬' 아니라 '패널'. 출력은 JSON 하나만.")
ASK = """{"LB_HOST_K":"섹션 위 작은 라벨(6~10자, 예: 모임 진행자를 위한)","LB_HOST_T":"방장 모드 섹션 제목 두 줄, 줄 사이 ' / ', 줄마다 6~12자, 결과를 몰래 정할 수 있다는 재미",
"LB_HOST_B":"설명 한두 문장 40~70자","LB_H_S1":"1단계 짧은 제목(8~12자, 게임 아이콘을 길게 눌러 숨은 패널 열기)","LB_H_S2":"2단계 짧은 제목(8~12자, 당첨자를 고르는 동작. \"패널\"·\"열기\"라는 말 금지. 예 형식: \"OO를 몰래 골라요\")","LB_H_S3":"3단계 짧은 제목(8~14자, 평소처럼 게임을 시작하면 정한 결과가 나옴)",
"LB_CTA":"페이지 맨 아래 다운로드 권유 제목(10~16자), '뽑기'나 '당첨'이라는 말을 반드시 넣고 설렘이 느껴지게, '결정'이라는 말 금지"}"""
body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "temperature": 0.4, "max_tokens": 600, "chat_template_kwargs": {"enable_thinking": False},
        "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": FACTS + "\n\n다음 JSON을 채워:\n" + ASK}]}
t = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900))["choices"][0]["message"]["content"]
d = json.loads(re.search(r"\{.*\}", t, re.S).group(0)); print(json.dumps(d, ensure_ascii=False, indent=1))
p = "tools/site_copy.json"; c = json.load(open(p)); c.update(d); json.dump(c, open(p, "w"), ensure_ascii=False, indent=1)
