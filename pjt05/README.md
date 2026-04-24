# 스켈레톤 코드

- pjt04 의 정답 코드입니다.
- 심화 기능인 [LLM을 활용한 부적절한 컨텐츠 필터링] 기능은 모두 주석처리 되어 있습니다.
  - `.env` 생성 후 `MODE`에서 `OPENAI 또는 UPSTAGE` 를 선택하고, `OPENAI_API_KEY` 혹은 `UPSTAGE_API_KEY` 를 설정
  - `[심화] LLM 부적절 댓글 필터링` 주석을 모두 검색 후 관련 코드를 주석해제하시면 정상 동작 됩니다.
    - `llm.py` 전체
    - `settings.py` API KEY load 부분
    - `views.py` 의 관련 코드
  