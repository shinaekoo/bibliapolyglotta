# 빌드 때 쓰는 사전 자료

`.github/workflows/lexdata.yml`이 만든다. 앱에는 들어가지 않는다.

| 파일 | 자료 | 라이선스 |
|---|---|---|
| `ko_parse.json.gz` | mecab-ko-dic으로 분석한 한국어 어형 → 형태소 목록. 이 저장소 `text/ko*.json`에 나오는 어형만. 기본형을 정하는 일은 `tools/` 쪽에서 한다. | Apache License 2.0 (mecab-ko-dic, Yongwoon Lee·Yungho Yu) |
| `oewn.json.gz` | Open English WordNet의 낱말 → 뜻묶음 번호 | CC BY 4.0 (Open English WordNet) |

사전 자체는 담지 않는다. 받아서 우리 본문에 필요한 만큼만 뽑은 결과다.
