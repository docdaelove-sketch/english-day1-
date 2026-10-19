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
    partner_kid = "Sinwoo and Eunchan"
    current_day_number = 0
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
        11: "차량 정비 및 주유소 이용 (세차, 엔진오일 교환, 타이어 공기압 점검)",
        12: "학교 담임선생님 면담 및 출결·생활 문의 (PTC/PTM 학부모 상담, 학교 적응 확인, 조퇴·결석 안내)",
        13: "미용실 및 바버샵 방문 (아이 헤어컷 스타일 요청, 기장 조절, 앞머리 및 숱 정리)",
        14: "현지 은행 및 통신사·결제 서비스 이용 (계좌 개설 문의, TNG eWallet·DuitNow 충전 및 한도 설정, 유심 요금제)",
        15: "주말 가족 여행 및 호텔·리조트 체크인 (얼리 체크인, 커넥팅룸·엑스트라 베드 요청, 수영장 및 조식 문의)"
    }
    topic_desc = topic_pool.get(current_day_number, f"말레이시아 생활 실전 회화 (Day {current_day_number})")

    # 짝수 Day는 Eunchan, 홀수 Day는 Sinwoo (단, 친구/학부모가 필요한 주제일 때만 사용)
    partner_kid = "Eunchan" if current_day_number % 2 == 0 else "Sinwoo"

date_str = now_dt.strftime("%Y년 %m월 %d일")

if current_day_number == 7:
    dialogue_guide = """                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Doctor, Mike has had a high fever and a bad cough since last night.</div><button class="speak-btn" onclick="playAudio('Doctor, Mike has had a high fever and a bad cough since last night.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Doctor:</span> His throat is quite swollen. I will prescribe fever syrup and cough medicine for three days.</div><button class="speak-btn" onclick="playAudio('His throat is quite swollen. I will prescribe fever syrup and cough medicine for three days.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Should he take this medicine after meals? Also, does it cause drowsiness?</div><button class="speak-btn" onclick="playAudio('Should he take this medicine after meals? Also, does it cause drowsiness?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Pharmacist:</span> Take the syrup three times a day after meals, and the fever medicine only when his temperature is above 38.5°C.</div><button class="speak-btn" onclick="playAudio('Take the syrup three times a day after meals, and the fever medicine only when his temperature is above 38.5 degrees.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Got it. Could I please get an itemized receipt and a medical certificate for our insurance claim?</div><button class="speak-btn" onclick="playAudio('Got it. Could I please get an itemized receipt and a medical certificate for our insurance claim?')">🔊</button></div>
                <!-- 주의: Day 7의 dialogue-box 안에는 Parent of Sinwoo 없이 위 5개의 dialogue-line을 정확히 그대로 출력하세요. -->"""
else:
    dialogue_guide = "                <!-- 4~6개의 dialogue-line 생성 (학부모 모임/플레이데이트 등 친구 학부모가 꼭 필요한 주제만 친구 학부모 등장, 그 외 병원/상점/식당 등에서는 주인공 학부모와 현지 직원만 등장) -->"

if weekday == 5:
    prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
날짜: {date_str}
일차: {day_title}
주제: {topic_desc}

[토요일 주간 통합 복습 특별 규칙 - 1주차 총정리와 100% 동일한 구조로 생성할 것]
- 이번 주차(Day {start_day_of_week}~{end_day_of_week})에 배운 핵심 내용을 총정리하는 복습 페이지입니다.
- 대화문(dialogue-box) 섹션은 절대로 생성하지 마세요!
- 📌 핵심 어휘 25선:
  * Day {start_day_of_week}부터 Day {end_day_of_week}까지 각 Day별로 5개씩 총 25개의 핵심 어휘를 배치하세요 (1. ~ 25.).
  * 각 어휘의 vocab-tip 시작 부분에는 반드시 '[Day X]'를 명시하세요 (예: 💡 [Day 6] 콘도 단지가 넓을 때는...).
- 🗣️ 주간 베스트 핵심 패턴 5선:
  * 각 Day별 대표 패턴 1개씩 총 5개의 pattern-item을 배치하세요 (Pattern 1 ~ Pattern 5).
  * pattern-example 시작 부분에 반드시 '[Day X]'를 표기하세요 (예: [Day 6] Block A가 아니라...).
- ✍️ 주간 실전 통합 퀴즈 (5문제):
  * 각 Day별 1문제씩 총 5개의 details quiz-item을 배치하세요 (Q1 ~ Q5).
  * 질문 summary 시작 부분에 반드시 '[Day X]'를 표기하세요 (예: Q1. [Day 6] ...).

