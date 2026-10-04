import os
import datetime
import requests
import google.generativeai as genai

# 1. GitHub Secrets에 저장한 환경 변수 불러오기
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
KAKAO_REST_KEY = os.environ.get("KAKAO_REST_API_KEY")
KAKAO_REFRESH_TOKEN = os.environ.get("KAKAO_REFRESH_TOKEN")

# 2. 오늘 요일 및 날짜 계산 (말레이시아 시간 기준: UTC+8)
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
weekday = now.weekday()  # 0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일

# 일요일은 발송 및 업데이트 쉬어감
if weekday == 6:
    print("오늘은 일요일이므로 발행을 쉽니다.")
    exit(0)

# 요일별 커리큘럼 설정
# 월~금: Day 2 ~ Day 6 순차 진행 / 토: 1주차 총정리 테스트 (Day 1~6 통합)
curriculum = {
    0: ("Day 2", "레스토랑 주문하기 (인원 안내, 맵기·얼음 조절, 계산서 분할 요청)"),
    1: ("Day 3", "그로서리 계산하기 (봉투, 무게 측정 코너, 포인트 적립, 분할 결제)"),
    2: ("Day 4", "콘도 관리사무소 문의 및 보수 (에어컨 청소, 누수, 카드키, 택배 수령)"),
    3: ("Day 5", "방과 후 액티비티 및 학원 상담 (수영/골프/튜터링 레슨 조율, 등록 및 보강 문의)"),
    4: ("Day 6", "Grab 호출 및 배달 기사 소통 (픽업 장소 설명, 경로 변경, 로비 전달 요청)"),
    5: ("1주차 총정리 테스트", "Day 1부터 Day 6까지 6일간 배운 핵심 단어 30개 및 필수 표현 10개 실전 평가 시험지")
}

day_title, topic_desc = curriculum.get(weekday, ("Daily English", "말레이시아 실전 회화"))

# 3. Gemini API 프롬프트 구성 및 모델 자동 연결
genai.configure(api_key=GEMINI_KEY)

# 사용 가능한 generateContent 지원 모델 중 최신 모델 자동 선택
available_models = [
    m.name for m in genai.list_models() 
    if "generateContent" in m.supported_generation_methods
]
chosen_model = next((m for m in available_models if "flash" in m), available_models[0])
print(f"선택된 모델: {chosen_model}")

model = genai.GenerativeModel(chosen_model)

if weekday == 5:
    # 토요일: 주간 총정리 테스트 양식
    prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
주제: [{day_title}] {topic_desc}

학부모들이 스마트폰과 PC 웹 브라우저에서 편리하게 풀 수 있는 깔끔한 단일 HTML 파일 전체 코드를 작성해주세요.
- <!DOCTYPE html>부터 </html>까지 누락 없이 완전한 코드로 출력할 것.
- 가독성이 뛰어난 반응형 CSS를 <style> 내에 포함할 것.
- 구성:
  1. Part 1: 이번 주 핵심 어휘 테스트 30문항 (객관식 또는 빈칸 완성형)
  2. Part 2: 핵심 회화 표현 테스트 10문항 (상황별 영작 및 문장 완성)
  3. Part 3: 정답 및 명쾌한 해설표 (접이식 <details> 태그 등을 활용하여 바로 보이지 않게 깔끔하게 배치)
- 마크다운 태그(```html) 없이 순수한 HTML 코드만 출력할 것.
"""
else:
    # 평일: 실전 일상 회화 리포트 양식
    prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
주제: [{day_title}] {topic_desc}

학부모들이 웹 브라우저에서 읽고 연습하기 좋은 단일 HTML 파일 전체 코드를 작성해주세요.
- <!DOCTYPE html>부터 </html>까지 누락 없이 완전한 코드로 출력할 것.
- 깔끔하고 모던한 모바일 반응형 CSS를 <style> 내에 포함할 것.
- 구성:
  1. 오늘의 핵심 어휘 6개 (단어, 의미, 말레이시아 현지 팁)
  2. 입에 붙이는 핵심 패턴 3가지 및 예문
  3. 실전 상황 롤플레잉 대화문 (학부모 실생활 밀착형)
  4. 1분 셀프 테스트 (간단한 복습 퀴즈 3개)
- 마크다운 태그(```html) 없이 순수한 HTML 코드만 출력할 것.
"""

response = model.generate_content(prompt)
html_content = response.text.strip().removeprefix("```html").removesuffix("```").strip()

# 4. index.html 파일 저장
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"index.html 업데이트 완료: {day_title}")

# 5. 카카오톡 액세스 토큰 갱신 및 본인에게 링크 전송
def send_kakao_message(link_url, title_text):
    # 토큰 갱신 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_KEY,
        "refresh_token": KAKAO_REFRESH_TOKEN
    }
    token_res = requests.post(token_url, data=token_data).json()
    access_token = token_res.get("access_token")

    if not access_token:
        print("카카오 토큰 갱신 실패:", token_res)
        return

    # 나에게 메시지 전송
    msg_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "template_object": f'''{{
            "object_type": "text",
            "text": "[오늘의 영어 리포트 도착]\\n{title_text}\\n웹페이지가 업데이트되었습니다. 아래 링크를 눌러 확인하고 공유해보세요!",
            "link": {{
                "web_url": "{link_url}",
                "mobile_web_url": "{link_url}"
            }},
            "button_title": "리포트 확인하기"
        }}'''
    }
    res = requests.post(msg_url, headers=headers, data=payload)
    print("카카오톡 전송 결과:", res.status_code, res.text)

# GitHub Pages 웹사이트 주소
MY_GITHUB_PAGES_URL = "https://docdaelove-sketch.github.io/english-day1-/"
send_kakao_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
