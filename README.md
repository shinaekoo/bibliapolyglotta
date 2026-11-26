# Biblia Polyglotta · 다국어 대조 성경

라틴어 불가타 · KJV · 루터 1912 · 루이 스공 1910 · 개역한글 · 和合本 · 레이나-발레라 1909 · 리베두타 1927 · 러시아 시노달역 1876 · 口語訳 1955 · 알메이다(포르투갈어) · 앙 비블리아(타갈로그어 1905, 세부아노어 1917) · AYT(인도네시아어) · Baịbụlụ Nsọ(이그보어)를 히브리어·헬라어 원문과 함께 절 단위로 나란히 보는 성경 대조 도구입니다.

- 단어를 누르면 다른 언어에서 대응하는 단어가 강조됩니다.
- 라틴어 단어를 길게 누르거나(또는 두 번 탭) 낱말풀이 팝업이 열립니다: 기본형, 어간·어미와 각각의 뜻, 문법, 한국어 뜻, Whitaker 영어 풀이, 이 절에서 대응하는 원어의 STEPBible 사전 뜻.
- 지명(청록 밑줄)·인물(보라 점선)은 어느 언어에서든 한 번 더 누르면 정보 창이 열립니다: 지명은 성경 속 이름과 바뀐 내력, 오늘날 위치(구글 지도), 언급된 구절, 메모 / 인물은 가족, 이름, 나오는 구절, 메모.
- 신약이 구약을 인용한 자리에는 절 번호 밑에 따옴표 표시가 붙습니다. 누르면 인용한 구약 본문이 보고 있는 번역 그대로 펼쳐지고, 거꾸로 구약 쪽에서는 그 절을 인용한 신약 자리가 보입니다. 말이 그대로인 직접 인용인지, 신약이 칠십인역을 인용해 히브리어 본문과 다른 자리인지도 표시합니다.
- 전체 언어 검색, 장 이동, 도구 막대 접기.

## 구성

