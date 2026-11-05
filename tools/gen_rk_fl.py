#!/usr/bin/env python3
"""Reckoner·FloorLog 전용 섹션 문구 — 로컬 LLM(Gemma). 사실은 FACTS에 고정, 모델은 말만. site_copy.json에 병합."""
import json, urllib.request, re
RULE = ("모든 문장은 해요체. 합니다체 금지. 한국 IT 서비스 소개 페이지(토스·당근) 카피라이터처럼 짧고 또렷하게. "
        "가격·광고·무료·개인정보 금지. 감탄사·느낌표·이모지 금지. 섹션을 설명하는 말('~섹션이에요') 금지. 출력은 JSON 하나만.")
JOBS = {
"reckoner": ("""앱: Reckoner - 점수 카운터(탁구·배드민턴·피클볼·라켓볼 점수판). '판정'·'분쟁'·'심판 대신' 금지, 규칙대로 세고 기록한다까지만.
종목별 규칙 사실(앱이 자동으로 따라 셈):
- 탁구: 11점 게임, 10:10부터 듀스로 2점 차가 나야 끝, 서브는 2점마다 교대하고 듀스부터는 1점마다 교대
- 배드민턴: 21점 랠리 포인트, 20:20부터 2점 차, 29:29면 30점을 먼저 낸 쪽이 이김
- 피클볼: 11점 2점 차, 서브하는 쪽만 득점(사이드아웃), 복식은 서버 1·2번 순서
- 라켓볼: 15점 게임, 서브하는 쪽만 득점, 3게임째는 11점
보기 방식: 세로 점수판(손에 들고 탭으로 득점), 가로 멀리 보기(세워 두고 멀리서 큰 숫자), 마주 보기(마주 앉은 양쪽이 각자 정방향)
리모컨: 다른 폰이나 애플워치로 점수판 조작, 4자리 코드로 연결""",
 {"RK_RULE_T": "종목별 규칙을 앱이 대신 세 준다는 섹션 제목(20자 이내)",
  "RK_TT": "탁구 규칙을 앱이 어떻게 세는지 한두 문장(50자 이내)", "RK_BD": "배드민턴 같은 방식", "RK_PB": "피클볼 같은 방식", "RK_RB": "라켓볼 같은 방식",
  "RK_MODE_T": "보기 방식 3가지 섹션 제목(18자 이내)",
  "RK_M1": "세로 점수판 이름(8자 이내)", "RK_M1_B": "설명 30자 이내", "RK_M2": "가로 멀리 보기 이름", "RK_M2_B": "설명", "RK_M3": "마주 보기 이름", "RK_M3_B": "설명",
  "RK_REMOTE_T": "리모컨·워치 제목(16자 이내)", "RK_REMOTE_B": "리모컨 설명 40자 이내"}),
"floorlog": ("""앱: FloorLog - 층간소음 기록. '증거' 금지, 측정값은 참고값, 법정 기준 초과 단정 금지, 차분한 말투.
흐름 사실: ①소음이 들리면 가운데 버튼 한 번(크기 약 dB 참고값·시각 저장, 유형·메모·영상 첨부) ②날짜별 타임라인으로 쌓임 ③시간대·요일별 빈도 차트와 '주로 밤 7시~9시에 몰려 있어요' 같은 한 줄 요약 ④기간을 골라 정리 문서 PDF(기록표·차트·패턴 요약 문장)를 관리사무소 민원이나 이웃사이센터 신청 때 함께 냄
참고 사실: 폰 마이크 측정은 보정되지 않은 근사치라 공식 측정과 다를 수 있음. 공식 측정은 이웃사이센터(1661-2642)에서 받을 수 있음""",
 {"FL_FLOW_T": "누르기부터 문서까지 흐름 섹션 제목(18자 이내)",
  "FL_F1": "1단계 동사형 짧은 이름(6자 이내)", "FL_F1_B": "설명 35자 이내", "FL_F2": "2단계 이름", "FL_F2_B": "설명", "FL_F3": "3단계 이름", "FL_F3_B": "설명", "FL_F4": "4단계 이름", "FL_F4_B": "설명",
  "FL_NOTE_T": "측정값 안내 제목(14자 이내, 차분하게)", "FL_NOTE": "참고값이라는 점과 공식 측정 안내 두 문장(70자 이내, 전화번호 포함)"}),
}
out = {}
for k, (facts, schema) in JOBS.items():
    body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "temperature": 0.5, "max_tokens": 1500, "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": facts + "\n\n다음 키를 채운 JSON:\n" + json.dumps(schema, ensure_ascii=False, indent=1)}]}
    r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900)
    t = json.load(r)["choices"][0]["message"]["content"]
    out.update(json.loads(re.search(r"\{.*\}", t, re.S).group(0)))
print(json.dumps(out, ensure_ascii=False, indent=1))
p = "tools/site_copy.json"; c = json.load(open(p)); c.update(out); json.dump(c, open(p, "w"), ensure_ascii=False, indent=1)
