import os
import datetime
import requests
import json
import google.generativeai as genai

# 1. 환경 변수 불러오기
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
KAKAO_REST_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN")

# 2. 날짜 및 요일 매핑 (UTC -> 말레이시아/한국 시간 UTC+8)
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
weekday = now.weekday()
date_str = now.strftime("%Y년 %m월 %d일")

curriculum = {
    0: ("Day 2", "레스토랑 주문하기 (인원 안내, 맵기·얼음 조절, 계산서 분할 요청)"),
    1: ("Day 3", "그로서리 계산하기 (봉투, 무게 측정 코너, 포인트 적립, 분할 결제)"),
    2: ("Day 4", "콘도 관리사무소 문의 및 보수 (에어컨 청소, 누수, 카드키, 택배 수령)"),
    3: ("Day 5", "방과 후 액티비티 및 학원 상담 (수영/골프/튜터링 레슨 조율, 등록 및 보강 문의)"),
    4: ("Day 6", "Grab 호출 및 배달 기사 소통 (픽업 장소 설명, 경로 변경, 로비 전달 요청)"),
    5: ("주간 총정리", "1주차 총정리 테스트 (Day 1~6 핵심 복습 및 실전 평가 시험지)")
}

day_title, topic_desc = curriculum.get(weekday, ("Daily English", "말레이시아 실전 회화"))

# 3. Gemini API 프롬프트 구성
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-3.8-flash")

prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
날짜: {date_str}
일차: {day_title}
주제: {topic_desc}

아래와 완전히 동일한 포맷의 <article class="report-card">...</article> 단일 HTML 코드 조각만 생성하세요.
<!DOCTYPE html>, <html>, <body>, <style> 태그는 절대로 쓰지 마세요.
반드시 모든 영어 단어와 대화 문장 뒤에 <button class="speak-btn" onclick="playAudio('영어문장')">🔊</button>을 넣어주세요.

[필수 구조]
<article class="report-card">
    <div class="card-header">
        <span class="card-badge">{day_title}</span>
        <h2>{topic_desc.split('(')[0].strip()}</h2>
        <div class="topic">{topic_desc}</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <!-- 정확히 10개의 vocab-item 생성: -->
                <!-- <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. 단어</div><div class="vocab-meaning">의미</div><div class="vocab-tip">💡 말레이시아 현지 꿀팁</div></div><button class="speak-btn" onclick="playAudio('단어')">🔊</button></div> -->
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <!-- 정확히 3개의 pattern-item 생성 (예문 및 playAudio 버튼 포함) -->
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <!-- 학부모 실생활 밀착형 A/B 대화문 4~6줄, 각 줄마다 playAudio 버튼 포함 -->
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트</div>
            <div class="quiz-box">
                <!-- 퀴즈 3개와 정답 -->
            </div>
        </section>
    </div>
</article>

마크다운(```html) 없이 순수한 HTML 태그 조각만 출력하세요.
"""

# Gemini 호출 및 카드 추출
try:
    response = model.generate_content(prompt)
    card_html = response.text.strip().removeprefix("```html").removesuffix("```").strip()
except Exception as e:
    print("Gemini 호출 오류:", e)
    card_html = ""

# 4. 기존 index.html에 새 Day 카드 누적 삽입
if card_html:
    placeholder = "<!-- NEW_CARD_PLACEHOLDER -->"
    with open("index.html", "r", encoding="utf-8") as f:
        current_html = f.read()

    if placeholder in current_html:
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
        print("경고: index.html에 <!-- NEW_CARD_PLACEHOLDER --> 태그를 찾을 수 없습니다.")

# 5. 카카오톡 액세스 토큰 갱신 및 링크 전송
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