| 경로 | 내용 |
|---|---|
| `web/` | 앱 본체 (`index.html` + `data/*.json`). 브라우저로 바로 열 수 있음 |
| `tools/trim_site.py` | 설문 시험용 축소판 웹페이지(`site/`)를 만듦 — 창세기 1-3·여호수아 1-5·히브리서 전체·요한계시록 1-5만 담고 자료를 그 범위로 잘라 9MB로 줄임. 라틴어 낱말 음원은 `.github/workflows/lexdata.yml`의 `latin` 단계가 만든 `la_audio.tar.gz`를 끼워 넣음. `.github/workflows/testsite.yml`이 GitHub Pages에 올림 (`gh-pages` 브랜치) |
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
- 본문: Reina-Valera 1909, Riveduta 1927, 러시아 시노달역 1876, 口語訳 1955 — 퍼블릭 도메인 (seven1m/open-bibles). 리베두타의 아포스트로피 복원과 시노달역 장절 변환(히브리 체계 → KJV)은 BibleNLP/ebible 자료(eng.vrs)를 씀. 일본어 어절 나누기: janome(Apache 2.0, IPADIC). 포르투갈어 João Ferreira de Almeida(퍼블릭 도메인, open-bibles), 타갈로그어 Ang Biblia 1905·세부아노어 Ang Biblia 1917(퍼블릭 도메인, scrollmapper). 인도네시아어 Alkitab Yang Terbuka(© YLSA-AYT, CC BY-NC 4.0)와 이그보어 Baịbụlụ Nsọ(© Biblica, Inc. 2020, CC BY-SA 4.0)는 BibleNLP/ebible 말뭉치에서 받음 — 이 말뭉치는 히브리 장절 체계에 없는 KJV 절(장 끝 약 130절)이 빠져 있음. 만드는 순서: tools/build_texts.py → tools/verse_map.py → tools/align_original.py → tools/pack_texts.py
- 절 번호: 모든 번역을 KJV 번호에 맞춥니다. 라틴어 불가타는 그리스어 성경식으로 세고(불가타 9편 = 히브리 9+10편, 시편 표제가 한 절, 다니엘 3장에 세 젊은이의 노래 67절, 에스더 10장이 13절), 루터 1912는 히브리식으로 세어 시편 63편이 한 절씩 밀립니다. BibleNLP/ebible의 vul.vrs·eng.vrs로 빌드 때 본문 자체를 옮깁니다 — tools/verse_map.py. 단 vul.vrs는 우리가 쓰는 클레멘스 본문의 번호를 설명해 주지 않아(대부분의 책에서 영어와 같은 번호를 쓰는데, 클레멘스 본문은 요나 2장은 히브리식·요엘 3장은 KJV식으로 섞여 있음) 장마다 고유명사·숫자를 그 자리의 영어 절과 옮길 자리의 영어 절에 맞춰 보고 더 맞는 쪽을 택합니다. 시편·다니엘·에스더는 불가타 번호가 확실하고 맞춰 볼 이름이 없는 절이 많아 파일을 그대로 따릅니다. KJV에 자리가 없는 절(세 젊은이의 노래, 수산나, 벨, 에스더 추가분)은 그 장의 KJV 절 뒤에 ᴸ 표시로 붙습니다.
- 라틴어 형태 분석: William Whitaker's WORDS (모든 용도로 자유 사용 허용). 여러 분석 가운데 앞뒤 낱말과, 대응하는 히브리어·헬라어 단어의 문법(STEPBible)을 보고 고름 — tools/build_latin.py. 창세기 1장은 손으로 검토함. 낱말 풀이 창의 사전 내용은 Whitaker 영어 뜻과 STEPBible 원어 사전.
- 단어 대응: STEPBible이 히브리어·헬라어 단어마다 붙인 영어 번역어(TAHOT·TAGNT)를 KJV 단어와 맞추고(tools/orig_glosses.py → tools/align_original.py, NOSTRONG 모드), 성경 전체 통계(fast_align)로 보충해 KJV를 원어에 잇고, 다른 번역은 모두 이 연결과 원어를 거쳐 정렬함. 번역본의 스트롱 번호 태깅은 쓰지 않음.
- 화면 언어의 뜻: 원어·라틴어 단어마다 화면 언어의 번역(개역한글·KJV·루터·스공)에서 연결된 말을 성경 전체에서 세어 사전형으로 묶은 것(사랑하는·사랑하면 → 사랑하다, loved → love) — tools/meanings.py, data/ox*.json의 "m"과 data/lxL.json 여섯째 칸. tools/build_orig_lex.py와 tools/build_latin_meanings.py(build_latin.py 다음)가 만듦.
- 영어 동의어: Princeton WordNet 3.0 — STEPBible의 현대 영어 번역어와 KJV 단어를 맞출 때("emptiness" ~ "void"), 라틴어 분석에서 Whitaker 뜻과 원어 뜻을 비교할 때 씀(빌드 때만 쓰고 앱에는 넣지 않음). WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved. THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. 받은 곳: nltk_data(corpora/wordnet.zip). 환경 변수 WN_DIR.
- 일본어 기본형: UniDic (unidic-mecab, © UniDic Consortium, GPL/LGPL/BSD 중 BSD로 이용) — "愛して下さった" → 愛する처럼 어절의 기본형으로 같은 단어를 묶음(빌드 때만 씀). 받은 곳: siikamiika/unidic-mecab-translate의 lex.csv-original.gz. 환경 변수 UNIDIC_LEX. 둘 다 tools/lexres.py.

