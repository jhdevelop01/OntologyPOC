# Plan 01: Streamlit 대시보드

## 목표
Neo4j에 저장된 UPW 온톨로지 데이터를 시각화하는 웹 대시보드 구현

## 기술 스택
- **Streamlit**: Python 기반 웹 대시보드 프레임워크
- **neo4j Python driver**: Neo4j 연결
- **pandas**: 데이터 처리
- **plotly**: 인터랙티브 차트

## 기능 목록

### 1. 장비 현황 (Equipment Overview)
- 전체 장비 목록 테이블
- 장비별 센서 수, 운영 시간 표시
- 장비 타입별 필터링

### 2. 이상탐지 모니터링 (Anomaly Detection)
- Anomaly Score 기준 정렬된 목록
- Score > 0.5 하이라이트 (위험)
- 시간대별 이상탐지 차트

### 3. 고장 예측 (Failure Prediction)
- 예측된 고장 일정 타임라인
- Confidence Score 표시
- 잔여 수명(RUL) 게이지

### 4. 에너지 예측 (Energy Forecast)
- 96포인트 일일 에너지 예측 라인 차트
- 피크 시간대 하이라이트
- 총 에너지/피크 전력 KPI 카드

### 5. 정비 일정 (Maintenance Schedule)
- 캘린더 뷰 또는 타임라인
- 우선순위별 색상 구분
- 필터: 예방/예측/교정 정비

## 파일 구조
```
dashboard/
├── app.py              # Streamlit 메인 앱
├── pages/
│   ├── 1_equipment.py      # 장비 현황
│   ├── 2_anomaly.py        # 이상탐지
│   ├── 3_prediction.py     # 고장 예측
│   ├── 4_energy.py         # 에너지 예측
│   └── 5_maintenance.py    # 정비 일정
├── utils/
│   ├── neo4j_client.py     # Neo4j 연결 유틸
│   └── queries.py          # Cypher 쿼리 모음
├── requirements.txt
└── README.md
```

## Neo4j 연결 설정
```python
NEO4J_URI = "bolt://localhost:17687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
```

## 실행 방법
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

## 예상 결과
- 브라우저에서 `http://localhost:8501` 접속
- 5개 페이지로 구성된 대시보드
- Neo4j 데이터 실시간 조회 및 시각화
