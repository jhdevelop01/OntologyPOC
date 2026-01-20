# 이상탐지 모델 (Anomaly Detection)

센서 데이터 기반 장비 이상 탐지 ML 모델

## 설치

```bash
cd ml
pip install -r requirements.txt
```

## 학습

```bash
# 합성 데이터로 학습 (Neo4j 없이 테스트)
python train.py --synthetic

# Neo4j 데이터로 학습
python train.py

# 특정 센서 데이터로 학습
python train.py --sensor VIB-001

# 알고리즘 선택
python train.py --algorithm isolation_forest  # 기본값
python train.py --algorithm one_class_svm
python train.py --algorithm zscore
```

## 추론

```bash
# 단일 값 예측
python predict.py --value 5.2

# 특정 센서의 전체 데이터 예측
python predict.py --batch --sensor VIB-001

# 결과를 Neo4j에 저장
python predict.py --value 5.2 --sensor VIB-001 --save
```

## 알고리즘

### Isolation Forest (기본)
- 비지도 학습 기반
- 이상치를 빠르게 격리
- 고차원 데이터에 효과적

### One-Class SVM
- 정상 데이터 경계 학습
- 견고한 이상 탐지

### Z-Score
- 통계 기반 단순 방법
- 해석 가능

## 출력 형식

| Score 범위 | Label | 의미 |
|-----------|-------|------|
| 0.0 - 0.5 | normal | 정상 |
| 0.5 - 0.7 | warning | 주의 |
| 0.7 - 1.0 | anomaly | 이상 |

## 모델 파일

학습된 모델은 `models/` 디렉토리에 저장됩니다.
- `anomaly_model.joblib`: 기본 모델
