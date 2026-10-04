import os
import datetime
import requests
import json
import google.generativeai as genai

# 1. 환경 변수 불러오기
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
KAKAO_REST_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN")

# 2. 요일 및 날짜 계산 (UTC -> 말레이시아/한국 시간 UTC+8 기준)
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
weekday = now.weekday()
date_str = now.strftime("%Y년 %m월 %d일")

# 커리큘럼 매핑 (월~토)
curriculum = {
    0: ("Day 2", "레스토랑 주문하기 (인원 안내, 맵기·얼음 조절, 계산서 분할 요청)"),
    1: ("Day 3", "그로서리 계산하기 (봉투, 무게 측정 코너, 포인트 적립, 분할 결제)"),
    2: ("Day 4", "콘도 관리사무소 문의 및 보수 (에어컨 청소, 누수, 카드키, 택배 수령)"),
    3: ("Day 5", "방과 후 액티비티 및 학원 상담 (수영/골프/튜터링 레슨 조율, 등록 및 보강 문의)"),
    4: ("Day 6", "Grab 호출 및 배달 기사 소통 (픽업 장소 설명, 경로 변경, 로비 전달 요청)"),
    5: ("주간 총정리", "1주차 총정리 테스트 (Day 1~6 주간 핵심 단어 30개 및 복습 시험지)")
}

day_title, topic_desc = curriculum.get(weekday, ("Daily English", "말레이시아 실전 회화"))

# 3. Gemini API 프롬프트 구성 및 모델 연결
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-3.8-flash")

prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
날짜: {date_str}
일차: {day_title}
주제: {topic_desc}

반드시 기존 웹사이트 디자인과 동일한 규격의 단일 카드 HTML 코드 조각만 생성하세요.
<!DOCTYPE html>이나 <html>, <head>, <body> 태그는 일절 쓰지 마세요.
오직 아래의 `<article class="report-card"> ... </article>` 구조만 작성하세요:

<article class="report-card">
    <div class="card-header">
        <span class="card-badge">{day_title}</span>
        <h2>{topic_desc.split('(')[0].strip()}</h2>
        <div class="topic">{topic_desc}</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 6개</div>
            <div class="vocab-grid">
                <!-- 6개 어휘 (vocab-item 구조 유지, 말레이시아 실생활 팁 포함) -->
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <!-- 패턴 3가지 및 학부모 실생활 예문 -->
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <!-- 현지 상황에 맞는 생생한 A/B 대화문 4~6줄 -->
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트</div>
            <div class="quiz-box">
                <!-- 퀴즈 2~3개와 정답 -->
            </div>
        </section>
    </div>
</article>

마크다운 기호(```html) 없이 순수한 HTML 코드 조각만 출력하세요.
"""

# Gemini 호출 및 카드 조각 추출
try:
    response = model.generate_content(prompt)
    card_html = response.text.strip().removeprefix("```html").removesuffix("```").strip()
except Exception as e:
    print("Gemini 호출 오류:", e)
    card_html = ""

# 4. 기존 index.html에 새 카드 누적 삽입
if card_html:
    placeholder = "<!-- NEW_CARD_PLACEHOLDER -->"
    with open("index.html", "r", encoding="utf-8") as f:
        current_html = f.read()

    if placeholder in current_html:
        # Day 제목이 이미 들어가 있는 경우 중복 생성 방지
        if f'<span class="card-badge">{day_title}</span>' not in current_html:
            updated_html = current_html.replace(
                placeholder,
                f"{placeholder}\n\n            <!-- {day_title} Card -->\n" + card_html
            )
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(updated_html)
            print(f"index.html 업데이트 완료: {day_title} 누적 추가됨")
        else:
            print(f"{day_title} 카드가 이미 존재합니다.")
    else:
        print("경고: index.html에 <!-- NEW_CARD_PLACEHOLDER --> 태그가 없습니다.")

# 5. 카카오톡 액세스 토큰 갱신 및 본인에게 링크 전송
def send_kakao_message(link_url, title_text):
    token_url = "[https://kauth.kakao.com/oauth/token](https://kauth.kakao.com/oauth/token)"
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

    msg_url = "[https://kapi.kakao.com/v2/api/talk/memo/default/send](https://kapi.kakao.com/v2/api/talk/memo/default/send)"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    message_text = (
        f"[오늘의 영어 리포트 도착]\n"
        f"{title_text}\n\n"
        f"오늘의 리포트 바로가기:\n"
        f"{link_url}"
    )
    
    template = {
        "object_type": "text",
        "text": message_text,
        "link": {
            "web_url": link_url,
            "mobile_web_url": link_url
        },
        "buttons": [
            {
                "title": "리포트 바로보기",
                "link": {
                    "web_url": link_url,
                    "mobile_web_url": link_url
                }
            }
        ]
    }
    
    res = requests.post(msg_url, headers=headers, data={"template_object": json.dumps(template, ensure_ascii=False)})
    print("카카오톡 전송 결과:", res.status_code, res.text)

MY_GITHUB_PAGES_URL = "[https://docdaelove-sketch.github.io/english-day1-/](https://docdaelove-sketch.github.io/english-day1-/)"
send_kakao_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