[HTML 뼈대 구조 - 마크다운(```html) 없이 순수한 텍스트로 출력할 것]
<article class="report-card">
    <div class="card-header">
        <span class="card-badge">{day_title}</span>
        <h2>{day_title.split(' ')[0]} 통합 복습 테스트</h2>
        <div class="topic">{topic_desc}</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 Day {start_day_of_week}~{end_day_of_week} 핵심 어휘 25선</div>
            <div class="vocab-grid">
                <!-- Day별 5개씩 총 25개의 vocab-item 생성 -->
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 주간 베스트 핵심 패턴 5선</div>
            <div class="pattern-box">
                <!-- 각 Day별 대표 패턴 1개씩 총 5개의 pattern-item 생성 -->
            </div>
        </section>
        <section>
            <div class="section-title">✍️ {day_title.split(' ')[0]} 실전 통합 퀴즈 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <!-- 각 Day별 1문제씩 총 5개의 details quiz-item 생성 -->
            </div>
        </section>
    </div>
</article>
"""
else:
    prompt = f"""
당신은 말레이시아 거주 한국인 학부모를 위한 실전 영어 교육 전문가입니다.
날짜: {date_str}
일차: {day_title}
주제: {topic_desc}

[필수 캐릭터 및 배경 규칙]
- 오늘의 주인공 자녀: 'Mike' 또는 'Clara'
- 엄마 이름 필수 규칙 (영구 적용):
  * 주인공 자녀(Mike & Clara)의 엄마 이름: 'Tina'
  * 상대방 자녀 'Eunchan'의 엄마 이름: 'Yunkyung'
  * 상대방 자녀 'Sinwoo'의 엄마 이름: 'Sera'
  * 롤플레잉에서 엄마 이름이 필요하거나 서로를 부를 때는 반드시 위 이름을 정확하게 사용할 것 (Jenny, Sarah 등 임의의 이름을 절대 사용하지 마세요).
- 상대방 친구 자녀('{partner_kid}' / Parent of {partner_kid}) 등장 규칙: 굳이 모든 롤플레잉에 Sinwoo나 Eunchan이가 등장할 필요는 없습니다. 오직 '학부모 모임, 카페 스몰톡, 생일 파티 초대, 플레이데이트 조율' 등 친구 학부모와의 대화가 문맥상 자연스럽고 꼭 필요한 주제일 때만 '{partner_kid}' (Parent of {partner_kid})를 등장시키세요. 병원, 약국, 쇼핑몰, 식당, 그로서리, 관리사무소, 차량 정비 등 현지 직원(의사, 약사, 점원 등)과 소통하는 주제에서는 친구 학부모를 절대 억지로 등장시키지 말고 주인공 학부모(Tina)와 현지 직원 간의 대화로만 자연스럽게 구성하세요.
- 학교명 및 장소(Sunway International School, Block B): 오직 등하원이나 학교 관련 주제일 때만 사용하고, 일반 식당/카페/쇼핑몰/병원 등의 주제에서는 절대 억지로 언급하지 말 것
- 대화의 자연스러움 최우선: 직원의 질문이나 상황에 맞지 않는 엉뚱한 정보(픽업 이야기, 불필요한 친구 학부모 끼어들기 등)는 절대 넣지 말고 현지 실제 대화처럼 구성할 것
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
{dialogue_guide}
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

# 3. 다중 모델 자동 우회 (한 모델이 503 과부하일 때 즉시 다른 모델로 자동 전환)
card_html = ""
p_https = "h" + "ttps://"
gemini_host = "generativelanguage.googleapis.com"

model_candidates = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro",
    "gemini-4-argon"
]

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}

if GEMINI_KEY and current_day_number not in (12, 13, 14, 15) and not (weekday == 5 and week_num == 3):
    for attempt in range(1, 9):
        model_name = model_candidates[(attempt - 1) % len(model_candidates)]
        gemini_path = f"/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
        gemini_api_url = p_https + gemini_host + gemini_path
        try:
            print(f"Gemini 호출 시도 중 ({attempt}/8) - 모델: {model_name} ...")
            api_res = requests.post(gemini_api_url, json=payload, timeout=75)
            if api_res.status_code == 200:
                res_json = api_res.json()
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                cleaned = raw_text.strip().removeprefix("```html").removeprefix("```").removesuffix("```").strip()
                if "<article" in cleaned:
                    card_html = cleaned
                    print(f"Gemini 생성 성공! (사용 모델: {model_name})")
                    break
            elif api_res.status_code in (429, 500, 502, 503, 504):
                print(f"서버 혼잡({api_res.status_code}). 5초 후 다음 예비 모델로 자동 전환합니다...")
                time.sleep(5)
            else:
                print(f"모델 {model_name} 응답 코드 {api_res.status_code}, 다음 예비 모델로 전환합니다...")
                time.sleep(3)
        except Exception as e:
            print(f"모델 {model_name} 네트워크 지연({e}), 다음 예비 모델로 즉시 전환합니다...")
            time.sleep(3)

# 만약 모든 AI 서버가 동시에 점검/장애일 경우에도 절대 실패하지 않도록 보장하는 비상 카드
if not card_html and current_day_number == 7:
    print("비상용 사전 검증 Day 7 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 7</span>
        <h2>로컬 병원 및 약국 방문</h2>
        <div class="topic">로컬 병원 및 약국 방문 (아이 열·감기 증상 설명, 복용법 확인, 보험 청구 서류 요청)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. High fever</div><div class="vocab-meaning">고열</div><div class="vocab-tip">💡 아이 체온이 38.5도 이상일 때 로컬 클리닉 접수처에서 가장 먼저 말하는 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('High fever')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Runny nose</div><div class="vocab-meaning">콧물</div><div class="vocab-tip">💡 코감기 증상을 설명할 때 코막힘(Stuffy nose)과 함께 세트로 자주 쓰입니다.</div></div><button class="speak-btn" onclick="playAudio('Runny nose')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Sore throat</div><div class="vocab-meaning">인후통 (목 아픔)</div><div class="vocab-tip">💡 아이가 침이나 음식을 삼키기 힘들어할 때 의사에게 꼭 알려주세요.</div></div><button class="speak-btn" onclick="playAudio('Sore throat')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Prescribe</div><div class="vocab-meaning">처방하다</div><div class="vocab-tip">💡 말레이시아 로컬 클리닉(GP)은 진료 후 병원 내 약국 창구에서 바로 약을 조제해 줍니다.</div></div><button class="speak-btn" onclick="playAudio('Prescribe')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Dosage</div><div class="vocab-meaning">복용량 (1회분 용량)</div><div class="vocab-tip">💡 어린이 시럽약은 아이 몸무게(Weight)에 따라 복용량(ml)이 달라지므로 꼭 확인하세요.</div></div><button class="speak-btn" onclick="playAudio('Dosage')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. After meals</div><div class="vocab-meaning">식후에</div><div class="vocab-tip">💡 식전은 Before meals, 공복은 On an empty stomach이라고 약 봉투에 적혀 있습니다.</div></div><button class="speak-btn" onclick="playAudio('After meals')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Drowsiness</div><div class="vocab-meaning">졸음 (약 부작용)</div><div class="vocab-tip">💡 등교 전 먹이는 콧물·기침약이라면 졸음이 없는 약(Non-drowsy)인지 확인하면 좋습니다.</div></div><button class="speak-btn" onclick="playAudio('Drowsiness')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Antibiotics</div><div class="vocab-meaning">항생제</div><div class="vocab-tip">💡 항생제 시럽은 증상이 나아져도 의사 안내 기간(보통 5~7일) 동안 끝까지 먹여야 합니다.</div></div><button class="speak-btn" onclick="playAudio('Antibiotics')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Medical certificate</div><div class="vocab-meaning">진단서 / 병결 확인서 (MC)</div><div class="vocab-tip">💡 말레이시아에서는 흔히 줄여서 'MC'라고 부르며, 학교 결석 제출 및 보험 청구에 필수입니다.</div></div><button class="speak-btn" onclick="playAudio('Medical certificate')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Itemized receipt</div><div class="vocab-meaning">세부 내역 영수증</div><div class="vocab-tip">💡 유학생·실손 보험 청구 시 단순 총액 영수증이 아닌 진료비·약값이 나뉜 세부 영수증을 요청하세요.</div></div><button class="speak-btn" onclick="playAudio('Itemized receipt')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. He has had a high fever since last night. <button class="speak-btn" onclick="playAudio('He has had a high fever since last night.')">🔊</button></div><div class="pattern-example">아이가 어젯밤부터 계속 고열이 나요.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. Should he take this medicine after meals? <button class="speak-btn" onclick="playAudio('Should he take this medicine after meals?')">🔊</button></div><div class="pattern-example">이 약은 식후에 먹여야 하나요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. Could I get an itemized receipt for our insurance claim? <button class="speak-btn" onclick="playAudio('Could I get an itemized receipt for our insurance claim?')">🔊</button></div><div class="pattern-example">보험 청구를 위해 세부 내역 영수증을 받을 수 있을까요?</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Doctor, Mike has had a high fever and a bad cough since last night.</div><button class="speak-btn" onclick="playAudio('Doctor, Mike has had a high fever and a bad cough since last night.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Doctor:</span> His throat is quite swollen. I will prescribe fever syrup and cough medicine for three days.</div><button class="speak-btn" onclick="playAudio('His throat is quite swollen. I will prescribe fever syrup and cough medicine for three days.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Should he take this medicine after meals? Also, does it cause drowsiness?</div><button class="speak-btn" onclick="playAudio('Should he take this medicine after meals? Also, does it cause drowsiness?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Pharmacist:</span> Take the syrup three times a day after meals, and the fever medicine only when his temperature is above 38.5°C.</div><button class="speak-btn" onclick="playAudio('Take the syrup three times a day after meals, and the fever medicine only when his temperature is above 38.5 degrees.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Got it. Could I please get an itemized receipt and a medical certificate for our insurance claim?</div><button class="speak-btn" onclick="playAudio('Got it. Could I please get an itemized receipt and a medical certificate for our insurance claim?')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 말레이시아 병원이나 학교에서 '진단서(병결 확인서)'를 흔히 줄여서 부르는 말은?</summary>
                    <div class="quiz-answer-content">정답: MC (Medical Certificate)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. "이 약은 식후에 먹여야 하나요?"를 영어로 말해보세요.</summary>
                    <div class="quiz-answer-content">정답: Should he take this medicine after meals?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. 보험 청구를 위해 진료비와 약제비 내역이 상세히 적힌 '세부 영수증'을 뜻하는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Itemized receipt</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 8:
    print("비상용 사전 검증 Day 8 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 8</span>
        <h2>쇼핑몰 교환 및 환불</h2>
        <div class="topic">쇼핑몰 교환 및 환불 (영수증 제시, 사이즈 변경, 결제 취소 요청)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. Receipt</div><div class="vocab-meaning">영수증</div><div class="vocab-tip">💡 말레이시아 매장에서는 교환/환불 시 실물 종이 영수증 지참이 필수입니다.</div></div><button class="speak-btn" onclick="playAudio('Receipt')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Exchange</div><div class="vocab-meaning">교환</div><div class="vocab-tip">💡 구매 후 보통 7~14일 이내 영수증과 함께 가져가면 다른 사이즈나 색상으로 교환 가능합니다.</div></div><button class="speak-btn" onclick="playAudio('Exchange')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Refund</div><div class="vocab-meaning">환불</div><div class="vocab-tip">💡 말레이시아 많은 브랜드는 단순 변심 시 현금 환불 대신 교환이나 크레딧 노트를 제공합니다.</div></div><button class="speak-btn" onclick="playAudio('Refund')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Tag attached</div><div class="vocab-meaning">가격표/태그가 붙어 있는</div><div class="vocab-tip">💡 상품 가격표(Price tag)가 훼손되지 않고 붙어 있어야 교환/환불이 접수됩니다.</div></div><button class="speak-btn" onclick="playAudio('Tag attached')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Defective</div><div class="vocab-meaning">불량의 / 하자가 있는</div><div class="vocab-tip">💡 박음질 불량이나 흠집 등 제품 하자가 있을 때는 규정과 상관없이 전액 환불/교환 대상입니다.</div></div><button class="speak-btn" onclick="playAudio('Defective')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Store credit</div><div class="vocab-meaning">매장 적립금 / 교환권 (Credit note)</div><div class="vocab-tip">💡 환불이 불가능할 때 해당 금액만큼 매장에서 나중에 쓸 수 있도록 발행해 주는 전표입니다.</div></div><button class="speak-btn" onclick="playAudio('Store credit')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Size up</div><div class="vocab-meaning">한 치수 크게 (사이즈 업)</div><div class="vocab-tip">💡 'Can I size up?' 형태로 일상에서 매장 직원에게 치수를 키워달라고 할 때 매우 자주 쓰입니다.</div></div><button class="speak-btn" onclick="playAudio('Size up')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Original packaging</div><div class="vocab-meaning">원래 제품 포장</div><div class="vocab-tip">💡 신발이나 잡화는 박스 및 포장 상태가 온전해야 교환이 승인됩니다.</div></div><button class="speak-btn" onclick="playAudio('Original packaging')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Fitting room</div><div class="vocab-meaning">탈의실 / 피팅룸</div><div class="vocab-tip">💡 교환하기 전 다른 사이즈나 색상을 직접 입어볼 때 직원에게 위치를 물어보세요.</div></div><button class="speak-btn" onclick="playAudio('Fitting room')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Transaction slip</div><div class="vocab-meaning">카드 결제 전표</div><div class="vocab-tip">💡 카드 결제 취소 시 영수증과 함께 결제했던 실물 카드 및 전표가 필요합니다.</div></div><button class="speak-btn" onclick="playAudio('Transaction slip')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. I'd like to exchange this for a bigger size. <button class="speak-btn" onclick="playAudio('I would like to exchange this for a bigger size.')">🔊</button></div><div class="pattern-example">이거 더 큰 사이즈로 교환하고 싶어요.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. Can I get a refund on this? Here is the receipt. <button class="speak-btn" onclick="playAudio('Can I get a refund on this? Here is the receipt.')">🔊</button></div><div class="pattern-example">이거 환불받을 수 있을까요? 여기 영수증 있습니다.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. Does your store issue a store credit note instead? <button class="speak-btn" onclick="playAudio('Does your store issue a store credit note instead?')">🔊</button></div><div class="pattern-example">환불 대신 매장 크레딧 노트(교환권)로 발행해 주시나요?</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Hi, good afternoon. I bought this shirt for Mike yesterday, but it's a bit too small. I'd like to exchange it for a bigger size.</div><button class="speak-btn" onclick="playAudio('Hi, good afternoon. I bought this shirt for Mike yesterday, but it is a bit too small. I would like to exchange it for a bigger size.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Cashier:</span> Sure! May I see your receipt and check if the tag is still attached?</div><button class="speak-btn" onclick="playAudio('Sure! May I see your receipt and check if the tag is still attached?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Here is the receipt. The tags are untouched, and it hasn't been worn.</div><button class="speak-btn" onclick="playAudio('Here is the receipt. The tags are untouched, and it has not been worn.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Cashier:</span> Thank you. Let me check our stock... I'm sorry, size L is sold out in navy. Would you like another color, or would you prefer a refund?</div><button class="speak-btn" onclick="playAudio('Thank you. Let me check our stock... I am sorry, size L is sold out in navy. Would you like another color, or would you prefer a refund?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> He really wanted navy. Can I get a refund to the card I used yesterday?</div><button class="speak-btn" onclick="playAudio('He really wanted navy. Can I get a refund to the card I used yesterday?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Cashier:</span> Under our store policy, we can issue a store credit note valid for 3 months at all branches.</div><button class="speak-btn" onclick="playAudio('Under our store policy, we can issue a store credit note valid for 3 months at all branches.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> That works for me. I'll take the store credit note then. Thank you!</div><button class="speak-btn" onclick="playAudio('That works for me. I will take the store credit note then. Thank you!')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 매장에서 "더 큰 사이즈로 교환하고 싶어요"를 영어로 말해보세요.</summary>
                    <div class="quiz-answer-content">정답: I'd like to exchange this for a bigger size.</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 환불 불가 시 매장에서 나중에 쓸 수 있도록 발행해 주는 '매장 적립/교환 전표'는?</summary>
                    <div class="quiz-answer-content">정답: Store credit (또는 Credit note)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. 가격표가 떼어지지 않고 옷에 달려 있는 상태를 뜻하는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Tag attached (The tag is attached)</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 9:
    print("비상용 사전 검증 Day 9 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 9</span>
        <h2>학부모 모임 &amp; 카페 스몰톡</h2>
        <div class="topic">학부모 모임 &amp; 카페 스몰톡 (아이들 방과후 이야기, 주말 골프 및 브런치 대화)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. Catch up</div><div class="vocab-meaning">밀린 이야기를 나누다 / 안부를 묻다</div><div class="vocab-tip">💡 오랜만에 만난 학부모들과 카페에서 이야기 나눌 때 가장 대표적으로 쓰는 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('Catch up')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Settle in</div><div class="vocab-meaning">새 환경에 잘 적응하다 / 자리잡다</div><div class="vocab-tip">💡 새 학기나 방과 후 활동에 아이가 잘 적응하고 있는지 물어볼 때 자주 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Settle in')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. After-school club</div><div class="vocab-meaning">방과 후 활동 / 클럽 (CCAs)</div><div class="vocab-tip">💡 국제학교에서는 방과 후 액티비티를 CCA(Co-Curricular Activities)나 Club이라고 부릅니다.</div></div><button class="speak-btn" onclick="playAudio('After-school club')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Exhausted</div><div class="vocab-meaning">기진맥진한 / 몹시 지친</div><div class="vocab-tip">💡 격렬한 운동 수업이나 방과 후 스포츠 후 아이가 곯아떨어졌을 때 표현합니다.</div></div><button class="speak-btn" onclick="playAudio('Exhausted')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Round of golf</div><div class="vocab-meaning">골프 한 라운딩 (18홀 경기)</div><div class="vocab-tip">💡 주말에 함께 골프 치자고 제안할 때 'play a round of golf' 형태로 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Round of golf')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Tee time</div><div class="vocab-meaning">티오프 시간 (골프 예약 시간)</div><div class="vocab-tip">💡 말레이시아는 더위를 피해 주로 오전 7~8시대 모닝 티타임을 선호합니다.</div></div><button class="speak-btn" onclick="playAudio('Tee time')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Driving range</div><div class="vocab-meaning">골프 인도어/야외 연습장</div><div class="vocab-tip">💡 주중에 가볍게 샷 연습하러 갈 때 학부모들끼리 연습장 같이 가자고 할 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Driving range')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Brunch spot</div><div class="vocab-meaning">브런치 맛집 / 좋은 카페</div><div class="vocab-tip">💡 모임 장소를 정할 때 분위기 좋고 맛있는 브런치 카페를 추천하거나 물어볼 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Brunch spot')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Playdate</div><div class="vocab-meaning">아이들 놀이 약속 (플레이데이트)</div><div class="vocab-tip">💡 주말이나 하교 후 서로 집을 오가거나 키즈카페에서 만날 때 자주 쓰입니다.</div></div><button class="speak-btn" onclick="playAudio('Playdate')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Carpool</div><div class="vocab-meaning">카풀 (등하원 함께 태우기)</div><div class="vocab-tip">💡 같은 콘도나 동네에 사는 학부모들끼리 번갈아 가며 아이들을 픽업할 때 유용합니다.</div></div><button class="speak-btn" onclick="playAudio('Carpool')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. It's so good to finally catch up over coffee! <button class="speak-btn" onclick="playAudio('It is so good to finally catch up over coffee!')">🔊</button></div><div class="pattern-example">커피 한잔하면서 드디어 밀린 이야기 나누니 너무 좋아요!</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. How is your child settling in with the new schedule? <button class="speak-btn" onclick="playAudio('How is your child settling in with the new schedule?')">🔊</button></div><div class="pattern-example">아이가 새 일정(수업)에 잘 적응하고 있나요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. Are you free for a round of golf this weekend? <button class="speak-btn" onclick="playAudio('Are you free for a round of golf this weekend?')">🔊</button></div><div class="pattern-example">이번 주말에 골프 라운딩 갈 시간 괜찮으세요?</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Hi Jenny! Thanks for meeting up today. It's so nice to sit down and catch up over iced Americanos. How is Sinwoo settling into his new term?</div><button class="speak-btn" onclick="playAudio('Hi Jenny! Thanks for meeting up today. It is so nice to sit down and catch up over iced Americanos. How is Sinwoo settling into his new term?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Sinwoo:</span> Hi Grace! He's doing great. He joined the soccer club this week, but he comes home completely exhausted every Tuesday. How about Mike?</div><button class="speak-btn" onclick="playAudio('Hi Grace! He is doing great. He joined the soccer club this week, but he comes home completely exhausted every Tuesday. How about Mike?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> Mike started swimming lessons twice a week, and he loves it! By the way, are you free for a round of golf or brunch this Sunday morning?</div><button class="speak-btn" onclick="playAudio('Mike started swimming lessons twice a week, and he loves it! By the way, are you free for a round of golf or brunch this Sunday morning?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Sinwoo:</span> I'd love that! My husband can look after Sinwoo on Sunday. Let's book an early morning tee time to beat the heat, and then grab brunch afterwards.</div><button class="speak-btn" onclick="playAudio('I would love that! My husband can look after Sinwoo on Sunday. Let us book an early morning tee time to beat the heat, and then grab brunch afterwards.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike:</span> That sounds like a wonderful plan! I know a fantastic new brunch spot near the golf club. I'll reserve our tee time right now.</div><button class="speak-btn" onclick="playAudio('That sounds like a wonderful plan! I know a fantastic new brunch spot near the golf club. I will reserve our tee time right now.')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 카페에서 "커피 한잔하며 밀린 이야기를 나누다"를 영어로 말해보세요.</summary>
                    <div class="quiz-answer-content">정답: Catch up over coffee (It's so good to catch up over coffee)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 아이가 새로운 학교 환경이나 클럽에 "잘 적응하다 / 자리잡다"를 뜻하는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Settle in (Settling in)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. "이번 주말에 골프 한 라운딩(게임) 할 시간 괜찮으세요?"를 영어로 표현해보세요.</summary>
                    <div class="quiz-answer-content">정답: Are you free for a round of golf this weekend?</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 10:
    print("비상용 사전 검증 Day 10 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 10</span>
        <h2>생일 파티 초대 및 플레이데이트 조율</h2>
        <div class="topic">생일 파티 초대 및 플레이데이트 조율 (초대 수락, 알레르기 안내, 픽업 시간 상의)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. RSVP</div><div class="vocab-meaning">초대 회신 (참석 여부 알림)</div><div class="vocab-tip">💡 초대장에 적힌 회신 마감일까지 참석 인원과 함께 답장을 보내는 에티켓입니다.</div></div><button class="speak-btn" onclick="playAudio('RSVP')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Food allergy</div><div class="vocab-meaning">음식 알레르기</div><div class="vocab-tip">💡 땅콩, 유제품, 계란 등 아이가 피해야 하는 알레르기 유무를 미리 주최 학부모에게 알려줍니다.</div></div><button class="speak-btn" onclick="playAudio('Food allergy')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Dietary restrictions</div><div class="vocab-meaning">식단 제한 / 식이 요건</div><div class="vocab-tip">💡 할랄(Halal)이나 채식(Vegetarian) 등 특정 식이 요구 사항을 확인할 때 쓰는 정중한 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('Dietary restrictions')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Drop-and-go</div><div class="vocab-meaning">아이만 내려주고 가기</div><div class="vocab-tip">💡 부모가 파티 내내 상주하지 않고 아이를 맡긴 후 끝나는 시간에 맞춰 데리러 올 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Drop and go')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Grip socks</div><div class="vocab-meaning">미끄럼 방지 양말</div><div class="vocab-tip">💡 말레이시아 실내 놀이터(Playground)나 트램펄린 파크는 미끄럼 방지 양말 착용이 필수입니다.</div></div><button class="speak-btn" onclick="playAudio('Grip socks')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Goodie bag</div><div class="vocab-meaning">파티 답례품 가방 (Party favor)</div><div class="vocab-tip">💡 파티가 끝날 때 참석해 준 친구들에게 과자나 작은 학용품, 장난감을 담아 선물합니다.</div></div><button class="speak-btn" onclick="playAudio('Goodie bag')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Wish list</div><div class="vocab-meaning">선물 희망 목록 (위시리스트)</div><div class="vocab-tip">💡 생일 주인공 아이가 원하는 장난감이나 테마가 있는지 사전에 물어볼 때 유용합니다.</div></div><button class="speak-btn" onclick="playAudio('Wish list')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Make it</div><div class="vocab-meaning">(파티/모임에) 갈 수 있다, 참석하다</div><div class="vocab-tip">💡 'We can make it!' 형태로 모임에 갈 수 있다고 확답할 때 일상에서 가장 흔히 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Make it')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Pick up time</div><div class="vocab-meaning">픽업 시간 (마치는 시간)</div><div class="vocab-tip">💡 파티가 몇 시에 마무리되어 아이를 데리러 가야 하는지 호스트와 조율할 때 확인합니다.</div></div><button class="speak-btn" onclick="playAudio('Pick up time')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Playdate</div><div class="vocab-meaning">플레이데이트 (놀이 약속)</div><div class="vocab-tip">💡 생일 파티 외에도 주말이나 하교 후 서로 집을 방문해 함께 놀도록 일정을 잡을 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Playdate')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. Thank you for the invitation! We'd love to make it. <button class="speak-btn" onclick="playAudio('Thank you for the invitation! We would love to make it.')">🔊</button></div><div class="pattern-example">초대해 주셔서 감사해요! 꼭 갈게요.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. Does he have any food allergies or specific wish lists? <button class="speak-btn" onclick="playAudio('Does he have any food allergies or specific wish lists?')">🔊</button></div><div class="pattern-example">아이가 음식 알레르기가 있거나 특별히 원하는 선물 목록이 있나요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. Should parents stay, or is it okay to just drop and go? <button class="speak-btn" onclick="playAudio('Should parents stay, or is it okay to just drop and go?')">🔊</button></div><div class="pattern-example">학부모가 함께 있어야 하나요, 아니면 아이만 맡겨두고 가도 괜찮을까요?</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Eunchan (Yunkyung):</span> Hi Tina! Thanks for the invitation to Mike's birthday party this Saturday. Eunchan would love to come!</div><button class="speak-btn" onclick="playAudio('Hi Tina! Thanks for the invitation to Mike birthday party this Saturday. Eunchan would love to come!')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Hi Yunkyung! That's wonderful news! Mike is so excited to celebrate with Eunchan and the class friends.</div><button class="speak-btn" onclick="playAudio('Hi Yunkyung! That is wonderful news! Mike is so excited to celebrate with Eunchan and the class friends.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Eunchan (Yunkyung):</span> Just to check beforehand, does Mike have a favorite character or a gift wish list? And does he have any food allergies?</div><button class="speak-btn" onclick="playAudio('Just to check beforehand, does Mike have a favorite character or a gift wish list? And does he have any food allergies?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> He has no food allergies, and he's obsessed with Legos lately, but please don't feel pressured! Just having Eunchan there is the best gift.</div><button class="speak-btn" onclick="playAudio('He has no food allergies, and he is obsessed with Legos lately, but please do not feel pressured! Just having Eunchan there is the best gift.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Eunchan (Yunkyung):</span> That's easy, Legos it is! By the way, should parents stay throughout, or is it okay to drop and go?</div><button class="speak-btn" onclick="playAudio('That is easy, Legos it is! By the way, should parents stay throughout, or is it okay to drop and go?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Either is totally fine! The party runs from 2 PM to 4:30 PM. We'll have coffee and cake for parents who want to hang out.</div><button class="speak-btn" onclick="playAudio('Either is totally fine! The party runs from 2 PM to 4:30 PM. We will have coffee and cake for parents who want to hang out.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Eunchan (Yunkyung):</span> Sounds great! I'll stay for a bit to say hi. See you guys at the party on Saturday!</div><button class="speak-btn" onclick="playAudio('Sounds great! I will stay for a bit to say hi. See you guys at the party on Saturday!')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 파티 초대장에 적힌 '참석 여부 회신(답장)'을 뜻하는 대표적인 약어는?</summary>
                    <div class="quiz-answer-content">정답: RSVP (Please RSVP by [날짜])</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 키즈카페나 파티 장소에 부모가 머물지 않고 '아이만 맡기고 가다'를 영어로 뭐라고 할까요?</summary>
                    <div class="quiz-answer-content">정답: Drop-and-go (또는 Drop off)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. "초대해 주셔서 감사해요! 꼭 갈게요."를 영어 패턴으로 말해보세요.</summary>
                    <div class="quiz-answer-content">정답: Thank you for the invitation! We'd love to make it.</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and weekday == 5 and week_num == 2:
    print("비상용 사전 검증 2주차 총정리 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">2주차 총정리</span>
        <h2>2주차 통합 복습 테스트</h2>
        <div class="topic">2주차 통합 복습 테스트 (Day 6~10 핵심 어휘 25개 및 실전 퀴즈 총정리)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 Day 6~10 핵심 어휘 25선</div>
            <div class="vocab-grid">
                <!-- Day 6 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. Pick-up pin</div><div class="vocab-meaning">픽업 위치 핀 (앱 상의 탑승 위치)</div><div class="vocab-tip">💡 [Day 6] 콘도 단지가 넓을 때는 게이트가 아닌 동 이름(Block B)에 핀을 정확히 찍어야 기사가 헤매지 않습니다.</div></div><button class="speak-btn" onclick="playAudio('Pick-up pin')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Drop-off point</div><div class="vocab-meaning">하차 지점</div><div class="vocab-tip">💡 [Day 6] 목적지에 도착할 때 특정 로비나 출입구에 내려달라고 말할 때 자주 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Drop-off point')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Guardhouse</div><div class="vocab-meaning">경비실, 아파트 출입 게이트</div><div class="vocab-tip">💡 [Day 6] 말레이시아 콘도나 국제학교 게이트를 현지에서는 security보다 guardhouse라고 가장 많이 부릅니다.</div></div><button class="speak-btn" onclick="playAudio('Guardhouse')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Visitor lane</div><div class="vocab-meaning">방문객 전용 차선</div><div class="vocab-tip">💡 [Day 6] 콘도 게이트 진입 시 기사에게 "Please use the visitor lane"이라고 말해주면 통과가 빠릅니다.</div></div><button class="speak-btn" onclick="playAudio('Visitor lane')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. License plate</div><div class="vocab-meaning">차량 번호판</div><div class="vocab-tip">💡 [Day 6] 현지에서는 car plate 또는 plate number라고 부르며 차량 탑승 전 반드시 일치 여부를 확인하세요.</div></div><button class="speak-btn" onclick="playAudio('License plate')">🔊</button></div>

                <!-- Day 7 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. High fever</div><div class="vocab-meaning">고열</div><div class="vocab-tip">💡 [Day 7] 아이 체온이 38.5도 이상일 때 로컬 클리닉 접수처에서 가장 먼저 말하는 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('High fever')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Prescribe</div><div class="vocab-meaning">처방하다</div><div class="vocab-tip">💡 [Day 7] 말레이시아 로컬 클리닉(GP)은 진료 후 병원 내 약국 창구에서 바로 약을 조제해 줍니다.</div></div><button class="speak-btn" onclick="playAudio('Prescribe')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Dosage</div><div class="vocab-meaning">복용량 (1회분 용량)</div><div class="vocab-tip">💡 [Day 7] 어린이 시럽약은 아이 몸무게(Weight)에 따라 복용량(ml)이 달라지므로 꼭 확인하세요.</div></div><button class="speak-btn" onclick="playAudio('Dosage')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Medical certificate</div><div class="vocab-meaning">진단서 / 병결 확인서 (MC)</div><div class="vocab-tip">💡 [Day 7] 말레이시아에서는 흔히 줄여서 'MC'라고 부르며, 학교 결석 제출 및 보험 청구에 필수입니다.</div></div><button class="speak-btn" onclick="playAudio('Medical certificate')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Itemized receipt</div><div class="vocab-meaning">세부 내역 영수증</div><div class="vocab-tip">💡 [Day 7] 유학생·실손 보험 청구 시 단순 총액 영수증이 아닌 진료비·약값이 나뉜 세부 영수증을 요청하세요.</div></div><button class="speak-btn" onclick="playAudio('Itemized receipt')">🔊</button></div>

                <!-- Day 8 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">11. Exchange</div><div class="vocab-meaning">교환</div><div class="vocab-tip">💡 [Day 8] 구매 후 보통 7~14일 이내 영수증과 함께 가져가면 다른 사이즈나 색상으로 교환 가능합니다.</div></div><button class="speak-btn" onclick="playAudio('Exchange')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">12. Refund</div><div class="vocab-meaning">환불</div><div class="vocab-tip">💡 [Day 8] 말레이시아 많은 브랜드는 단순 변심 시 현금 환불 대신 교환이나 크레딧 노트를 제공합니다.</div></div><button class="speak-btn" onclick="playAudio('Refund')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">13. Tag attached</div><div class="vocab-meaning">가격표/태그가 붙어 있는</div><div class="vocab-tip">💡 [Day 8] 상품 가격표(Price tag)가 훼손되지 않고 붙어 있어야 교환/환불이 접수됩니다.</div></div><button class="speak-btn" onclick="playAudio('Tag attached')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">14. Defective</div><div class="vocab-meaning">불량의 / 하자가 있는</div><div class="vocab-tip">💡 [Day 8] 박음질 불량이나 흠집 등 제품 하자가 있을 때는 규정과 상관없이 전액 환불/교환 대상입니다.</div></div><button class="speak-btn" onclick="playAudio('Defective')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">15. Store credit</div><div class="vocab-meaning">매장 적립금 / 교환권 (Credit note)</div><div class="vocab-tip">💡 [Day 8] 환불이 불가능할 때 해당 금액만큼 매장에서 나중에 쓸 수 있도록 발행해 주는 전표입니다.</div></div><button class="speak-btn" onclick="playAudio('Store credit')">🔊</button></div>

                <!-- Day 9 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">16. After-school activities</div><div class="vocab-meaning">방과후 활동</div><div class="vocab-tip">💡 [Day 9] 아이들의 클럽이나 과외 활동을 논할 때 가장 자주 쓰이는 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('After-school activities')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">17. Playdate</div><div class="vocab-meaning">아이들 놀이 약속</div><div class="vocab-tip">💡 [Day 9] 말레이시아 국제학교 학부모들 사이에서 친구 집 방문이나 키즈카페 약속을 잡을 때 필수 단어입니다.</div></div><button class="speak-btn" onclick="playAudio('Playdate')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">18. Tee time</div><div class="vocab-meaning">골프 티타임 (출발 시간)</div><div class="vocab-tip">💡 [Day 9] 주말 골프 모임을 조율할 때 꼭 필요한 필수 골프 용어입니다.</div></div><button class="speak-btn" onclick="playAudio('Tee time')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">19. Brunch spot</div><div class="vocab-meaning">브런치 장소 / 맛집</div><div class="vocab-tip">💡 [Day 9] KL 시내나 데사파크시티 등의 인기 카페/브런치 명소를 물어볼 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Brunch spot')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">20. Catch up</div><div class="vocab-meaning">근황을 나누다, 밀린 이야기를 하다</div><div class="vocab-tip">💡 [Day 9] 오랜만에 만난 학부모 친구에게 "그동안 잘 지냈어? 이야기 좀 하자"고 할 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Catch up')">🔊</button></div>

                <!-- Day 10 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">21. RSVP</div><div class="vocab-meaning">참석 여부를 회신하다</div><div class="vocab-tip">💡 [Day 10] 초대장 하단에 "RSVP by 날짜" 형태로 기한과 함께 적혀 있어요.</div></div><button class="speak-btn" onclick="playAudio('RSVP')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">22. Count someone in</div><div class="vocab-meaning">~를 참석 인원에 넣다</div><div class="vocab-tip">💡 [Day 10] "Count us in!"은 "우리도 갈게!"라는 아주 자연스러운 구어 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('count someone in')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">23. Dietary restriction</div><div class="vocab-meaning">식이 제한 (알레르기/종교적 이유)</div><div class="vocab-tip">💡 [Day 10] 다문화 국가인 말레이시아 파티 주최 시 반드시 확인하는 항목입니다.</div></div><button class="speak-btn" onclick="playAudio('dietary restriction')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">24. Drop-and-go</div><div class="vocab-meaning">아이만 내려주고 가기</div><div class="vocab-tip">💡 [Day 10] 부모가 파티 내내 상주하지 않고 아이를 맡긴 후 끝나는 시간에 맞춰 데리러 올 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('drop-off')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">25. Halal-certified</div><div class="vocab-meaning">할랄 인증을 받은</div><div class="vocab-tip">💡 [Day 10] 무슬림 친구들이 함께 오는 파티 음식이나 젤리를 고를 때 유의해야 합니다.</div></div><button class="speak-btn" onclick="playAudio('Halal-certified')">🔊</button></div>
            </div>
        </section>

        <section>
            <div class="section-title">🗣️ 주간 베스트 핵심 패턴 5선</div>
            <div class="pattern-box">
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 1. Please come to Block B lobby, not Block A. <button class="speak-btn" onclick="playAudio('Please come to Block B lobby, not Block A.')">🔊</button></div>
                    <div class="pattern-example">[Day 6] Block A가 아니라 Block B 로비로 와주세요.</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 2. Could I get an itemized receipt for our insurance claim? <button class="speak-btn" onclick="playAudio('Could I get an itemized receipt for our insurance claim?')">🔊</button></div>
                    <div class="pattern-example">[Day 7] 보험 청구를 위해 세부 내역 영수증을 받을 수 있을까요?</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 3. I'd like to exchange this for a bigger size. <button class="speak-btn" onclick="playAudio('I would like to exchange this for a bigger size.')">🔊</button></div>
                    <div class="pattern-example">[Day 8] 이거 더 큰 사이즈로 교환하고 싶어요.</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 4. Are you up for a weekend round of golf this Saturday? <button class="speak-btn" onclick="playAudio('Are you up for a weekend round of golf this Saturday?')">🔊</button></div>
                    <div class="pattern-example">[Day 9] 이번 주 토요일에 주말 골프 한 라운드 어떠세요?</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 5. What time should I drop him off and pick him up? <button class="speak-btn" onclick="playAudio('What time should I drop him off and pick him up?')">🔊</button></div>
                    <div class="pattern-example">[Day 10] 아이를 몇 시에 데려다주고 몇 시쯤 데리러 가면 될까요?</div>
                </div>
            </div>
        </section>

        <section>
            <div class="section-title">✍️ 2주차 실전 통합 퀴즈 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. [Day 6] Grab 기사가 콘도 내 엉뚱한 동으로 가고 있을 때 "Block B 로비로 와주세요"를 영어로 말하면?</summary>
                    <div class="quiz-answer-content">정답: Please come to Block B lobby, not Block A.</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. [Day 7] 말레이시아 병원이나 학교에서 출결 증빙 및 보험 청구에 쓰는 '진단서(병결 확인서)'를 줄여 부르는 말은?</summary>
                    <div class="quiz-answer-content">정답: MC (Medical Certificate)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. [Day 8] 매장에서 환불 규정상 현금 환불이 어려울 때 대신 발행해 주는 '매장 교환권/적립 전표'를 무엇이라고 할까요?</summary>
                    <div class="quiz-answer-content">정답: Store credit (또는 Credit note)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q4. [Day 9] 카페 등에서 오랜만에 만난 학부모에게 "커피 한잔하며 그동안 밀린 이야기를 나누다"라고 할 때 쓰는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Catch up over coffee (Catch up)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q5. [Day 10] 생일 파티 초대장에 적힌 "참석 여부를 회신해 주세요"를 뜻하는 국제 에티켓 약어는?</summary>
                    <div class="quiz-answer-content">정답: RSVP (Repondez s'il vous plait)</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 12:
    print("비상용 사전 검증 Day 12 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 12</span>
        <h2>학교 담임선생님 면담 및 출결·생활 문의</h2>
        <div class="topic">학교 담임선생님 면담 및 출결·생활 문의 (PTC/PTM 학부모 상담, 학교 적응 확인, 조퇴·결석 안내)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. Parent-Teacher Conference (PTC)</div><div class="vocab-meaning">학부모-교사 정기 상담</div><div class="vocab-tip">💡 국제학교에서는 학기별 정기 면담을 줄여서 'PTC' 또는 'PTM (Parent-Teacher Meeting)'이라고 부르며, 아이가 직접 주도하는 상담은 'SLC (Student-Led Conference)'라고 합니다.</div></div><button class="speak-btn" onclick="playAudio('Parent-Teacher Conference')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Homeroom teacher</div><div class="vocab-meaning">담임 선생님 (Form tutor / Class teacher)</div><div class="vocab-tip">💡 아이의 전반적인 학교생활과 출결을 가장 먼저 상의하는 담당 선생님입니다.</div></div><button class="speak-btn" onclick="playAudio('Homeroom teacher')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Keep up with</div><div class="vocab-meaning">(수업 진도 등을) 잘 따라가다</div><div class="vocab-tip">💡 'Is Mike keeping up with the class?'처럼 아이가 영어 수업 진도를 잘 따라가는지 물어볼 때 필수입니다.</div></div><button class="speak-btn" onclick="playAudio('Keep up with')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Get along with</div><div class="vocab-meaning">~와 잘 어울리다 / 친하게 지내다</div><div class="vocab-tip">💡 새 학기나 전학 초기, 교우 관계를 물어볼 때 가장 자연스럽게 쓰는 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('Get along with')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Sick leave / Absence</div><div class="vocab-meaning">병결 / 결석</div><div class="vocab-tip">💡 아이가 아파서 결석할 때 아침 일찍 학교 포털 앱이나 이메일로 알릴 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Sick leave')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Early pick-up</div><div class="vocab-meaning">조퇴 (정규 하교 전 픽업 / Early dismissal)</div><div class="vocab-tip">💡 병원 예약 등으로 아이를 일찍 데리고 나와야 할 때 행정실(Admin office)과 담임선생님께 미리 알립니다.</div></div><button class="speak-btn" onclick="playAudio('Early pick-up')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Homework load</div><div class="vocab-meaning">숙제량</div><div class="vocab-tip">💡 아이가 과제를 버거워하거나 반대로 추가 학습 자료가 필요할 때 상담하는 단어입니다.</div></div><button class="speak-btn" onclick="playAudio('Homework load')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Participate in</div><div class="vocab-meaning">(수업/활동에) 참여하다</div><div class="vocab-tip">💡 수업 시간에 발표나 모둠 활동에 적극적으로 참여(actively participate)하는지 확인할 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Participate in')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Strengths and weaknesses</div><div class="vocab-meaning">강점과 보완할 점(약점)</div><div class="vocab-tip">💡 면담 시 아이가 잘하는 과목과 집에서 더 신경 써주어야 할 부분을 여쭤볼 때 유용합니다.</div></div><button class="speak-btn" onclick="playAudio('Strengths and weaknesses')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. School portal</div><div class="vocab-meaning">학교 포털 앱 / 학사 시스템</div><div class="vocab-tip">💡 국제학교는 모든 공지와 상담 신청, 성적표 확인이 전용 포털(Seesaw, Toddle, Engage 등)로 이루어집니다.</div></div><button class="speak-btn" onclick="playAudio('School portal')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. How is Mike keeping up with his classes lately? <button class="speak-btn" onclick="playAudio('How is Mike keeping up with his classes lately?')">🔊</button></div><div class="pattern-example">요즘 마이크가 수업 진도는 잘 따라가고 있나요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. Is there anything we can do at home to support his learning? <button class="speak-btn" onclick="playAudio('Is there anything we can do at home to support his learning?')">🔊</button></div><div class="pattern-example">아이 학습을 돕기 위해 집에서 저희가 해줄 수 있는 게 있을까요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. I'd like to request an early pick-up for Clara at 1:30 PM tomorrow. <button class="speak-btn" onclick="playAudio('I would like to request an early pick-up for Clara at 1:30 PM tomorrow.')">🔊</button></div><div class="pattern-example">내일 오후 1시 30분에 클라라 조퇴(일찍 픽업)를 신청하고 싶습니다.</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Good afternoon, Ms. Rachel! Thank you for taking the time to meet with me today. How is Mike keeping up with his classes this term?</div><button class="speak-btn" onclick="playAudio('Good afternoon, Ms. Rachel! Thank you for taking the time to meet with me today. How is Mike keeping up with his classes this term?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Teacher (Ms. Rachel):</span> Good afternoon, Tina! Mike is doing wonderfully. He gets along very well with his classmates and actively participates in math and science.</div><button class="speak-btn" onclick="playAudio('Good afternoon, Tina! Mike is doing wonderfully. He gets along very well with his classmates and actively participates in math and science.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> I'm so relieved to hear that! He sometimes feels a bit shy when speaking English in front of a large group. Is there anything we can do at home to help him?</div><button class="speak-btn" onclick="playAudio('I am so relieved to hear that! He sometimes feels a bit shy when speaking English in front of a large group. Is there anything we can do at home to help him?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Teacher (Ms. Rachel):</span> Reading aloud together for 15 minutes a day will boost his confidence a lot. I'll also pair him with a friendly buddy for next week's presentation.</div><button class="speak-btn" onclick="playAudio('Reading aloud together for 15 minutes a day will boost his confidence a lot. I will also pair him with a friendly buddy for next week presentation.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> That's a great idea, thank you so much! Also, just to let you know, Mike has a dentist appointment this Friday, so I'll request an early pick-up at 2:00 PM through the school portal.</div><button class="speak-btn" onclick="playAudio('That is a great idea, thank you so much! Also, just to let you know, Mike has a dentist appointment this Friday, so I will request an early pick-up at 2 PM through the school portal.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Teacher (Ms. Rachel):</span> Noted! I'll make sure he packs his belongings and heads to the Block B pick-up zone by 2:00 PM on Friday.</div><button class="speak-btn" onclick="playAudio('Noted! I will make sure he packs his belongings and heads to the Block B pick-up zone by 2 PM on Friday.')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 선생님께 "마이크가 수업 진도를 잘 따라가고 있나요?"를 영어로 물어보세요.</summary>
                    <div class="quiz-answer-content">정답: How is Mike keeping up with his classes?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 병원 예약 등으로 정규 하교 시간보다 "일찍 데리러 가기(조퇴)"를 뜻하는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Early pick-up (또는 Early dismissal)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. "아이 학습을 돕기 위해 집에서 저희가 해줄 수 있는 게 있을까요?"를 영어로 말해보세요.</summary>
                    <div class="quiz-answer-content">정답: Is there anything we can do at home to support his learning?</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 13:
    print("비상용 사전 검증 Day 13 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 13</span>
        <h2>미용실 및 바버샵 방문</h2>
        <div class="topic">미용실 및 바버샵 방문 (아이 헤어컷 스타일 요청, 기장 조절, 앞머리 및 숱 정리)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. Trim</div><div class="vocab-meaning">(끝부분만 살짝) 다듬다</div><div class="vocab-tip">💡 전체 스타일은 유지하고 지저분하게 자란 끝부분만 조금 자를 때 'Just a trim, please'라고 합니다.</div></div><button class="speak-btn" onclick="playAudio('Trim')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Bangs / Fringe</div><div class="vocab-meaning">앞머리</div><div class="vocab-tip">💡 미국식으로는 Bangs, 영국·말레이시아식으로는 Fringe라고도 많이 부릅니다.</div></div><button class="speak-btn" onclick="playAudio('Bangs and Fringe')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Thin out</div><div class="vocab-meaning">머리 숱을 치다</div><div class="vocab-tip">💡 더운 말레이시아 날씨 때문에 아이 머리 숱이 많아 답답할 때 'thin out the hair'라고 요청하세요.</div></div><button class="speak-btn" onclick="playAudio('Thin out')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Clippers (Guard number)</div><div class="vocab-meaning">바리깡 / 클리퍼 (미는 길이 단계)</div><div class="vocab-tip">💡 남자아이 옆·뒷머리를 밀 때 클리퍼 탭 번호(예: Number 2 또는 Number 3)를 말하면 실패가 없습니다.</div></div><button class="speak-btn" onclick="playAudio('Clippers')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Sideburns</div><div class="vocab-meaning">구레나룻</div><div class="vocab-tip">💡 귀 옆 라인과 구레나룻을 깔끔하게 정리해 달라고 할 때 쓰는 필수 단어입니다.</div></div><button class="speak-btn" onclick="playAudio('Sideburns')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Nape (of the neck)</div><div class="vocab-meaning">뒷목 라인 (목덜미)</div><div class="vocab-tip">💡 뒷머리가 목을 덮지 않게 'clean up the nape'라고 하면 단정하게 다듬어 줍니다.</div></div><button class="speak-btn" onclick="playAudio('Nape of the neck')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Layered cut</div><div class="vocab-meaning">층을 낸 커트 (레이어드 컷)</div><div class="vocab-tip">💡 여자아이 긴 머리가 너무 무거워 보이지 않게 자연스럽게 층을 내달라고 할 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Layered cut')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Part (Side part)</div><div class="vocab-meaning">가르마 (옆 가르마)</div><div class="vocab-tip">💡 평소 아이가 타는 가르마 방향(Side part / Middle part)을 디자이너에게 미리 알려줄 때 유용합니다.</div></div><button class="speak-btn" onclick="playAudio('Side part')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Eyebrow level</div><div class="vocab-meaning">눈썹 높이(길이)</div><div class="vocab-tip">💡 앞머리가 너무 짧아지지 않도록 'right at the eyebrow level(눈썹 라인에 맞춰서)'처럼 기준점을 잡아주세요.</div></div><button class="speak-btn" onclick="playAudio('Eyebrow level')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Blow-dry</div><div class="vocab-meaning">드라이 (머리를 말리며 스타일링하기)</div><div class="vocab-tip">💡 샴푸 후 간단히 말리기만 할지, 스타일링 드라이를 할지 물어볼 때 자주 등장합니다.</div></div><button class="speak-btn" onclick="playAudio('Blow-dry')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. Just a trim on the top, and keep the sides neat and short. <button class="speak-btn" onclick="playAudio('Just a trim on the top, and keep the sides neat and short.')">🔊</button></div><div class="pattern-example">윗머리는 살짝만 다듬어 주시고, 옆머리는 깔끔하고 짧게 해주세요.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. Could you thin out his hair a bit? It gets too hot here. <button class="speak-btn" onclick="playAudio('Could you thin out his hair a bit? It gets too hot here.')">🔊</button></div><div class="pattern-example">아이 머리 숱을 조금 쳐주시겠어요? 여기 날씨가 더워서 땀이 많이 나요.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. Please cut her bangs right to the eyebrow level, not too short. <button class="speak-btn" onclick="playAudio('Please cut her bangs right to the eyebrow level, not too short.')">🔊</button></div><div class="pattern-example">앞머리는 너무 짧지 않게 딱 눈썹 위치까지만 잘라주세요.</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Hi! We have a haircut appointment for Mike and Clara at 3:30 PM.</div><button class="speak-btn" onclick="playAudio('Hi! We have a haircut appointment for Mike and Clara at 3:30 PM.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Hairstylist:</span> Welcome! Please have a seat here. How would you like Mike's hair done today?</div><button class="speak-btn" onclick="playAudio('Welcome! Please have a seat here. How would you like Mike hair done today?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> I'd like to show you this photo. Please keep the sides neat and short around his ears, and just a trim on the top.</div><button class="speak-btn" onclick="playAudio('I would like to show you this photo. Please keep the sides neat and short around his ears, and just a trim on the top.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Hairstylist:</span> Sure, I can use a number 3 clipper on the sides and blend it naturally. His hair is quite thick—should I thin it out a little?</div><button class="speak-btn" onclick="playAudio('Sure, I can use a number 3 clipper on the sides and blend it naturally. His hair is quite thick. Should I thin it out a little?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Yes, please thin out his hair a bit so it's easier to dry after swimming. And for Clara later, please just trim the ends and cut her bangs to the eyebrow level.</div><button class="speak-btn" onclick="playAudio('Yes, please thin out his hair a bit so it is easier to dry after swimming. And for Clara later, please just trim the ends and cut her bangs to the eyebrow level.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Hairstylist:</span> Got it! Not too short on the bangs. Let's start with Mike first!</div><button class="speak-btn" onclick="playAudio('Got it! Not too short on the bangs. Let us start with Mike first!')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 미용실에서 "아이 머리 숱을 조금 쳐주시겠어요?"를 영어로 말해보세요.</summary>
                    <div class="quiz-answer-content">정답: Could you thin out his/her hair a bit?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 전체 길이를 많이 자르지 않고 "끝만 살짝 다듬다"를 뜻하는 단어는?</summary>
                    <div class="quiz-answer-content">정답: Trim (Just a trim, please.)</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. 앞머리를 자를 때 "눈썹 위치(높이)까지만 잘라주세요"라고 기준을 말할 때 쓰는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Please cut her bangs right to the eyebrow level.</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 14:
    print("비상용 사전 검증 Day 14 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 14</span>
        <h2>현지 은행 및 통신사·결제 서비스 이용</h2>
        <div class="topic">현지 은행 및 통신사·결제 서비스 이용 (계좌 개설 문의, TNG eWallet·DuitNow 충전 및 한도 설정, 유심 요금제)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. DuitNow QR</div><div class="vocab-meaning">말레이시아 통합 QR 결제·송금 시스템</div><div class="vocab-tip">💡 말레이시아 식당, 야시장, 학원비 이체까지 분홍색 DuitNow QR 하나로 모든 은행·페이 결제가 가능합니다.</div></div><button class="speak-btn" onclick="playAudio('DuitNow QR')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. TNG (Touch 'n Go) eWallet</div><div class="vocab-meaning">터치앤고 전자지갑 앱 (및 톨게이트·주차 카드)</div><div class="vocab-tip">💡 현지 생활 필수 앱으로, 여권 인증을 완료해야 한도 증액과 DuitNow 계좌 이체가 활성화됩니다.</div></div><button class="speak-btn" onclick="playAudio('Touch and Go eWallet')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Top up / Reload</div><div class="vocab-meaning">(선불 유심·페이 잔액 등을) 충전하다</div><div class="vocab-tip">💡 톨게이트용 TNG 카드나 선불 유심 잔액을 충전할 때 현지에서는 'Top up' 또는 'Reload'라고 합니다.</div></div><button class="speak-btn" onclick="playAudio('Top up and Reload')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Daily transfer limit</div><div class="vocab-meaning">일일 이체 한도</div><div class="vocab-tip">💡 집세(Rent)나 학원비를 송금할 때 일일 한도에 걸리면 은행 앱에서 한도(Limit)를 상향해야 합니다.</div></div><button class="speak-btn" onclick="playAudio('Daily transfer limit')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Guardian visa / Student pass</div><div class="vocab-meaning">가디언 비자(동반 부모 비자) / 학생 비자</div><div class="vocab-tip">💡 현지 은행 계좌(Maybank, CIMB 등) 개설 시 여권에 부착된 유효한 비자 스티커와 학교 재학증명서가 필수입니다.</div></div><button class="speak-btn" onclick="playAudio('Guardian visa')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Bank statement</div><div class="vocab-meaning">은행 거래내역서 (잔고·입출금 증명서)</div><div class="vocab-tip">💡 비자 연장이나 국제학교 서류 제출 시 최근 3개월 치 은행 거래내역서를 요청할 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Bank statement')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Postpaid / Prepaid plan</div><div class="vocab-meaning">후불 요금제 / 선불 요금제</div><div class="vocab-tip">💡 장기 거주 학부모님은 매월 자동 결제되는 Postpaid(후불) 요금제로 전환하면 번호 유지가 편합니다.</div></div><button class="speak-btn" onclick="playAudio('Postpaid and Prepaid plan')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Data roaming / Hotspot</div><div class="vocab-meaning">데이터 로밍 / 핫스팟 테더링</div><div class="vocab-tip">💡 방학 때 한국이나 싱가포르 등에 다녀올 때 통신사 앱에서 로밍 패스를 신청할 때 확인하는 용어입니다.</div></div><button class="speak-btn" onclick="playAudio('Data roaming')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Verification (eKYC)</div><div class="vocab-meaning">본인 인증 (비대면 여권·얼굴 인식 인증)</div><div class="vocab-tip">💡 앱에서 여권 스캔 후 수동 승인(Manual verification)이 지연될 때 고객센터에 문의하는 단어입니다.</div></div><button class="speak-btn" onclick="playAudio('Verification')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Minimum balance</div><div class="vocab-meaning">계좌 최소 유지 잔액</div><div class="vocab-tip">💡 말레이시아 일반 예금 계좌(Savings account)는 보통 RM 20~250의 최소 잔액을 유지해야 계좌가 활성 상태로 유지됩니다.</div></div><button class="speak-btn" onclick="playAudio('Minimum balance')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. I'd like to open a savings account. I hold a guardian visa. <button class="speak-btn" onclick="playAudio('I would like to open a savings account. I hold a guardian visa.')">🔊</button></div><div class="pattern-example">예금 계좌를 개설하고 싶습니다. 저는 가디언 비자를 소지하고 있어요.</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. How can I increase my daily transfer limit on the mobile app? <button class="speak-btn" onclick="playAudio('How can I increase my daily transfer limit on the mobile app?')">🔊</button></div><div class="pattern-example">모바일 앱에서 일일 이체 한도를 어떻게 늘릴 수 있나요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. Can I pay with DuitNow QR or Touch 'n Go eWallet? <button class="speak-btn" onclick="playAudio('Can I pay with DuitNow QR or Touch and Go eWallet?')">🔊</button></div><div class="pattern-example">DuitNow QR이나 터치앤고 이월렛으로 결제할 수 있나요?</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Good morning! I'd like to open a savings account here. I hold a guardian visa, and my children go to Sunway International School.</div><button class="speak-btn" onclick="playAudio('Good morning! I would like to open a savings account here. I hold a guardian visa, and my children go to Sunway International School.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Bank Officer:</span> Good morning, ma'am! Sure, may I see your passport, valid visa sticker, and the school confirmation letter?</div><button class="speak-btn" onclick="playAudio('Good morning, maam! Sure, may I see your passport, valid visa sticker, and the school confirmation letter?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Here are all the documents. Once the account is opened, can I link it to DuitNow and Touch 'n Go eWallet right away?</div><button class="speak-btn" onclick="playAudio('Here are all the documents. Once the account is opened, can I link it to DuitNow and Touch and Go eWallet right away?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Bank Officer:</span> Yes, we'll set up your mobile banking app today so you can scan DuitNow QR codes immediately. A minimum deposit of 250 Ringgit is required to activate the account.</div><button class="speak-btn" onclick="playAudio('Yes, we will set up your mobile banking app today so you can scan DuitNow QR codes immediately. A minimum deposit of 250 Ringgit is required to activate the account.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Great! Also, how can I increase my daily transfer limit? I need to transfer our monthly condo rent next week.</div><button class="speak-btn" onclick="playAudio('Great! Also, how can I increase my daily transfer limit? I need to transfer our monthly condo rent next week.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Bank Officer:</span> Let me help you set the daily transfer limit to 20,000 Ringgit directly at the counter now so you won't have any issues.</div><button class="speak-btn" onclick="playAudio('Let me help you set the daily transfer limit to 20000 Ringgit directly at the counter now so you will not have any issues.')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 말레이시아 상점이나 식당에서 "DuitNow QR이나 터치앤고로 결제할 수 있나요?"를 영어로 물어보세요.</summary>
                    <div class="quiz-answer-content">정답: Can I pay with DuitNow QR or Touch 'n Go eWallet?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 터치앤고 카드나 선불 유심에 "잔액을 충전하다"를 뜻하는 현지 표현 두 가지는?</summary>
                    <div class="quiz-answer-content">정답: Top up 또는 Reload</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. 월세나 학비를 보내기 위해 모바일 뱅킹의 "일일 이체 한도를 늘리다"를 영어로 표현하면?</summary>
                    <div class="quiz-answer-content">정답: Increase my daily transfer limit</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and current_day_number == 15:
    print("비상용 사전 검증 Day 15 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">Day 15</span>
        <h2>주말 가족 여행 및 호텔·리조트 체크인</h2>
        <div class="topic">주말 가족 여행 및 호텔·리조트 체크인 (얼리 체크인, 커넥팅룸·엑스트라 베드 요청, 수영장 및 조식 문의)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 오늘의 핵심 어휘 10개</div>
            <div class="vocab-grid">
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. Early check-in / Late check-out</div><div class="vocab-meaning">얼리 체크인 (일찍 입실) / 레이트 체크아웃 (늦은 퇴실)</div><div class="vocab-tip">💡 아이들과 수영장을 더 이용하고 싶을 때 객실 여유(Subject to availability)에 따라 요청해 볼 수 있습니다.</div></div><button class="speak-btn" onclick="playAudio('Early check-in and Late check-out')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Connecting rooms</div><div class="vocab-meaning">커넥팅 룸 (방 사이에 내부 문이 연결된 객실)</div><div class="vocab-tip">💡 아이들이 크거나 두 가족이 함께 여행 갈 때 'Adjoining rooms(이웃한 방)'와 구분해 '내부 문이 연결된 방'을 뜻합니다.</div></div><button class="speak-btn" onclick="playAudio('Connecting rooms')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Extra bed / Rollaway bed</div><div class="vocab-meaning">추가 침대 (이동식 간이침대)</div><div class="vocab-tip">💡 아이 두 명과 함께 묵을 때 객실에 간이침대 추가가 가능한지 물어볼 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Extra bed')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Complimentary breakfast</div><div class="vocab-meaning">무료 포함 조식</div><div class="vocab-tip">💡 예약에 포함된 성인 조식 외에 아동 조식 추가 요금(Child rate) 기준 나이를 확인할 때 유용합니다.</div></div><button class="speak-btn" onclick="playAudio('Complimentary breakfast')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Security deposit</div><div class="vocab-meaning">객실 보증금 (디파짓)</div><div class="vocab-tip">💡 체크인 시 카드 가승인이나 현금으로 맡겼다가 체크아웃 시 환불(Refunded upon check-out)받는 보증금입니다.</div></div><button class="speak-btn" onclick="playAudio('Security deposit')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Tourism tax</div><div class="vocab-meaning">관광세 (박당 RM 10)</div><div class="vocab-tip">💡 말레이시아 호텔에서는 외국인 투숙객에게 1박당 RM 10의 관광세를 부과하나, 장기 비자 소지 여부에 따라 확인하기도 합니다.</div></div><button class="speak-btn" onclick="playAudio('Tourism tax')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Pool towel</div><div class="vocab-meaning">수영장 타월</div><div class="vocab-tip">💡 객실 수건 대신 수영장 옆 Towel counter에서 객실 번호를 적고 대여하는 타월입니다.</div></div><button class="speak-btn" onclick="playAudio('Pool towel')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Kids' club</div><div class="vocab-meaning">키즈 클럽 (어린이 체험·놀이 공간)</div><div class="vocab-tip">💡 페낭, 코타키나발루, 데사루 등의 리조트에서 시간대별 키즈 액티비티 프로그램을 물어볼 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Kids club')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Luggage storage</div><div class="vocab-meaning">짐 보관 서비스</div><div class="vocab-tip">💡 체크인 시간 전 도착했거나 체크아웃 후 차량 탑승 전까지 컨시어지에 짐을 맡길 때 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Luggage storage')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. Housekeeping (Make up the room)</div><div class="vocab-meaning">객실 청소 (방 정리 요청)</div><div class="vocab-tip">💡 외출하면서 방 청소와 수건 교체를 부탁할 때 'Could you make up our room, please?'라고 말합니다.</div></div><button class="speak-btn" onclick="playAudio('Housekeeping')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">🗣️ 입에 붙이는 핵심 패턴 3가지</div>
            <div class="pattern-box">
                <div class="pattern-item"><div class="pattern-title">Pattern 1. Hi, I'd like to check in under the name Tina. Is early check-in available? <button class="speak-btn" onclick="playAudio('Hi, I would like to check in under the name Tina. Is early check-in available?')">🔊</button></div><div class="pattern-example">안녕하세요, 티나 이름으로 체크인하려고 합니다. 혹시 얼리 체크인이 가능할까요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 2. Could we get an extra bed and extra towels for the kids, please? <button class="speak-btn" onclick="playAudio('Could we get an extra bed and extra towels for the kids, please?')">🔊</button></div><div class="pattern-example">아이들을 위해 엑스트라 베드 하나와 수건을 좀 더 받을 수 있을까요?</div></div>
                <div class="pattern-item"><div class="pattern-title">Pattern 3. What time is breakfast served, and where is the kids' pool located? <button class="speak-btn" onclick="playAudio('What time is breakfast served, and where is the kids pool located?')">🔊</button></div><div class="pattern-example">조식 시간은 몇 시부터이고, 어린이 수영장은 어디에 있나요?</div></div>
            </div>
        </section>
        <section>
            <div class="section-title">💬 실전 롤플레잉 대화문</div>
            <div class="dialogue-box">
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Good afternoon! I'd like to check in. I have a reservation for two nights under the name Tina.</div><button class="speak-btn" onclick="playAudio('Good afternoon! I would like to check in. I have a reservation for two nights under the name Tina.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Receptionist:</span> Welcome to our resort, Ms. Tina! May I have your passport for registration? I see you booked a Family Suite for two adults and two children.</div><button class="speak-btn" onclick="playAudio('Welcome to our resort, Ms. Tina! May I have your passport for registration? I see you booked a Family Suite for two adults and two children.')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Here is my passport. I know it's an hour before the official check-in time, but is early check-in available by any chance? Mike and Clara can't wait to jump into the pool!</div><button class="speak-btn" onclick="playAudio('Here is my passport. I know it is an hour before the official check-in time, but is early check-in available by any chance? Mike and Clara cannot wait to jump into the pool!')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Receptionist:</span> Good news! Your room on the 5th floor overlooking the ocean is already ready. Would you still like the extra bed we noted in your booking request?</div><button class="speak-btn" onclick="playAudio('Good news! Your room on the 5th floor overlooking the ocean is already ready. Would you still like the extra bed we noted in your booking request?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Parent of Mike (Tina):</span> Yes, please! Could we also get two extra bath towels sent to the room? And what time is breakfast served tomorrow morning?</div><button class="speak-btn" onclick="playAudio('Yes, please! Could we also get two extra bath towels sent to the room? And what time is breakfast served tomorrow morning?')">🔊</button></div>
                <div class="dialogue-line"><div class="dialogue-text"><span class="speaker">Receptionist:</span> Certainly, housekeeping will bring the extra bed and towels right up. Breakfast is served from 6:30 AM to 10:30 AM at the main restaurant on the ground floor. Enjoy your stay!</div><button class="speak-btn" onclick="playAudio('Certainly, housekeeping will bring the extra bed and towels right up. Breakfast is served from 6:30 AM to 10:30 AM at the main restaurant on the ground floor. Enjoy your stay!')">🔊</button></div>
            </div>
        </section>
        <section>
            <div class="section-title">✍️ 1분 셀프 테스트 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. 호텔 프런트에서 "혹시 얼리 체크인(일찍 입실)이 가능할까요?"를 영어로 물어보세요.</summary>
                    <div class="quiz-answer-content">정답: Is early check-in available (by any chance)?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. 아이들을 위해 객실에 "추가 간이침대와 수건을 더 받을 수 있을까요?"를 영어로 말하면?</summary>
                    <div class="quiz-answer-content">정답: Could we get an extra bed and extra towels for the kids, please?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. 외출할 때 하우스키핑 직원에게 "객실 청소(방 정리) 좀 해주시겠어요?"를 뜻하는 자연스러운 표현은?</summary>
                    <div class="quiz-answer-content">정답: Could you make up our room, please?</div>
                </details>
            </div>
        </section>
    </div>
</article>"""
elif not card_html and weekday == 5 and week_num == 3:
    print("비상용 사전 검증 3주차 총정리 카드를 적용합니다.")
    card_html = """<article class="report-card">
    <div class="card-header">
        <span class="card-badge">3주차 총정리</span>
        <h2>3주차 통합 복습 테스트</h2>
        <div class="topic">3주차 통합 복습 테스트 (Day 11~15 핵심 어휘 25개 및 실전 퀴즈 총정리)</div>
    </div>
    <div class="card-body">
        <section>
            <div class="section-title">📌 Day 11~15 핵심 어휘 25선</div>
            <div class="vocab-grid">
                <!-- Day 11 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">1. RON 95 / RON 97</div><div class="vocab-meaning">일반 휘발유 / 고급 휘발유</div><div class="vocab-tip">💡 [Day 11] 말레이시아 주유소(Petronas, Shell 등)에서 노란색/초록색 건은 RON 95, 빨간색 건은 RON 97입니다.</div></div><button class="speak-btn" onclick="playAudio('RON ninety-five and RON ninety-seven')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">2. Tyre pressure</div><div class="vocab-meaning">타이어 공기압</div><div class="vocab-tip">💡 [Day 11] 주유소 한쪽에 마련된 무료 공기 주입기(Air pump)에서 디지털 숫자를 맞추고 직접 주입할 수 있습니다.</div></div><button class="speak-btn" onclick="playAudio('Tyre pressure')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">3. Engine oil service</div><div class="vocab-meaning">엔진오일 교환 정비</div><div class="vocab-tip">💡 [Day 11] 현지 정비소에서는 보통 마이너 서비스(Minor service)라고 부르며 오일과 오일 필터를 함께 교체합니다.</div></div><button class="speak-btn" onclick="playAudio('Engine oil service')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">4. Car wash (Snow wash)</div><div class="vocab-meaning">세차 (폼건 버블 세차)</div><div class="vocab-tip">💡 [Day 11] 말레이시아 로컬 세차장에서는 거품을 듬뿍 얹고 실내 청소까지 해주는 'Wash and vacuum'을 주로 이용합니다.</div></div><button class="speak-btn" onclick="playAudio('Snow wash')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">5. Full tank</div><div class="vocab-meaning">가득 주유 (만땅)</div><div class="vocab-tip">💡 [Day 11] 기름을 가득 넣고 싶을 때 주유원에게 "Full tank, please"라고 말하면 됩니다.</div></div><button class="speak-btn" onclick="playAudio('Full tank')">🔊</button></div>

                <!-- Day 12 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">6. Parent-Teacher Conference (PTC)</div><div class="vocab-meaning">학부모-교사 정기 상담</div><div class="vocab-tip">💡 [Day 12] 국제학교 학기별 정기 면담은 'PTC' 또는 'PTM', 아이가 주도하는 상담은 'SLC'라고 부릅니다.</div></div><button class="speak-btn" onclick="playAudio('Parent-Teacher Conference')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">7. Keep up with</div><div class="vocab-meaning">(수업 진도 등을) 잘 따라가다</div><div class="vocab-tip">💡 [Day 12] 아이가 영어 수업 진도를 잘 따라가고 있는지 선생님께 여쭤볼 때 가장 자주 씁니다.</div></div><button class="speak-btn" onclick="playAudio('Keep up with')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">8. Get along with</div><div class="vocab-meaning">~와 잘 어울리다 / 친하게 지내다</div><div class="vocab-tip">💡 [Day 12] 반 친구들과의 교우 관계 및 학교 적응을 확인할 때 유용한 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('Get along with')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">9. Early pick-up</div><div class="vocab-meaning">조퇴 (정규 하교 전 픽업)</div><div class="vocab-tip">💡 [Day 12] 병원 예약 등으로 아이를 일찍 데리고 나와야 할 때 포털 앱이나 이메일로 사전 신청합니다.</div></div><button class="speak-btn" onclick="playAudio('Early pick-up')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">10. School portal</div><div class="vocab-meaning">학교 포털 앱 / 학사 시스템</div><div class="vocab-tip">💡 [Day 12] 가정통신문 확인, 결석·조퇴 신청, 상담 예약이 이루어지는 학교 전용 온라인 시스템입니다.</div></div><button class="speak-btn" onclick="playAudio('School portal')">🔊</button></div>

                <!-- Day 13 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">11. Trim</div><div class="vocab-meaning">(끝부분만 살짝) 다듬다</div><div class="vocab-tip">💡 [Day 13] 전체 스타일은 유지하고 자란 끝부분만 다듬을 때 'Just a trim, please'라고 합니다.</div></div><button class="speak-btn" onclick="playAudio('Trim')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">12. Bangs / Fringe</div><div class="vocab-meaning">앞머리</div><div class="vocab-tip">💡 [Day 13] 미국식으로는 Bangs, 영국·말레이시아식으로는 Fringe라고도 많이 부릅니다.</div></div><button class="speak-btn" onclick="playAudio('Bangs and Fringe')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">13. Thin out</div><div class="vocab-meaning">머리 숱을 치다</div><div class="vocab-tip">💡 [Day 13] 더운 날씨에 아이 머리 숱이 많아 답답할 때 'thin out his/her hair'라고 요청하세요.</div></div><button class="speak-btn" onclick="playAudio('Thin out')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">14. Clippers</div><div class="vocab-meaning">바리깡 / 클리퍼</div><div class="vocab-tip">💡 [Day 13] 남자아이 옆·뒷머리를 밀 때 클리퍼 탭 번호(예: Number 3)를 지정해 주면 정확합니다.</div></div><button class="speak-btn" onclick="playAudio('Clippers')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">15. Eyebrow level</div><div class="vocab-meaning">눈썹 높이(길이)</div><div class="vocab-tip">💡 [Day 13] 앞머리가 너무 짧아지지 않도록 'right at the eyebrow level'처럼 기준점을 잡아주세요.</div></div><button class="speak-btn" onclick="playAudio('Eyebrow level')">🔊</button></div>

                <!-- Day 14 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">16. DuitNow QR</div><div class="vocab-meaning">말레이시아 통합 QR 결제·송금 시스템</div><div class="vocab-tip">💡 [Day 14] 분홍색 DuitNow QR 하나로 말레이시아 모든 은행 앱 및 eWallet 결제가 가능합니다.</div></div><button class="speak-btn" onclick="playAudio('DuitNow QR')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">17. TNG (Touch 'n Go) eWallet</div><div class="vocab-meaning">터치앤고 전자지갑 앱</div><div class="vocab-tip">💡 [Day 14] 여권 본인 인증을 마치면 QR 결제, 톨게이트 카드 연동, 계좌 이체까지 모두 가능합니다.</div></div><button class="speak-btn" onclick="playAudio('Touch and Go eWallet')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">18. Top up / Reload</div><div class="vocab-meaning">(잔액·데이터 등을) 충전하다</div><div class="vocab-tip">💡 [Day 14] 선불 유심이나 터치앤고 카드 잔액을 충전할 때 가장 흔히 쓰는 현지 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('Top up and Reload')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">19. Daily transfer limit</div><div class="vocab-meaning">일일 이체 한도</div><div class="vocab-tip">💡 [Day 14] 집세나 학비를 송금하기 전에 모바일 뱅킹 앱의 일일 이체 한도를 미리 확인하세요.</div></div><button class="speak-btn" onclick="playAudio('Daily transfer limit')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">20. Guardian visa</div><div class="vocab-meaning">가디언 비자 (동반 학부모 비자)</div><div class="vocab-tip">💡 [Day 14] 현지 은행 계좌 개설 시 여권, 가디언 비자 스티커, 학교 재학 확인서가 필요합니다.</div></div><button class="speak-btn" onclick="playAudio('Guardian visa')">🔊</button></div>

                <!-- Day 15 -->
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">21. Early check-in / Late check-out</div><div class="vocab-meaning">얼리 체크인 / 레이트 체크아웃</div><div class="vocab-tip">💡 [Day 15] 리조트 도착 시간이나 비행기 스케줄에 맞춰 프런트에 객실 여유를 문의해 볼 수 있습니다.</div></div><button class="speak-btn" onclick="playAudio('Early check-in and Late check-out')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">22. Extra bed</div><div class="vocab-meaning">추가 간이침대 (Rollaway bed)</div><div class="vocab-tip">💡 [Day 15] 아이들과 함께 투숙할 때 객실에 간이침대 추가를 요청하는 표현입니다.</div></div><button class="speak-btn" onclick="playAudio('Extra bed')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">23. Security deposit</div><div class="vocab-meaning">객실 보증금 (디파짓)</div><div class="vocab-tip">💡 [Day 15] 체크인 시 결제했다가 퇴실 시 이상이 없으면 돌려받는 보증금입니다.</div></div><button class="speak-btn" onclick="playAudio('Security deposit')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">24. Complimentary breakfast</div><div class="vocab-meaning">무료 포함 조식</div><div class="vocab-tip">💡 [Day 15] 객실 요금에 기본 포함된 아침 식사이며, 식당 위치와 운영 시간을 체크인 시 확인하세요.</div></div><button class="speak-btn" onclick="playAudio('Complimentary breakfast')">🔊</button></div>
                <div class="vocab-item"><div class="vocab-content"><div class="vocab-word">25. Housekeeping (Make up the room)</div><div class="vocab-meaning">객실 청소 (방 정리 요청)</div><div class="vocab-tip">💡 [Day 15] 외출 전 객실 정돈과 수건 교체를 요청할 때 'make up our room'이라고 표현합니다.</div></div><button class="speak-btn" onclick="playAudio('Make up the room')">🔊</button></div>
            </div>
        </section>

        <section>
            <div class="section-title">🗣️ 주간 베스트 핵심 패턴 5선</div>
            <div class="pattern-box">
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 1. Could you please check my tyre pressure and brake pads? <button class="speak-btn" onclick="playAudio('Could you please check my tyre pressure and brake pads?')">🔊</button></div>
                    <div class="pattern-example">[Day 11] 타이어 공기압이랑 브레이크 패드 좀 점검해 주시겠어요?</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 2. How is Mike keeping up with his classes lately? <button class="speak-btn" onclick="playAudio('How is Mike keeping up with his classes lately?')">🔊</button></div>
                    <div class="pattern-example">[Day 12] 요즘 마이크가 수업 진도는 잘 따라가고 있나요?</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 3. Could you thin out his hair a bit? It gets too hot here. <button class="speak-btn" onclick="playAudio('Could you thin out his hair a bit? It gets too hot here.')">🔊</button></div>
                    <div class="pattern-example">[Day 13] 아이 머리 숱을 조금 쳐주시겠어요? 여기 날씨가 더워서 땀이 많이 나요.</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 4. How can I increase my daily transfer limit on the mobile app? <button class="speak-btn" onclick="playAudio('How can I increase my daily transfer limit on the mobile app?')">🔊</button></div>
                    <div class="pattern-example">[Day 14] 모바일 앱에서 일일 이체 한도를 어떻게 늘릴 수 있나요?</div>
                </div>
                <div class="pattern-item">
                    <div class="pattern-title">Pattern 5. Could we get an extra bed and extra towels for the kids, please? <button class="speak-btn" onclick="playAudio('Could we get an extra bed and extra towels for the kids, please?')">🔊</button></div>
                    <div class="pattern-example">[Day 15] 아이들을 위해 엑스트라 베드 하나와 수건을 좀 더 받을 수 있을까요?</div>
                </div>
            </div>
        </section>

        <section>
            <div class="section-title">✍️ 3주차 실전 통합 퀴즈 (클릭 시 정답 확인)</div>
            <div class="quiz-box">
                <details class="quiz-item">
                    <summary>Q1. [Day 11] 세차장에서 외부 세차와 함께 실내 진공청소기 청소까지 세트로 요청할 때 쓰는 표현은?</summary>
                    <div class="quiz-answer-content">정답: Wash and vacuum, please.</div>
                </details>
                <details class="quiz-item">
                    <summary>Q2. [Day 12] 담임선생님께 "마이크가 수업 진도를 잘 따라가고 있나요?"를 영어로 물어보면?</summary>
                    <div class="quiz-answer-content">정답: How is Mike keeping up with his classes?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q3. [Day 13] 미용실에서 아이 머리가 너무 무겁고 더워 보일 때 "머리 숱을 조금 쳐주시겠어요?"를 영어로 말하면?</summary>
                    <div class="quiz-answer-content">정답: Could you thin out his/her hair a bit?</div>
                </details>
                <details class="quiz-item">
                    <summary>Q4. [Day 14] 터치앤고(TNG) 카드나 선불 유심에 '잔액을 충전하다'를 뜻하는 현지 영어 표현 두 가지는?</summary>
                    <div class="quiz-answer-content">정답: Top up 또는 Reload</div>
                </details>
                <details class="quiz-item">
                    <summary>Q5. [Day 15] 리조트 체크인 시간보다 일찍 도착했을 때 "혹시 얼리 체크인이 가능할까요?"를 영어로 물어보세요.</summary>
                    <div class="quiz-answer-content">정답: Is early check-in available (by any chance)?</div>
                </details>
            </div>
        </section>
    </div>
</article>"""

# 4. 기존 index.html에 새 Day 카드 누적 삽입
update_success = False
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
            update_success = True
        else:
            print(f"{day_title} 카드가 이미 존재합니다.")
            update_success = True
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

# 6. 왓츠앱(WhatsApp) 알림 전송 (Green API 연동 - 말레이시아 번호: +601123906456)
GREENAPI_ID_INSTANCE = os.getenv("GREENAPI_ID_INSTANCE", "710722770876")
GREENAPI_API_TOKEN = os.getenv("GREENAPI_API_TOKEN", "9fe88468b24248fd88bc903bfa5f8669c833de4baa8d4ccb97")
GREENAPI_CHAT_ID = os.getenv("GREENAPI_CHAT_ID", "601123906456@c.us")

def send_whatsapp_message(link_url, title_text):
    if not GREENAPI_ID_INSTANCE or not GREENAPI_API_TOKEN:
        print("WhatsApp(Green API) 인증 정보가 설정되지 않아 발송을 건너뜁니다.")
        return

    msg_text = (
        f"🌟 *[오늘의 영어 리포트 도착]*\n"
        f"{title_text}\n\n"
        f"👉 *오늘의 리포트 바로가기:*\n"
        f"{link_url}"
    )
    api_url = f"{p_https}api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}/sendMessage/{GREENAPI_API_TOKEN}"
    payload = {
        "chatId": GREENAPI_CHAT_ID,
        "message": msg_text
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        res = requests.post(api_url, data=data, headers=headers, timeout=20)
        print("WhatsApp(Green API) 전송 결과:", res.status_code, res.text)
    except Exception as e:
        print("WhatsApp 전송 오류:", e)

# 웹사이트 주소 결합 방식 및 정상 업데이트 시에만 카카오톡 및 왓츠앱 발송
MY_GITHUB_PAGES_URL = p_https + "docdaelove-sketch.github.io/english-day1-/"
if update_success:
    send_kakao_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
    send_whatsapp_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
else:
    print("카드 생성 실패로 인해 알림 발송을 건너뜁니다.")
