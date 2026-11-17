#!/usr/bin/env python3
"""잔상 소개 페이지 문구 후보(로컬 Gemma). 기능 구간 문장은 스토어 스크린샷 확정 문구(app/Afterimage/assets/store-v14/copy-ko.json)를 그대로 쓰고,
여기서는 첫 화면 한 줄·안내 카드·마무리·검색 설명만 후보를 받는다. 출력 _afterimage_cands.json"""
import json, re, urllib.request, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
_src = open("gen_marketing.py").read(); RULE = eval(_src[_src.index("RULE = (") + 7:_src.index("\n", _src.index("출력은 JSON 하나만")) ])  # 같은 규칙(모듈을 import 하면 전체 생성이 돌아서 문자열만 가져옴)
FACT = ("앱: 잔상 - 타임캡슐, 사진일기. 사진을 찍으면 바로 볼 수 없고, 내가 정한 날(내일·일주일·한 달·1년, 3년·5년·날짜 직접 지정)에 열리는 사진 타임캡슐 앱. "
        "찍을 때 한 줄을 남기면 열리는 날 편지처럼 먼저 보이고, 봉투에서 폴라로이드 사진이 올라오며 흐린 사진이 선명해짐(현상). "
        "기다리는 동안 흐린 폴라로이드와 남은 날(D-day), 홈 화면 위젯. 열린 사진에 일기 덧붙이기. 오늘의 질문. 같은 날의 잔상(1년 전·2년 전 오늘). 이달의 기록. "
        "필름 한 통(24장을 채우면 한꺼번에 현상). Face ID 앱 잠금, iCloud 자동 백업, 전체 내보내기. 사진은 기기 안에 보관.")
ASK = {"hero_sub": "첫 화면 큰 제목 아래 설명 한 문장 30~50자 후보 4개",
       "note_title": "안내 카드 제목 4~10자 후보 3개(예: 이용 시 참고)",
       "note": "안내 카드 본문 2문장 후보 3개: 사진은 기기 안에 보관된다는 점, 앱을 지우기 전 백업·내보내기를 해 두면 좋다는 점을 긍정형으로",
       "cta": "마지막 권유 한 줄 10~20자 후보 4개",
       "seo_description": "검색 결과 설명 60~90자 후보 3개(기능 사실 위주)"}
user = f"{FACT}\n추가 규칙: 긍정형, '마음'·'설렘' 같은 감정어 남발 금지, 사실에 있는 기능만.\n\n다음 키마다 후보 배열을 담은 JSON:\n{json.dumps(ASK, ensure_ascii=False, indent=1)}"
body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": user}],
        "temperature": 0.6, "max_tokens": 2000, "chat_template_kwargs": {"enable_thinking": False}}
r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900)
t = re.sub(r"^```(?:json)?|```$", "", json.load(r)["choices"][0]["message"]["content"].strip(), flags=re.M).strip()
j = json.loads(t); json.dump(j, open("_afterimage_cands.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(j, ensure_ascii=False, indent=1))
