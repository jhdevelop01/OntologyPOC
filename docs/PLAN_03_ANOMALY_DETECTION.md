# Plan 03: 이상탐지 모델

## 목표
센서 데이터를 기반으로 장비 이상을 탐지하는 ML 모델 구현

## 기술 스택
- **scikit-learn**: Isolation Forest, One-Class SVM
- **pandas/numpy**: 데이터 처리
- **joblib**: 모델 저장/로드
- **neo4j**: 데이터 소스 및 결과 저장

## 알고리즘 선택

### 1. Isolation Forest (주요)
- 비지도 학습 기반 이상탐지
- 고차원 데이터에 효과적
- 빠른 학습 및 추론

### 2. One-Class SVM (보조)
- 정상 데이터로만 학습
- 경계 기반 탐지

### 3. Statistical (기준선)
- Z-Score 기반 탐지
- 단순하고 해석 가능

## 파이프라인

```
[Neo4j 데이터] → [전처리] → [학습] → [추론] → [결과 저장]
```

1. **데이터 수집**: Neo4j에서 센서 관측 데이터 추출
2. **전처리**: 정규화, 결측치 처리, 특성 엔지니어링
3. **학습**: 정상 데이터로 모델 학습
4. **추론**: 새 데이터에 대해 이상 점수 계산
5. **저장**: 결과를 Neo4j에 저장

## 특성 (Features)

### 센서별 특성
- `value`: 현재 측정값
- `rolling_mean`: 이동 평균
- `rolling_std`: 이동 표준편차
- `rate_of_change`: 변화율
- `deviation_from_mean`: 평균 대비 편차

### 장비별 특성
- `operating_hours`: 운영 시간
- `sensor_correlation`: 센서 간 상관관계

## 파일 구조
```
ml/
├── anomaly_detection.py   # 메인 모델 클래스
├── data_loader.py         # Neo4j 데이터 로더
├── preprocessing.py       # 전처리 유틸
├── train.py               # 학습 스크립트
├── predict.py             # 추론 스크립트
├── models/                # 저장된 모델
│   └── .gitkeep
├── requirements.txt
└── README.md
```

## API 통합
- FastAPI 엔드포인트: `POST /api/anomalies/detect`
- 입력: 센서 ID + 측정값
- 출력: 이상 점수 + 라벨

## 평가 지표
- Precision/Recall (라벨 있는 경우)
- Anomaly Score 분포
- False Positive Rate

## 실행 방법
```bash
cd ml

# 학습
python train.py

# 추론
python predict.py --sensor VIB-001 --value 5.2
```
