# 원어 대조 성경 · Biblia Originalis

개역한글 · KJV · 원어(구약 히브리어, 신약 헬라어)를 절 단위로 나란히 보는 성경 대조 앱입니다.

## 기능

- **동어 대조**: 어느 본문의 단어든 누르면 같은 원어에서 나온 말이 세 본문에 금색으로 표시됩니다. 같은 장에서 같은 원어가 다시 나오면 금색 밑줄이 그어집니다.
- **원어 사전**: 단어를 한 번 더 누르거나(또는 길게 누르기·오른쪽 클릭) 열립니다.
  - 원어 낱말과 음역, 히브리어 접두·접미사 구성(전치사·관사·대명 접미사 등)
  - 기본형, 스트롱 번호, 문법(히브리어 동사 어간·형태, 헬라어 시제·태·법·격 등)과 한국어 풀이
  - 이 절에서 대응하는 개역한글·KJV 말
  - 개역한글과 KJV가 이 원어를 성경 전체에서 어떻게 옮겼는지(횟수)
  - 영문 뜻풀이(구약 BDB 간추림, 신약 Abbott-Smith) — 본문 참조를 누르면 그 절로 이동
- **같은 원어가 쓰인 곳**: 책별 횟수 → 책을 누르면 절 목록(개역한글 본문에 대응 단어 강조) → 누르면 그 절로 이동해 단어를 표시합니다.
- **메모**: 절마다 본문 묵상, 사전 안에서 원어 낱말마다 단어 묵상. 메모 탭에서 시간순·본문순·단어순으로 보고, 설정에서 모두 복사(백업).
- **검색**: 개역한글·KJV·원어 본문(원어는 모음·악센트 무시), 스트롱 번호(H7225, G3056)로 사전 바로 열기.
- 원어 음역 보기, 글자 크기, 본문 표시 선택, 도구 막대 접기.

## 구성

| 경로 | 내용 |
|---|---|
| `original/web/` | 앱 본체 (`index.html` + `data/*.json`). 브라우저로 바로 열 수 있음 |
| `original/android/` | 안드로이드 앱 (WebView, 패키지 `kr.bible.originalis`). `original/web`을 그대로 assets로 묶음 |
| `.github/workflows/build-original.yml` | 푸시하면 APK·AAB 자동 빌드 → Releases의 **originalis-latest** |
| `tools/original/` | 자료를 만드는 스크립트 |

`data/` 파일: `ko##`(개역한글), `en##`(KJV), `or##`(원어 낱말: 본문·음역·스트롱 번호·문법), `al##`(개역한글·KJV 단어 ↔ 원어 낱말 연결), `lx0–15`(사전), `cc0–15`(같은 원어가 쓰인 곳).

## 자료 다시 만들기

```sh
# 1) 원본 자료
git clone --depth 1 https://github.com/STEPBible/STEPBible-Data      # TAHOT, TAGNT, TBESH, TBESG
git clone --depth 1 https://github.com/kaiserlik/kjv                 # 스트롱 번호가 붙은 KJV
git clone --depth 1 https://github.com/clab/fast_align && (cd fast_align && mkdir build && cd build && cmake .. && make)

# 2) 원어 본문 (KJV 장절 기준, 히브리어 칸틸레이션 제거, 헬라어는 공인본문 읽기)
python3 tools/original/parse_step.py STEPBible-Data orig.json

# 3) 연결·사전·용례 (개역한글·KJV는 web/data에서 가져옴)
python3 tools/original/build_original.py orig.json web/data kjv STEPBible-Data fast_align/build original/web/data

# 4) 아이콘 (바꿀 때만)
python3 tools/original/make_icons.py original/android/app/src/main/res
```

## 출처와 라이선스

- 개역한글(1961), KJV(1769): 퍼블릭 도메인.
- 히브리어 구약(레닌그라드 사본, Qere 반영)·헬라어 신약(스크리브너 공인본문 1894)과 낱말 분석, 사전(TBESH·TBESG): STEPBible.org, Tyndale House Cambridge — **CC BY 4.0** (출처 표시하면 상업적 이용 가능).
- KJV 스트롱 번호 태깅: kaiserlik/kjv (퍼블릭 도메인 본문).
- 개역한글 ↔ 원어 단어 연결은 fast_align으로 통계적으로 정렬한 것이라 가끔 틀립니다.