낱말 가르기: 글자·결합기호가 이어진 덩어리가 한 낱말이고, **글자 사이에 낀
엔대시(–)는 낱말 속 글자로 친다**. KJV가 고유명사를 엔대시로 잇고(Beth–el,
Beer–sheba, Abed–nego — 260종 775회), 러시아어 시노드역도 что–нибудь, из–за
처럼 쓰기 때문이다. 앱은 `web/index.html`의 `WORD`, 도구는 각 `toks()`가
같은 규칙을 쓴다. tools/merge_dash.py 는 이 규칙으로 바꾸면서 이미 쌓아 둔
al*.json 의 짝 번호를 옮긴 1회성 도구다(두 번 돌려도 결과는 같다).


클릭으로 연결하기: tools/make_editor.py --verses 목록.txt 제목 파일.html 로 여러 책에
흩어진 절만 모아 한 파일로 낼 수도 있다 (목록은 한 줄에 '책번호 장 절').
tools/make_editor.py <책번호> <장> [파일.html] 로 한 장짜리 편집기
HTML 을 만든다. 영어 낱말을 고르고 한국어 낱말을 눌러 켜고 끄면 tools/fix_links.py 에
그대로 붙일 항목이 아래에 쌓인다(#번호 자동). ← → 로 낱말을 옮겨 다닐 수 있고,
'대응 없음'은 words=[] 이 된다. 본문과 지금 짝을 HTML 안에 넣어 두므로 혼자 열린다.


표로 주고받기: tools/csv_links.py out 파일.csv --names 로 아직 연결이 없는 자리를
표로 내보내고(책·절·영어낱말·후보·본문), '대응한국어' 칸을 채워서
tools/csv_links.py in 파일.csv 로 들여오면 tools/fix_links.py 에 항목이 들어간다.
이어서 tools/fix_links.py 를 돌리면 반영된다. --names 를 떼면 이름이 아닌 자리까지 전부 낸다.


- 원어: 히브리어 구약·헬라어 신약 본문, 낱말 정보(Strong 번호·문법·음역), 간략 사전 — STEPBible.org (Tyndale House) TAHOT·TAGNT·TBESH·TBESG, CC BY 4.0. 히브리어 악센트 기호는 뺐고, 헬라어는 공인본문(Textus Receptus, 스크리브너 1894, KJV의 바탕 본문)을 씀. 만드는 순서: tools/build_original.py → tools/orig_glosses.py → tools/verse_map.py → NOSTRONG=… tools/align_original.py(모든 번역을 원문 기준으로 다시 정렬·교차 확인, OE_OUT으로 KJV↔원어 연결 저장) → tools/fix_jehovah.py → tools/fix_bridge.py(개역한글이 두 절을 한 절로 합쳐 놓은 곳을 다른 언어도 한 줄로 묶음) → tools/fix_pairs.py(뚜렷한 짝 — 제자/disciples, 아들/son 같은 것이 한쪽에 몰린 곳을 개수가 같을 때만 순서대로 나눠 줌) → tools/fix_namepairs.py(사람·지명 이름이 한 절에 두 번 이상 나와 짝이 한쪽에 몰린 곳을, 영어 쪽과 한국어 쪽 개수가 같을 때만 순서대로 나눠 줌 — pi.json·gi.json의 이름표를 씀) → tools/fix_enders.py(인용을 닫는 어미 …하고·하니라·하며·하라에 억지로 붙은 대응을 지움) → tools/fix_articles.py(관사 the·a·an 을 바로 뒤 낱말과 같은 한국어에 함께 걺 — 한국어에 관사가 없어 the substance=실상이요 처럼 한 낱말이 되므로. 더하기만 하고 기존 짝은 건드리지 않는다) → tools/fix_links.py(손으로 고친 낱말 연결) → tools/build_latin.py(라틴어 분석) → tools/build_concordance.py → tools/build_orig_lex.py STEP OE_JSON SUBS_JSON(원어 사전·용례·번역어 통계, data/ox0~3.json) → tools/build_xref.py(구약 인용 상호참조, data/xref.json)
- 인물: STEPBible.org TIPNR (Tyndale House), CC BY 4.0 — 가족 관계, 이름, 나오는 구절, 설명(영어). 번역별 이름은 본문 연결과 발음 비교로 찾음. 만드는 스크립트: tools/build_persons.py (build_orig_lex.py 다음)
- 성경 사전(인물·지명): Easton's Bible Dictionary (1897), Smith's Bible Dictionary (1863), Hastings (1909), Hitchcock's Bible Names (1869) — 모두 퍼블릭 도메인(CCEL), 정리된 데이터는 NEUU bible-dictionary-dataset (CC BY 4.0). 어느 항목이 어느 인물·지명인지는 인용 구절이 겹치는 정도로 골랐음. 만드는 스크립트: tools/build_dict.py
- 지도: Natural Earth (퍼블릭 도메인) 해안선·호수·강을 성경 지역만 잘라 앱에 넣음(data/map.json, 인터넷 없이 표시). 만드는 스크립트: tools/build_map.py
- 지명: STEPBible.org TIPNR (CC BY 4.0) + 오늘날 위치 OpenBible.info. 만드는 스크립트: tools/build_geo.py
- 지명·위치: OpenBible.info Bible Geocoding Data — CC BY 4.0 (https://www.openbible.info/geo/). 지명 내력 설명은 앱 제작 중 정리한 것으로 검토 중입니다.
- 구약 인용: 바깥에서 받아 온 자료가 아니라 "히브리서 1:5가 시편 2:7을 인용한다"는 사실을 tools/build_xref.py에 손으로 적어 둔 목록입니다. 따로 따를 라이선스가 없습니다. 지금은 히브리서만 들어 있고(36곳), 절 번호만 믿지 않도록 신약·구약 양쪽에 그 자리에 반드시 있어야 하는 영어 낱말을 함께 적어 빌드 때마다 본문과 대조합니다 — 못 찾으면 빌드가 멈춥니다. 칠십인역을 인용해 히브리어 본문과 달라진 자리의 설명은 앱 제작 중 정리한 것으로, 지금은 한국어로만 보여 줍니다.

### tools/survey_word.py
영어 낱말 하나를 한국어와 맞댄 자리가 빈 곳을 전수 조사한다.

    python3 tools/survey_word.py "Went,went"

쉼표로 여러 꼴을 함께 센다(대·소문자는 따로 세므로 둘 다 적는다).
결과 절 목록은 /tmp/wrows.json 에 남으니 make_editor.py --verses 로 바로 넘길 수 있다.
KJV 는 놋을 brass, 철을 iron 으로 옮긴다(bronze·steel 은 현대 역본 용어라 거의 없다).

### 편집기 본문 칸
make_editor.py 가 만드는 편집기는 낱말 조각 위에 **본문 전체**를 영어·한국어
문장으로 보여 준다. 고른 영어 낱말은 파랗게, 그 짝 한국어는 초록으로 물들고,
아무 짝도 없는 낱말은 빨간 물결밑줄이 붙는다.

### 편집기 '전부 지우기'
confirm() 은 브라우저가 "추가 대화상자 차단"을 걸면 늘 false 를 돌려주므로
쓰지 않는다. 두 번 눌러야 지워진다 — 한 번 누르면 '정말? 다시 누르기'로
바뀌고, 4초 안에 다시 누르면 지운다.

## 오류 신고 받기

**지금은 꺼져 있다.** `web/index.html` 맨 위 쪽의 스위치 셋으로 켠다.

    const SHOW_SEND=false, SHOW_REPORT=false;
    const DONATE="";

| 스위치 | 켜면 보이는 것 |
|---|---|
| `SHOW_REPORT` | 낱말 신고 깃발과 설정의 '오류 신고 모음' (기기에만 쌓인다) |
| `SHOW_SEND` | 깃허브 오류 신고 · 의견 보내기 · 후원 단추 |
| `DONATE` | 후원 주소. 비어 있으면 '준비 중'이라고만 알린다 |

받는 곳(도메인·Worker·구글 폼)이 생기면 그때 켠다. 코드는 그대로 두었으니
스위치만 바꾸면 살아난다. 아래는 켰을 때의 움직임이다.


앱은 네트워크를 쓰지 않는다(WebView 가 번들 자산만 읽는다). 그래서 신고도
**앱이 보내지 않고** 사용자의 브라우저나 손으로 가져간다.

1. 본문에서 낱말을 누르면 오른쪽 아래에 **⚑ 신고** 깃발이 떠오른다.
2. 깃발을 누르면 갈래(연결 틀림·연결 없음·본문 오자·낱말풀이·그 밖)를
   고르고 한 줄 적어 **담는다**. 바로 보내지 않고 기기에 쌓인다.
3. 설정 → **오류 신고 모음**에서 모두 복사하거나 깃허브 이슈로 보낸다.

담을 때 책·장·절, 언어, 낱말 자리와 `#n`, 영어 쪽 짝, 앱 판을 자동으로
적는다. 그래서 받은 글이 바로 교정 자료가 된다. 같은 자리·같은 갈래는
한 번만 쌓이고, 최대 300건까지 둔다.

앱이 스스로 적는 것도 있다 — `window.onerror` 와 거절된 promise 를 '멈춤'
갈래로 담는다(같은 오류는 한 번만). 사용자가 신고하지 않는 오류를 잡는다.

### tools/inbox.py
모인 신고를 읽어 점검하고 편집기로 넘긴다.

    python3 tools/inbox.py 신고.txt --lst /tmp/inbox.lst
    python3 tools/make_editor.py --verses /tmp/inbox.lst "신고 교정" /tmp/kodo-inbox.html

겹친 신고를 묶고, 갈래·판·책별로 세고, **지금 자료에서 그 낱말이 이미
걸려 있는지**를 '고쳐짐?' 칸에 보여 준다 — 옛 판에서 온 신고를 솎아낸다.
`--fix` 를 주면 fix_links 뼈대까지 찍는다.

앱 판 번호는 build.yml 이 `__BPVER__` 자리에 갈아 넣는다. 갈아 넣히지
않으면 'dev' 로 보인다.

## 자체점검 (tools/selfcheck.py)

밀어 올릴 때마다 CI(.github/workflows/selfcheck.yml)가 돌린다.
숫자를 `tools/selfcheck.json`(기준선)과 견주어 **나빠지면 알린다**.

    python3 tools/selfcheck.py           # 점검하고 기준선과 견준다
    python3 tools/selfcheck.py --save    # 지금 숫자를 기준선으로 삼는다

돌려주는 값: 0 이상 없음 · 1 품질이 나빠짐(사람이 봐야 함) · 2 자료가 깨짐(반드시 고침)

깨짐은 반드시 0이어야 한다 — `bad_parse`(파일을 못 읽음),
`bad_shape`(장·절 수가 **영어 본문**과 어긋남), `bad_range`(짝 번호가 낱말 수를 넘음).
한국어 절 수는 견주지 않는다 — 요삼 1:15, 계 12:18 처럼 개역한글에만 있는
절이 있어 번역본 차이로 어긋난다.

품질은 늘거나 줄기를 지켜본다 — `ko_empty`(짝 없는 한국어 낱말),
`en_zero`(한 번도 안 걸린 영어 낱말 가지), `low30`(맞댄 비율 30% 이하 절),
`twin`(같은 낱말 한 벌이 둘을 쥐고 다른 벌이 빈 곳), `neg`(부정어 뭉침).
교정이 맞아서 숫자가 흔들린 것이면 `--save` 로 기준선을 다시 잡는다.

### 파일 이름에 주의
al 파일은 **두 자리**다 — `web/data/al00.json`, `text/ko00.json`.
`al%d.json` 으로 찾으면 책 0~9(창세기~열왕기하)를 소리 없이 건너뛴다.
도구를 새로 만들 때는 반드시 `%02d` 를 쓸 것. 자체점검이 이 구멍을
`bad_parse` 로 잡아낸다.
