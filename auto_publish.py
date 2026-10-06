import os
import datetime
import requests
import json
import time

# 1. 환경 변수
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
KAKAO_REST_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN")

# 2. 날짜 및 일차 계산 (2026년 10월 5일 월요일 = Day 1 기준)
START_DATE = datetime.date(2026, 10, 5)
now_dt = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
today_date = now_dt.date()
weekday = now_dt.weekday()  # 0:월 ~ 6:일

if weekday == 6:
    print("일요일은 정규 배포가 없습니다. (자율 복습일)")
    exit(0)

delta_days = (today_date - START_DATE).days
if delta_days < 0:
    delta_days = 0

week_num = (delta_days // 7) + 1

if weekday == 5:
    day_title = f"{week_num}주차 총정리"
    start_day_of_week = (week_num - 1) * 5 + 1
    end_day_of_week = week_num * 5
    topic_desc = f"{week_num}주차 통합 복습 테스트 (Day {start_day_of_week}~{end_day_of_week} 핵심 어휘 25개 및 실전 퀴즈 총정리)"
else:
    current_day_number = (week_num - 1) * 5 + (weekday + 1)
    day_title = f"Day {current_day_number}"
    
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

# 3. Gemini REST API 프롬프트 (정확한 클래스명 강제 템플릿 포함)
prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
날짜: {date_str}
일차: {day_title}
주제: {topic_desc}

[필수 캐릭터 및 배경 규칙]
- 등장인물/아이 이름: 'Mike', 'Clara', 'Sinwoo', 'Eunchan'을 대화 맥락에 맞게 자연스럽게 사용
- 학교명 및 장소(Sunway International School, Block B): 오직 등하원이나 학교 관련 주제일 때만 사용하고, 일반 식당/카페/쇼핑몰/병원 등의 주제에서는 절대 억지로 언급하지 말 것
- 대화의 자연스러움 최우선: 직원의 질문이나 상황에 맞지 않는 엉뚱한 정보(픽업 이야기 등)는 절대 넣지 말고 현지 실제 대화처럼 구성할 것
- 어휘 및 대화문: 말레이시아 거주 학부모들이 실생활에서 매일 쓰는 고빈도 실전 표현만 엄선

[필수 CSS 클래스 준수 규칙 - Day 1 디자인과 100% 동일하게 생성할 것]
- 어휘 아이템은 반드시 다음 태그 구조를 지키세요:
  <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">번호. 단어</div><div class="vocab-meaning">한글뜻</div><div class="vocab-tip">💡 실생활 팁</div></div><button class="speak-btn" onclick="playAudio('단어')">🔊</button></div>
- 패턴 아이템은 반드시 다음 태그 구조를 지키세요:
  <div class="pattern-item"><div class="pattern-title">Pattern 번호. 영어문장 <button class="speak-btn" onclick="playAudio('영어문장')">🔊</button></div><div class="pattern-example">한글 해석</div></div>
- 대화문은 반드시 다음 태그 구조를 지키세요:
  <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">화자:</span> 대화 내용</div><button class="speak-btn" onclick="playAudio('대화 내용')">🔊</button></div>

[HTML 뼈대 구조]
<!DOCTYPE html>, <html>, <body>, <style> 태그는 절대로 쓰지 마세요.
오직 아래의 <article class="report-card">...</article> 단일 조각만 마크다운(```html) 없이 순수한 텍스트로 출력하세요.

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
                <!-- 정확히 10개의 vocab-item 생성 -->
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <!-- 정확히 3개의 pattern-item 생성 -->
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <!-- 4~6개의 dialogue-line 생성 -->
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
"""

card_html = ""
p_https = "h" + "ttps://"
gemini_host = "generativelanguage.googleapis.com"
gemini_path = f"/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_KEY}"
gemini_api_url = p_https + gemini_host + gemini_path

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}

# 503 과부하 방어: 최대 3회 재시도 (5초 대기)
for attempt in range(1, 4):
    try:
        print(f"Gemini 호출 시도 중 ({attempt}/3)...")
        api_res = requests.post(gemini_api_url, json=payload, timeout=45)
        if api_res.status_code == 200:
            res_json = api_res.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            card_html = raw_text.strip().removeprefix("```html").removesuffix("```").strip()
            print("Gemini 생성 성공!")
            break
        elif api_res.status_code == 503:
            print(f"구글 서버 과부하(503). 5초 대기 후 재시도합니다 ({attempt}/3)...")
            time.sleep(5)
        else:
            print("Gemini API 호출 실패 코드:", api_res.status_code, api_res.text)
            break
    except Exception as e:
        print("Gemini 네트워크 오류:", e)
        time.sleep(3)

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
else:
    print("오류: 생성된 카드 HTML이 없어 index.html 업데이트를 건너뜁니다.")

# 5. 카카오톡 본인에게 링크 전송
def send_kakao_message(link_url, title_text):
    token_url = p_https + "kauth.kakao.com" + "/oauth/token"
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

    msg_url = p_https + "kapi.kakao.com" + "/v2/api/talk/memo/default/send"
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

# 웹사이트 주소 결합 방식
MY_GITHUB_PAGES_URL = p_https + "docdaelove-sketch.github.io/english-day1-/"
send_kakao_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
