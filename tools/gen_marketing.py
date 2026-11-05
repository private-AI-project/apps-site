#!/usr/bin/env python3
"""앱별 소개 페이지 마케팅 문구(로컬 Gemma). 사실·숫자·화면은 FACTS에 고정, 모델은 말만 씀. 출력 marketing.json
실행: python3 tools/gen_marketing.py [slug]"""
import json, sys, urllib.request, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
FACTS = {
 "lucky-bite": {"name": "뽑기 한입", "what": "모임에서 당첨·순서·자리·팀을 정하는 뽑기 게임 앱",
   "facts": "돌림판·사다리타기·제비뽑기·경마 레이스·폭탄 돌리기·악어 룰렛·플링코·라이어 게임 등 뽑기 게임 21가지 + 마니또 뽑기 + AI 게임 3가지(AI 법정: 각자 최후 변론을 하면 AI가 판결, AI 밸런스 게임, AI 마음대로) = 모두 25가지. 참가자 이름과 사진 등록, 모임 명단 저장, 결과 카드 공유, 자리 배치(원탁·긴 테이블·교실), 공정 모드(최근 많이 걸린 사람 확률 낮춤), 모임별 당첨 기록",
   "extra": "큰 제목 예시 형식(그대로 쓰지 말 것): '고민될 땐 / 한 번에 뽑아요'. 모임에서 누가 걸릴지·누가 먼저 할지 고민을 바로 끝낸다는 혜택. '기록'이라는 말 금지",
   "stats": [["25", "게임 수"], ["3", "AI 게임 수"], ["4", "자리 배치판 종류(원탁·긴 테이블·교실·자유)"]],
   "scenes": [["home", "홈: 게임 목록과 오늘의 모임 명단"], ["race", "경마 레이스: 참가자 캐릭터가 달리는 게임"], ["court", "AI 법정: 커피 쏘기 재판, 각자 변론하면 AI가 판결"], ["seats", "자리 배치판"]]},
 "quiz-bite": {"name": "퀴즈 한입", "what": "매일 조금씩 푸는 상식·넌센스 퀴즈 앱",
   "facts": "넌센스·상식 OX·상식 4지선다·맞춤법·사자성어 다섯 가지 퀴즈, 모두 1,488문제. 10문제씩 푸는 이정표를 깨며 카테고리별 그림 지도를 따라감. 틀리면 바로 정답과 한 줄 해설. 이정표를 마치면 등급(S~D)과 칭호, 결과 카드 저장·공유. 안내 요정이 처음부터 도와줌. 연속 출석 기록, 다음 이정표 열리면 아침 9시 알림",
   "stats": [["1,488", "문제 수"], ["5", "퀴즈 종류"], ["10", "이정표 하나의 문제 수"]],
   "scenes": [["map", "카테고리별 그림 지도 위 이정표"], ["quiz", "OX 문제와 바로 나오는 해설"], ["result", "결과 카드: 9/10, 등급 A, 칭호 상식 박사님"], ["onboarding", "안내 요정과 대화로 시작"]]},
 "officekit": {"name": "오피스킷", "what": "문서 스캔과 사진·PDF 용량 줄이기, 변환을 한 앱에서 하는 문서 도구",
   "facts": "문서 스캔(테두리 자동 인식, 무음 연속 촬영, 모서리 조정, 필터), 신분증 앞뒷면을 A4 한 장에 배치·'OO은행 제출용+날짜' 사선 문구·주민번호 뒷자리 가리기, 제출처 제한 용량(예 50KB·1MB)을 입력하면 그 이하로 맞춰 저장, 줄이기 전후 화질 나란히 비교, HEIC를 JPG로, 사진 여러 장을 PDF로, PDF 합치기·페이지 정리·나누기·이미지로, 보관함 자동 정리, 카카오톡·사진 앱에서 공유하기로 바로 불러오기, 위젯·Siri 단축어. 문서 도구 8가지",
   "stats": [["8", "문서 도구 수"], ["50KB", "맞출 수 있는 작은 용량 예"], ["A4 1장", "신분증 앞뒷면 배치"]],
   "scenes": [["scan", "문서 스캔: 테두리 자동 인식 촬영"], ["compress", "목표 용량에 맞춘 PDF 용량 줄이기 결과(73% 줄었어요)"], ["compare", "줄이기 전후 화질 비교"], ["redact", "신분증 사본: 중요 정보 가리기와 제출용 문구"]]},
 "maejeum": {"name": "맺음", "what": "가족을 떠나보낸 유족이 부고부터 부의금 정리, 사망 후 할 일과 기일까지 챙기는 앱",
   "facts": "모바일 부고장 링크(빈소 지도·길찾기, 장례식장 전화, 계좌 복사, 카카오톡 미리보기), 장례식장 이름 검색으로 주소·전화 자동 입력, 부의금을 봉투 번호·상주별로 기록, 장례비 기록, 장례비를 뺀 부의금을 상주별로 나누는 정산, 부의금 명세서 PDF·엑셀, 감사 인사 문자와 모바일 감사장, 삼우제·49재 날짜 자동 계산, 사망신고·상속포기 등 사망 후 할 일 9가지를 남은 날짜로 보여 주고 방법·근거 법령 링크, 양력·음력 기일, 조문 가는 사람을 위한 조문 예절 카드 5장. 말투는 차분하고 담백하게",
   "extra": "반드시 해요체(~해요, ~돼요). 합니다체·습니다 금지. 슬픔·위로·마음·애도 같은 감정어 금지. 장례 첫날 상주가 할 일을 바로 처리한다는 실용 혜택만. 49재 라벨은 '날짜 자동 계산' 뜻으로",
   "stats": [["9", "사망 후 챙길 일"], ["49재", "날짜 자동 계산"], ["5", "조문 예절 카드"]],
   "scenes": [["web", "모바일 부고장: 빈소 지도·전화·계좌 복사"], ["money", "부의금 기록: 상주별·봉투 번호"], ["settle", "상주별 정산: 장례비 뺀 금액 나누기"], ["tasks", "사망 후 할 일: 사망신고·상속 기한 D-day"]]},
}
RULE = ("모든 문장은 해요체(~해요, ~돼요, ~있어요)로 끝내고 합니다체(~합니다·~습니다)는 절대 쓰지 마. 너는 한국 IT 서비스 소개 페이지(토스·당근·카카오 스타일) 카피라이터다. 혜택 중심, 짧고 또렷하게. 해요체. "
        "금지: 가격·무료·유료·광고·구독·결제·이용권·제한 언급, 개인정보·로그인·서버 언급, 감탄사·느낌표·이모지, 과장(최고·1위·완벽), 사실에 없는 기능. "
        "출력은 JSON 하나만, 설명 없이.")
