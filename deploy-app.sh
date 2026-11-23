#!/bin/bash
# importants-app.com 배포(2026-11-19): 앱 소개(apps-site) + 도구·날짜·정보 글(main-site SITE_TARGET=app)을 한 폴더로 합쳐 Worker 정적 자산으로 올린다.
# 앱 소개 파일이 이름이 겹치면 이긴다. 회사용 페이지(홈·about·contact·privacy·blogs)와 옛 도메인 전용 파일은 넣지 않는다.
set -euo pipefail
cd "$(dirname "$0")"
MAIN=../main-site
# 파이썬 3.12 이상 + Pillow 가 필요하다(맥 기본 python3 은 3.9 라 안 됨). 없으면 uv 로 .venv 를 만든다(2026-11-23, 판 카드 #102).
PY=.venv/bin/python
if ! "$PY" -c 'import PIL' 2>/dev/null; then
  uv venv -q --python 3.13 .venv && uv pip install -q --python "$PY" pillow
fi
[ -d "$MAIN/node_modules" ] || (cd "$MAIN" && npm ci)
TARGET=new "$PY" tools/build.py >/dev/null
(cd "$MAIN" && SITE_TARGET=app npm run build >/dev/null)
for d in tools days blog _astro c g s game og apps work; do
  [ -d "$MAIN/dist-app/$d" ] && rsync -a --ignore-existing "$MAIN/dist-app/$d" dist-app/
done
cp "$MAIN/dist-app/rss.xml" dist-app/blog-rss.xml   # 앱 소개 rss.xml 과 겹치지 않게
cp "$MAIN/dist-app/ads.txt" dist-app/ads.txt         # 애드센스(새 도메인 승인용)
# 사이트맵: 앱 소개 + 도구·날짜·글
{
  echo '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  echo "<url><loc>https://importants-app.com/</loc></url>"
  (cd dist-app && find . -name index.html ! -path './review/*' ! -path './c/*' ! -path './g/*' ! -path './s/*' ! -path './game/*' | sed 's|^\./||; s|index\.html$||' | grep -v '^$' | sort | sed 's|^|<url><loc>https://importants-app.com/|; s|$|</loc></url>|')
  echo '</urlset>'
} > dist-app/sitemap.xml
echo "pages: $(grep -c '<loc>' dist-app/sitemap.xml)"
[ -n "${DRY:-}" ] && exit 0
npx wrangler deploy
