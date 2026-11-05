#!/usr/bin/env python3
"""검색 결과용 meta description(앱별) — 로컬 LLM(Gemma). 키워드·사실은 seo.json·marketing.json에서. 결과는 seo.json의 description."""
import json, urllib.request, re, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
seo, M = json.load(open("seo.json")), json.load(open("marketing.json"))
RULE = ("모든 문장 끝은 반드시 ~해요/~돼요/~있어요. 반말(~해.)·합니다체 금지. 검색 결과 설명문(meta description) 작성자. 80~110자 한 덩어리 두 문장. "
        "앱이 해 주는 일을 구체적으로, 주어진 키워드 중 2~3개를 자연스럽게 포함. 가격·무료·광고·과장·느낌표·이모지 금지. 출력은 설명문만.")
for slug, v in seo.items():
    if sys.argv[1:] and slug not in sys.argv[1:]: continue
    m = M[slug]; facts = m["hero_sub"] + " / " + " / ".join(s["body"] for s in m["scenes"])
    user = f"앱 이름: {v['store_name']}\n키워드: {', '.join(v['keywords'])}\n기능 사실: {facts}"
    body = {"model": "mlx-community/gemma-4-26b-a4b-it-4bit", "temperature": 0.4, "max_tokens": 300, "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content": RULE}, {"role": "user", "content": user}]}
    t = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8088/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=900))["choices"][0]["message"]["content"].strip().strip('"')
    v["description"] = re.sub(r"\s+", " ", t); print(slug, len(v["description"]), v["description"])
json.dump(seo, open("seo.json", "w"), ensure_ascii=False, indent=1)
