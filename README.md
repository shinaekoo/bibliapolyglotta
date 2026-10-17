# Biblia Polyglotta · 다국어 대조 성경

라틴어 불가타 · KJV · 루터 1912 · 루이 스공 1910 · 개역한글 · 和合本을 절 단위로 나란히 보는 성경 대조 도구입니다.

- 단어를 누르면 다른 언어에서 대응하는 단어가 강조됩니다.
- 라틴어 단어를 길게 누르거나(또는 두 번 탭) 낱말풀이 팝업이 열립니다: 기본형, 어간·어미와 각각의 뜻, 문법, 한국어 뜻, Whitaker 영어 풀이, Lewis & Short 발췌.
- 전체 언어 검색, 장 이동, 도구 막대 접기.

## 구성

| 경로 | 내용 |
|---|---|
| `web/` | 앱 본체 (`index.html` + `data/*.json`). 브라우저로 바로 열 수 있음 |
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
- 라틴어 형태 분석: William Whitaker's WORDS (자유 사용 허용).
- 신약 형태 주석: PROIEL Treebank — CC BY-NC-SA 3.0 (비상업적 이용).
- 사전: Lewis & Short, *A Latin Dictionary* — Perseus Digital Library, CC BY-SA.

PROIEL 데이터가 비상업 라이선스이므로 이 앱도 비상업적으로 배포해야 합니다.
