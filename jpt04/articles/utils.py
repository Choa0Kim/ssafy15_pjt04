import requests
from django.conf import settings

def is_inappropriate(title, content):
    api_key = settings.UPSTAGE_API_KEY
    if not api_key:
        return False

    url = "https://api.upstage.ai/v1/solar/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 더욱 엄격한 필터링 프롬프트
    prompt = f"""
    당신은 엄격한 커뮤니티 관리자입니다. 아래 게시글에 부적절한 요소가 있는지 검사하세요.
    
    [검사 기준]
    1. 직접적인 욕설 및 비방
    2. 자음 욕설 (예: ㅅㅂ, ㄴㅇㅁ, ㅗ, ㄲㅈ 등)
    3. 변형된 비속어 (예: 시벌, 조카튼 등)
    4. 타인에 대한 혐오, 차별, 공격적인 언행
    5. 금융 커뮤니티의 품격을 떨어뜨리는 저속한 표현
    
    위 기준 중 하나라도 해당되면 즉시 'True'를 반환하세요. 
    매우 깨끗한 글일 때만 'False'를 반환하세요.
    단 한 글자라도 부적절한 자음이나 기호가 욕설의 의미로 쓰였다면 차단해야 합니다.
    
    답변은 오직 'True' 또는 'False'로만 하세요.
    
    제목: {title}
    내용: {content}
    """
    
    data = {
        "model": "solar-pro",
        "messages": [
            {"role": "system", "content": "너는 금융 커뮤니티를 정화하는 매우 엄격한 AI 관리자야. 조금이라도 의심되면 True를 반환해."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=5)
        response.raise_for_status()
        result = response.json()['choices'][0]['message']['content'].strip()
        # 'True'가 포함되어 있거나 대소문자 구분 없이 확인
        return "true" in result.lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False
