# """
# OpenAI/Upstage Chat Completions로 부적절한 텍스트 검사.
# 게시글 제목/내용 검사에 사용. 프롬프트에 한국어 욕설 필터링 지시 포함.
# """
# from django.conf import settings
# from openai import OpenAI

# SYSTEM_PROMPT = """당신은 한국어 커뮤니티의 '부적절 표현' 판별기입니다.
# 아래 규칙으로 사용자 입력(한 문장 또는 여러 문장)을 검사하세요.

# [판정 원칙]
# 1) 아래 항목 중 하나라도 해당하면 반드시 부적절(YES)입니다.
# 2) 맥락상 상대를 직접 공격/비하/모욕하면, 전형적 욕설이 아니어도 YES입니다.
# 3) 우회 표현(오타, 띄어쓰기 분리, 초성/자모 분해, 비슷한 발음 치환)도 원형으로 간주해 YES 처리합니다.

# [YES(부적절)로 판단할 내용]
# - 욕설/비속어/모욕/인신공격: 예) "멍청아", "나쁜 새끼야", "한심한 놈", "병X", "ㅂㅅ", "ㅅㅂ" 등
# - 혐오/차별/비하 발언: 성별, 지역, 인종, 장애, 종교, 직업군 등에 대한 멸시/배제
# - 괴롭힘/협박/위협/폭력 조장: 해치겠다는 표현, 위해 유도, 자해·타해 선동
# - 성적 대상화/성희롱/음란성 표현
# - 악의적 비방/모욕적 조롱/지속적 괴롭힘 맥락

# [우회 표현 처리 규칙]
# - 욕설 사이에 공백/특수문자 삽입: 예) "ㅅ ㅂ", "ㅂ-ㅅ", "새.끼"
# - 초성/자모/은어/오타/변형: 예) "ㅁㅊ", "ㅂㅅ", "새기", "시@발" 등
# - 반복 문자나 늘임표로 완화한 형태도 동일하게 간주

# [NO(적절) 예시]
# - 금융 자산, 투자 의견, 시장 분석, 일반 질문, 중립적 비판
# - 감정 표현이 있어도 타인 모욕/혐오/폭력/성적 괴롭힘이 없는 경우

# 출력 규칙:
# - 부적절하면 YES
# - 적절하면 NO
# - 반드시 YES 또는 NO만 단독으로 출력 (설명/부연/구두점/이모지 금지)"""


# def _build_llm_client():
#     """
#     MODE 값에 따라 LLM 클라이언트/모델을 구성한다.
#     - OPENAI: OpenAI API 사용
#     - UPSTAGE: Upstage OpenAI-compatible endpoint 사용
#     """
#     mode = (getattr(settings, "MODE", "OPENAI") or "OPENAI").strip().upper()

#     if mode == "UPSTAGE":
#         api_key = (getattr(settings, "UPSTAGE_API_KEY", None) or "").strip()
#         if not api_key:
#             print("UPSTAGE_API_KEY가 없습니다.")
#             return None, None
#         client = OpenAI(
#             api_key=api_key,
#             base_url="https://api.upstage.ai/v1/solar",
#         )
#         return client, "solar-mini"

#     # 기본값: OPENAI
#     api_key = (getattr(settings, "OPENAI_API_KEY", None) or "").strip()
#     if not api_key:
#         print("OPENAI_APIK_KEY(또는 OPENAI_API_KEY)가 없습니다.")
#         return None, None
#     client = OpenAI(api_key=api_key)
#     return client, "gpt-5-nano"


# def is_inappropriate(text: str) -> bool:
#     """
#     텍스트에 부적절한 내용이 있으면 True 반환.
#     MODE(OPENAI/UPSTAGE)에 맞는 API 키가 있을 때만 Chat Completions로 판별.
#     """
#     if not text or not text.strip():
#         return False

#     client, model = _build_llm_client()
#     if not client:
#         return False

#     stripped = text.strip()
#     try:
#         resp = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": stripped},
#             ],
#         )
#         answer = (resp.choices[0].message.content or "").strip().upper()
#         print(f"부적절 단어 검사 결과 = {answer}")
#         return "YES" in answer
#     except Exception as e:
#         print(f"[LLM 부적절 검사 실패] {type(e).__name__}: {e}")
#         return False
