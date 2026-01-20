# UPW Process REST API

Neo4j 기반 UPW 공정 온톨로지 REST API

## 설치

```bash
cd api
pip install -r requirements.txt
```

## 실행

```bash
# Neo4j 서버가 실행 중이어야 함
uvicorn main:app --reload --port 8000
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 엔드포인트

### Equipment
- `GET /api/equipment` - 전체 장비 목록
- `GET /api/equipment/{id}` - 장비 상세
- `GET /api/equipment/{id}/sensors` - 장비 센서 목록

### Sensors
- `GET /api/sensors` - 전체 센서 목록
- `GET /api/sensors/{id}` - 센서 상세
- `GET /api/sensors/{id}/observations` - 센서 관측 데이터

### Anomalies
- `GET /api/anomalies` - 이상탐지 목록
- `GET /api/anomalies?threshold=0.5` - 임계값 필터링

### Predictions
- `GET /api/predictions/failure` - 고장 예측
- `GET /api/predictions/energy` - 에너지 예측

### Maintenance
- `GET /api/maintenance` - 정비 일정
- `GET /api/maintenance?status=Scheduled` - 상태 필터링

### Health
- `GET /health` - 서버 상태

## 환경 변수

```bash
export NEO4J_URI="bolt://localhost:17687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password123"
```
