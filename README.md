# Biblia Polyglotta · 다국어 대조 성경

라틴어 불가타 · KJV · 루터 1912 · 루이 스공 1910 · 개역한글 · 和合本 · 레이나-발레라 1909 · 리베두타 1927 · 러시아 시노달역 1876 · 口語訳 1955 · 알메이다(포르투갈어) · 앙 비블리아(타갈로그어 1905, 세부아노어 1917) · AYT(인도네시아어) · Baịbụlụ Nsọ(이그보어)를 히브리어·헬라어 원문과 함께 절 단위로 나란히 보는 성경 대조 도구입니다.

- 단어를 누르면 다른 언어에서 대응하는 단어가 강조됩니다.
- 라틴어 단어를 길게 누르거나(또는 두 번 탭) 낱말풀이 팝업이 열립니다: 기본형, 어간·어미와 각각의 뜻, 문법, 한국어 뜻, Whitaker 영어 풀이, Lewis & Short 발췌.
- 지명(청록 밑줄)·인물(보라 점선)은 어느 언어에서든 한 번 더 누르면 정보 창이 열립니다: 지명은 성경 속 이름과 바뀐 내력, 오늘날 위치(구글 지도), 언급된 구절, 메모 / 인물은 가족, 이름, 나오는 구절, 메모.
- 전체 언어 검색, 장 이동, 도구 막대 접기.

## 구성

| 경로 | 내용 |
|---|---|
| `web/` | 앱 본체 (`index.html` + `data/*.json`). 브라우저로 바로 열 수 있음 |
| `text/` | 번역 본문 원본(언어·책마다 한 파일). `tools/pack_texts.py`가 언어마다 11개 묶음(`web/data/{언어}_{묶음}.json`)으로 합쳐 앱에 넣음 |
| `android/` | 안드로이드 앱 (WebView). `web/`을 그대로 assets로 묶음 |
| `.github/workflows/build.yml` | 푸시하면 APK·AAB 자동 빌드 |
| `tools/analysis/` | 라틴어 형태 분석·정렬 데이터를 만든 스크립트 (참고용) |

## 자동 빌드

- `main`에 푸시 → Releases의 **latest**(사전 릴리스)에 APK·AAB가 올라옵니다.
- `v1.1.0` 같은 태그를 푸시 → 해당 버전 릴리스가 만들어집니다.
- Actions 탭 → *Android build* → *Run workflow*로 수동 실행도 됩니다.

서명을 위해 저장소 **Settings → Secrets and variables → Actions**에 다음 비밀값이 필요합니다. 없으면 디버그 서명 APK만 만들어집니다.

| 이름 | 값 |
|---|---|
| `KEYSTORE_BASE64` | 서명 키(.jks)를 base64로 인코딩한 문자열 |
| `KEYSTORE_PASSWORD` | 키스토어 비밀번호 |
| `KEY_ALIAS` | 키 별칭 |
| `KEY_PASSWORD` | 키 비밀번호 (키스토어 비밀번호와 같으면 생략 가능) |

서명 키 파일(.jks)은 절대 저장소에 커밋하지 마세요 (`.gitignore`에 포함됨).

## 출처와 라이선스

- 본문: Clementine Vulgate, KJV, Luther 1912, Segond 1910, 개역한글, 和合本 — 퍼블릭 도메인 (scrollmapper/bible_databases, Beblia).
- 본문: Reina-Valera 1909(스트롱 번호 태깅 포함), Riveduta 1927, 러시아 시노달역 1876, 口語訳 1955 — 퍼블릭 도메인 (seven1m/open-bibles). 리베두타의 아포스트로피 복원과 시노달역 장절 변환(히브리 체계 → KJV)은 BibleNLP/ebible 자료(eng.vrs)를 씀. 일본어 어절 나누기: janome(Apache 2.0, IPADIC). 포르투갈어 João Ferreira de Almeida(퍼블릭 도메인, open-bibles), 타갈로그어 Ang Biblia 1905·세부아노어 Ang Biblia 1917(퍼블릭 도메인, scrollmapper). 인도네시아어 Alkitab Yang Terbuka(© YLSA-AYT, CC BY-NC 4.0)와 이그보어 Baịbụlụ Nsọ(© Biblica, Inc. 2020, CC BY-SA 4.0)는 BibleNLP/ebible 말뭉치에서 받음 — 이 말뭉치는 히브리 장절 체계에 없는 KJV 절(장 끝 약 130절)이 빠져 있음. 만드는 순서: tools/build_texts.py → tools/align_original.py → tools/pack_texts.py
- 라틴어 형태 분석: William Whitaker's WORDS (자유 사용 허용).
- 신약 형태 주석: PROIEL Treebank — CC BY-NC-SA 3.0 (비상업적 이용).
- 단어 대응: KJV 스트롱 번호 태깅(kaiserlik/kjv, KJV 본문 퍼블릭 도메인)과 fast_align으로 원어 번호를 거쳐 정렬.
- 사전: Lewis & Short, *A Latin Dictionary* — Perseus Digital Library, CC BY-SA.
- 원어: 히브리어 구약·헬라어 신약 본문, 낱말 정보(Strong 번호·문법·음역), 간략 사전 — STEPBible.org (Tyndale House) TAHOT·TAGNT·TBESH·TBESG, CC BY 4.0. 히브리어 악센트 기호는 뺐고, 헬라어는 공인본문(Textus Receptus, 스크리브너 1894, KJV의 바탕 본문)을 씀. 만드는 순서: tools/build_original.py → tools/align_original.py(모든 번역을 원문 기준으로 다시 정렬·교차 확인) → tools/fix_jehovah.py → tools/build_orig_lex.py(원어 사전·용례·번역어 통계, data/ox0~3.json)
- 인물: STEPBible.org TIPNR (Tyndale House), CC BY 4.0 — 가족 관계, 이름, 나오는 구절, 설명(영어). 번역별 이름은 본문 연결과 발음 비교로 찾음. 만드는 스크립트: tools/build_persons.py (build_orig_lex.py 다음)
- 성경 사전(인물·지명): Easton's Bible Dictionary (1897), Smith's Bible Dictionary (1863), Hastings (1909), Hitchcock's Bible Names (1869) — 모두 퍼블릭 도메인(CCEL), 정리된 데이터는 NEUU bible-dictionary-dataset (CC BY 4.0). 어느 항목이 어느 인물·지명인지는 인용 구절이 겹치는 정도로 골랐음. 만드는 스크립트: tools/build_dict.py
- 지도: Natural Earth (퍼블릭 도메인) 해안선·호수·강을 성경 지역만 잘라 앱에 넣음(data/map.json, 인터넷 없이 표시). 만드는 스크립트: tools/build_map.py
- 지명: STEPBible.org TIPNR (CC BY 4.0) + 오늘날 위치 OpenBible.info. 만드는 스크립트: tools/build_geo.py
- 지명·위치: OpenBible.info Bible Geocoding Data — CC BY 4.0 (https://www.openbible.info/geo/). 지명 내력 설명은 앱 제작 중 정리한 것으로 검토 중입니다.

PROIEL 데이터가 비상업 라이선스이므로 이 앱도 비상업적으로 배포해야 합니다.
