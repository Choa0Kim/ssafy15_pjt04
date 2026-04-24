"""
OpenAI/Upstage Chat Completions로 부적절한 텍스트 검사.
게시글 제목/내용 검사에 사용. 프롬프트에 한국어 욕설 필터링 지시 포함.
"""
from django.conf import settings
from openai import OpenAI

SYSTEM_PROMPT = """당신은 한국어 커뮤니티의 '부적절 표현' 판별기입니다.
아래 규칙으로 사용자 입력(한 문장 또는 여러 문장)을 검사하세요.

[판정 원칙]
1) 아래 항목 중 하나라도 해당하면 반드시 부적절(YES)입니다.
2) 맥락상 상대를 직접 공격/비하/모욕하면, 전형적 욕설이 아니어도 YES입니다.
3) 우회 표현(오타, 띄어쓰기 분리, 초성/자모 분해, 비슷한 발음 치환)도 원형으로 간주해 YES 처리합니다.

[YES(부적절)로 판단할 내용]
- 욕설/비속어/모욕/인신공격: 예) "멍청아", "나쁜 새끼야", "한심한 놈", "병X", "ㅂㅅ", "ㅅㅂ" 등
- 혐오/차별/비하 발언: 성별, 지역, 인종, 장애, 종교, 직업군 등에 대한 멸시/배제
- 괴롭힘/협박/위협/폭력 조장: 해치겠다는 표현, 위해 유도, 자해·타해 선동
- 성적 대상화/성희롱/음란성 표현
- 악의적 비방/모욕적 조롱/지속적 괴롭힘 맥락

[우회 표현 처리 규칙]
- 욕설 사이에 공백/특수문자 삽입: 예) "ㅅ ㅂ", "ㅂ-ㅅ", "새.끼"
- 초성/자모/은어/오타/변형: 예) "ㅁㅊ", "ㅂㅅ", "새기", "시@발" 등
- 반복 문자나 늘임표로 완화한 형태도 동일하게 간주

[NO(적절) 예시]
- 금융 자산, 투자 의견, 시장 분석, 일반 질문, 중립적 비판
- 감정 표현이 있어도 타인 모욕/혐오/폭력/성적 괴롭힘이 없는 경우

출력 규칙:
- 부적절하면 YES
- 적절하면 NO
- 반드시 YES 또는 NO만 단독으로 출력 (설명/부연/구두점/이모지 금지)"""


def _build_llm_client():
    """
    MODE 값에 따라 LLM 클라이언트/모델을 구성한다.
    - OPENAI: OpenAI API 사용
    - UPSTAGE: Upstage OpenAI-compatible endpoint 사용
    """
    mode = (getattr(settings, "MODE", "OPENAI") or "OPENAI").strip().upper()

    if mode == "UPSTAGE":
        api_key = (getattr(settings, "UPSTAGE_API_KEY", None) or "").strip()
        if not api_key:
            print("UPSTAGE_API_KEY가 없습니다.")
            return None, None
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1/solar",
        )
        return client, "solar-mini"

    # 기본값: OPENAI
    api_key = (getattr(settings, "OPENAI_API_KEY", None) or "").strip()
    if not api_key:
        print("OPENAI_APIK_KEY(또는 OPENAI_API_KEY)가 없습니다.")
        return None, None
    client = OpenAI(api_key=api_key)
    return client, "gpt-4o-mini"


def is_inappropriate(text: str) -> bool:
    """
    텍스트에 부적절한 내용이 있으면 True 반환.
    MODE(OPENAI/UPSTAGE)에 맞는 API 키가 있을 때만 Chat Completions로 판별.
    """
    if not text or not text.strip():
        return False

    client, model = _build_llm_client()
    if not client:
        return False

    stripped = text.strip()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": stripped},
            ],
        )
        answer = (resp.choices[0].message.content or "").strip().upper()
        print(f"부적절 단어 검사 결과 = {answer}")
        return "YES" in answer
    except Exception as e:
        print(f"[LLM 부적절 검사 실패] {type(e).__name__}: {e}")
        return False

def analyze_investment_style(posts_content: str, user=None) -> str:
    """
    사용자의 게시글 내용과 (있다면) 회원가입 시 작성한 설문 데이터를 모아서 투자 성향을 분석합니다.
    """
    has_posts = bool(posts_content and len(posts_content.strip()) >= 10)
    has_survey = bool(user and (user.investment_experience or user.risk_tolerance or user.investment_goal))

    if not has_posts and not has_survey:
        return "작성된 게시글이나 초기 설문 데이터가 없어 투자 성향을 분석할 수 없습니다. 커뮤니티에서 활동을 시작해 보세요!"

    client, model = _build_llm_client()
    if not client:
        return "LLM API 설정이 올바르지 않아 분석을 수행할 수 없습니다."

    # 설문 데이터 텍스트화
    survey_text = ""
    if has_survey:
        survey_text = f"""
[사용자 설문 기반 기본 성향]
- 투자 경험: {user.investment_experience or '미입력'}
- 위험 감수 성향: {user.risk_tolerance or '미입력'}
- 투자 목표: {user.investment_goal or '미입력'}
"""

    if not has_posts:
        # 콜드스타트: 게시글은 없지만 설문은 있는 경우
        prompt = f"""당신은 친절하고 전문적인 최고의 금융 투자 분석가입니다.
이 사용자는 방금 커뮤니티에 가입했으며 아직 작성한 게시글이 없지만, 가입 시 자신의 투자 성향을 다음과 같이 밝혔습니다.
{survey_text}

[요구사항]
1. 위 설문 결과를 바탕으로 사용자의 초기 투자 성향을 진단해 주세요.
2. 현재 성향에 맞는 첫 투자 가이드나 추천하는 자산군(예: ETF, 배당주 등)을 제안해 주세요.
3. 앞으로 커뮤니티에서 어떤 글을 읽고 쓰면 좋을지 응원의 메시지를 작성해 주세요.
4. 가독성 좋게 마크다운과 이모지를 섞어서 300자 내외로 따뜻하게 출력해 주세요."""
    else:
        # 게시글 + 설문
        prompt = f"""당신은 예리하고 전문적인 최고의 금융 투자 분석가입니다.
사용자의 가입 시 초기 설문 데이터와, 실제 커뮤니티 게시글 활동 내역을 종합하여 입체적으로 '투자 성향'을 분석해 주세요.
{survey_text}

[실제 커뮤니티 게시글 내용]
{posts_content}

[요구사항]
1. 설문(본인이 생각하는 성향)과 실제 활동(게시글)을 비교·대조하여 분석해 주세요. (예: 안정추구형이라고 했지만 실제로는 변동성 높은 자산에 관심이 많음 등)
2. 현재 진짜 투자 성향 요약 (예: 가치투자형, 단기트레이더 등) 및 주요 관심사.
3. 포트폴리오 다각화나 리스크 관리에 대한 친절하고 전문적인 조언.
4. 가독성 좋게 마크다운과 이모지를 섞어서 350자 내외로 출력해 주세요."""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content or "분석 결과를 가져올 수 없습니다."
    except Exception as e:
        print(f"[LLM 투자 성향 분석 실패] {type(e).__name__}: {e}")
        return "오류가 발생하여 투자 성향을 분석할 수 없습니다."
