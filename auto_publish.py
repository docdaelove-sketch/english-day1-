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
        11: "차량 정비 및 주유소 이용 (세차, 엔진오일 교환, 타이어 공기압 점검)"
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

if GEMINI_KEY:
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

# 웹사이트 주소 결합 방식 및 정상 업데이트 시에만 카카오톡 발송
MY_GITHUB_PAGES_URL = p_https + "docdaelove-sketch.github.io/english-day1-/"
if update_success:
    send_kakao_message(MY_GITHUB_PAGES_URL, f"[{day_title}] {topic_desc}")
else:
    print("카드 생성 실패로 인해 카카오톡 알림 발송을 건너뜁니다.")
