import os
import datetime
import requests
import json
import google.generativeai as genai

# 1. 환경 변수
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
KAKAO_REST_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN")

# 2. 날짜 및 일차 계산 (2026년 10월 5일 월요일 = Day 1 기준)
START_DATE = datetime.date(2026, 10, 5)
now_dt = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
today_date = now_dt.date()
weekday = now_dt.weekday() # 0:월 ~ 6:일

# 일요일은 배포 휴식
if weekday == 6:
    print("일요일은 정규 배포가 없습니다. (자율 복습일)")
    exit(0)

# 경과 주차 및 일차 계산
delta_days = (today_date - START_DATE).days
if delta_days < 0:
    delta_days = 0

week_num = (delta_days // 7) + 1

# 토요일: 주간 통합 총정리
if weekday == 5:
    day_title = f"{week_num}주차 총정리"
    start_day_of_week = (week_num - 1) * 5 + 1
    end_day_of_week = week_num * 5
    topic_desc = f"{week_num}주차 통합 복습 테스트 (Day {start_day_of_week}~{end_day_of_week} 핵심 어휘 25개 및 실전 퀴즈 총정리)"
else:
    # 월~금: 순차 일차 계산 (월요일=1, 화요일=2 ... 다음주 월요일=6, 다다음주 월요일=11)
    current_day_number = (week_num - 1) * 5 + (weekday + 1)
    day_title = f"Day {current_day_number}"
    
    # 대표 주제 풀 (순차 할당)
    topic_pool = {
        1: "Sunway International School 등하원 & 픽업 실전 회화 (드롭존 소통, 학부모 ID 확인, Block B 픽업)",
        2: "레스토랑 주문하기 (인원 안내, 맵기·얼음 조절, 계산서 분할 요청)",
        3: "그로서리 계산하기 (봉투 요청, 과일·채소 무게 측정, 포인트 적립, 분할 결제)",
        4: "콘도 관리사무소 문의 및 시설 보수 (에어컨 청소, 누수 접수, 카드키 재발급, 택배 수령)",
        5: "방과 후 액티비티 상담 (수영/골프/튜터링 레슨 조율, 등록 및 결석 보강 문의)",
        6: "Grab 호출 및 기사 소통 (Block B 픽업 핀 설정, 경로 안내, 로비 전달 요청)",
        7: "로컬 병원 및 약국 방문 (아이 열·감기 증상 설명, 복용법 확인, 보험 청구 서류 요청)",
        8: "쇼핑몰 교환 및 환불 (영수증 제시, 사이즈 변경, 결제 취소 요청)",
        9: "학부모 모임 & 카페 스몰톡 (아이들 방과후 이야기, 주말 골프 및 브런치 대화)",
        10: "생일 파티 초대 및 플레이데이트 조율 (초대 수락, 알레르기 안내, 픽업 시간 상의)",
        11: "차량 정비 및 주유소 이용 (세차, 엔진오일 교환, 타이어 공기압 점검)"
    }
    topic_desc = topic_pool.get(current_day_number, f"말레이시아 생활 실전 회화 (Day {current_day_number})")

date_str = now_dt.strftime("%Y년 %m월 %d일")

# 3. Gemini 프롬프트 구성 (엄격한 캐릭터 및 포맷 지침)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
날짜: {date_str}
일차: {day_title}
주제: {topic_desc}

[필수 캐릭터 및 배경 규칙]
- 주인공 자녀 이름: 항상 'Mike' 또는 'Clara' 사용
- 친구 자녀 이름: 항상 'Sinwoo' 또는 'Eunchan' 사용
- 학교명: 'Sunway International School'
- 픽업 장소 언급 시: 'Block B' 사용 (Bay 2 사용 금지)
- 어휘 및 대화문: 교과서식 표현 금지, 말레이시아 거주 학부모들이 실생활에서 매일 쓰는 고빈도 실전 표현만 엄선

[필수 HTML 구조]
<!DOCTYPE html>, <html>, <body>, <style> 태그는 절대로 쓰지 마세요.
오직 아래의 <article class="report-card">...</article> 단일 HTML 코드 조각만 생성하세요.
반드시 모든 영어 단어와 대화 문장 뒤에 <button class="speak-btn" onclick="playAudio('영어문장')">🔊</button>을 넣어주세요.

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
                <!-- 정확히 10개의 vocab-item 생성 (단어, 의미, 말레이시아 실생활 팁, playAudio 버튼) -->
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <!-- 정확히 3개의 pattern-item 생성 (Mike/Clara/Sinwoo/Eunchan 활용 예문 및 playAudio 버튼) -->
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <!-- 현지 상황에 맞는 생생한 A/B 대화문 4~6줄, 각 줄마다 playAudio 버튼 포함 -->
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 질문 내용</summary>
                    <div class="quiz-answer-content">정답: 정답 내용</div>
                </details>
                <!-- 퀴즈 총 3개 -->
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

# 5. 카카오톡 본인에게 링크 전송
def send_kakao_message(link_url, title_text):
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

    msg_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
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

MY_GITHUB_PAGES_URL = "https://docdaelove-sketch.github.io/english-day1-/"
send_kakao_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