def ask(slug):
    f = FACTS[slug]
    schema = {"hero_title": "두 줄, 줄 사이 ' / ', 줄마다 6~12자. 이 앱이 해결하는 순간이나 혜택",
              "hero_sub": "20~40자 한 문장",
              "stat_labels": [f"숫자 '{n}'에 붙일 짧은 라벨(4~10자), 뜻: {l}" for n, l in f["stats"]],
              "scenes": [{"screen": s, "shows": d, "kicker": "그 화면을 쓰는 상황 4~12자", "title": "혜택 제목 두 줄 ' / ', 줄마다 5~13자", "body": "30~60자 한두 문장"} for s, d in f["scenes"]],
              "why": [{"title": "이 앱을 고를 이유 6~12자", "body": "18~36자"} for _ in range(3)],
              "cta": "마지막 권유 한 줄 10~20자, 명령조 대신 해요체"}
    user = f"앱: {f['name']} — {f['what']}\n사실(이 범위 안에서만): {f['facts']}\n추가 규칙: {f.get('extra', '없음')}\n\n다음 구조를 채운 JSON:\n{json.dumps(schema, ensure_ascii=False, indent=1)}"
    body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": user}],
            "temperature": 0.5, "max_tokens": 2000, "chat_template_kwargs": {"enable_thinking": False}}
    r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900)
    t = json.load(r)["choices"][0]["message"]["content"]
    t = re.sub(r"^```(?:json)?|```$", "", t.strip(), flags=re.M).strip()
    j = json.loads(t)
    j["stats"] = [[n, lab] for (n, _), lab in zip(f["stats"], j.pop("stat_labels"))]
    for sc, (s, _) in zip(j["scenes"], f["scenes"]):
        sc["screen"] = s
        for k in list(sc):
            if k.replace(" ", "").endswith("kicker") and k != "kicker": sc["kicker"] = sc.pop(k)
    return j
out = json.load(open("marketing.json")) if os.path.exists("marketing.json") else {}
for slug in (sys.argv[1:] or FACTS):
    out[slug] = ask(slug); json.dump(out, open("marketing.json", "w"), ensure_ascii=False, indent=1)
    print(slug, json.dumps(out[slug], ensure_ascii=False, indent=1))
