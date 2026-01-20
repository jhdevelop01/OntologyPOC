# UPW Process Dashboard

Neo4j 기반 UPW 공정 온톨로지 시각화 대시보드

## 설치

```bash
cd dashboard
pip install -r requirements.txt
```

## 실행

```bash
# Neo4j 서버가 실행 중이어야 함
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 페이지 구성

| 페이지 | 설명 |
|--------|------|
| **Home** | 전체 요약 KPI, 이상탐지/고장예측 미리보기 |
| **Equipment** | 장비 목록, 타입별 분포, 센서 현황 |
| **Anomaly** | 이상탐지 목록, Score 분포 차트 |
| **Prediction** | 고장 예측 타임라인, RUL 현황 |
| **Energy** | 96포인트 에너지 예측 차트, 시간대별 분석 |
| **Maintenance** | 정비 일정 목록, 우선순위별 필터 |

## 환경 변수

```bash
export NEO4J_URI="bolt://localhost:17687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password123"
```

## 필요 조건

- Neo4j 서버 실행 중
- 온톨로지 데이터 임포트 완료
