#!/usr/bin/env python3
"""소개 페이지 숫자 띠(3개) — 앱별 정말 특징적인 사실만, 자연스러운 한국어. 로컬 LLM(Gemma). marketing.json의 stats를 바꿈."""
import json, urllib.request, re, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
F = {  # 핵심 기능 3개, 중요한 순(검색량·앱 목적 기준). 부가 기능(AI 게임 수·자리 배치판 등)은 넣지 않음
 "lucky-bite": ["사다리타기·돌림판·제비뽑기 등 뽑기 게임 25가지", "모임 명단을 저장해 두고 바로 불러와 시작", "공정 모드: 최근 자주 걸린 사람은 덜 걸리게"],
 "quiz-bite": ["넌센스·상식·맞춤법·사자성어 문제 1,488개", "하루 10문제씩 이정표를 하나씩 깸", "틀리면 바로 한 줄 해설"],
 "officekit": ["제출처가 정한 용량(예: 1MB·50KB) 이하로 사진·PDF 줄이기", "PDF 합치기와 JPG·PDF 변환", "종이 문서를 찍으면 테두리를 알아서 잡는 스캔"],
 "maejeum": ["모바일 부고장과 모바일 감사장을 둘 다 보냄(value는 '부고장·감사장', label은 '부고와 감사 인사를 링크로'처럼 둘 다 담을 것)", "부의금을 장례비 빼고 상주별로 나누는 정산", "삼우제·49재 날짜 자동 계산(value는 '49재 날짜 계산'. label 예: '삼우제·49재 날짜를 자동으로'. 제사라는 단어 절대 금지)"],
 "reckoner": ["탁구·배드민턴·피클볼·라켓볼 4종목을 규칙대로 점수 세기", "서브권·듀스·매치포인트 자동 표시", "애플워치와 다른 아이폰으로 점수 조작(value는 '워치·폰으로 조작'처럼 둘 다)"],
 "chaekkan": ["페이지를 넘기거나 글자 크기를 바꿔도 글자가 잘리지 않음(value 예: '글자 잘림 없이')", "읽던 자리를 기억하고 아이폰·아이패드 이어 읽기", "txt 소설·만화(zip·cbz)·PDF를 한 앱에서(value는 'txt·만화·PDF', '모든' 같은 과장 금지)"],
 "floorlog": ["소음이 들릴 때 버튼 한 번으로 기록", "시간대·요일별로 소음이 몰리는 때를 보여 줌", "기간을 골라 민원·이웃사이센터 신청용 PDF로 정리"],
}
RULE = ("앱 소개 페이지 첫 화면의 특징 3개를 만든다. 각 항목은 value(큰 글씨)와 label(작은 설명). "
        "value: 숫자+한국어 단위(예: '25가지', '1,488문제', '8가지', '5장') 또는 짧은 한국어 명사(예: '애플워치', 'PDF 정리'). 2~6자. '1탭' 같은 줄임말·영어 약어 금지. "
        "label: 6~14자 자연스러운 한국어 명사구. value의 숫자나 단어를 되풀이하지 말 것(나쁜 예: value '4', label '4가지 라켓 종목'). 해요체 문장 금지, 명사구로. "
        "쉬운 우리말로, 기능을 있는 그대로 부를 것. 금지어: 최적화·스마트·멀티·디바이스·원터치·시스템·솔루션·연동·기능(접미사)·다양한·방대한·간편한. value 좋은 예: '뽑기 25가지', '1,488문제', '부의금 정산', '49재 날짜 계산', '애플워치 조작', '버튼 한 번'. label 좋은 예: '사다리타기·돌림판·제비뽑기', '장례비 빼고 상주별로', '제출처 용량에 맞춰'. 주어진 기능 3개를 순서 그대로 하나씩 [value,label]로 바꾼다. 다른 기능을 더하거나 빼지 말 것. 출력은 정확히 [[value,label],[value,label],[value,label]] 형태의 JSON 하나만.")
M = json.load(open("marketing.json"))
for slug, facts in F.items():
    if sys.argv[1:] and slug not in sys.argv[1:]: continue
    body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "temperature": 0.4, "max_tokens": 300, "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": f"앱: {M[slug]['hero_title'].replace(' / ', ' ')}\n기능(중요한 순): " + " / ".join(facts)}]}
    t = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900))["choices"][0]["message"]["content"]
    st = json.loads(re.search(r"\[.*\]", t, re.S).group(0))
    assert len(st) == 3 and all(len(x) == 2 for x in st), (slug, st)
    M[slug]["stats"] = st; print(slug, st)
json.dump(M, open("marketing.json", "w"), ensure_ascii=False, indent=1)
