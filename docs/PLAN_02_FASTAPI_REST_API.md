# Plan 02: FastAPI REST API

## 목표
Neo4j 온톨로지 데이터를 외부 시스템에서 활용할 수 있는 RESTful API 제공

## 기술 스택
- **FastAPI**: 고성능 Python 웹 프레임워크
- **Pydantic**: 데이터 검증 및 직렬화
- **neo4j Python driver**: Neo4j 연결
- **uvicorn**: ASGI 서버

## API 엔드포인트

### Equipment API
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/equipment` | 전체 장비 목록 |
| GET | `/api/equipment/{id}` | 장비 상세 정보 |
| GET | `/api/equipment/{id}/sensors` | 장비의 센서 목록 |

### Sensor API
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/sensors` | 전체 센서 목록 |
| GET | `/api/sensors/{id}` | 센서 상세 정보 |
| GET | `/api/sensors/{id}/observations` | 센서 관측 데이터 |

### Anomaly API
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/anomalies` | 이상탐지 목록 |
| GET | `/api/anomalies?threshold=0.5` | 임계값 필터링 |

### Prediction API
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/predictions/failure` | 고장 예측 목록 |
| GET | `/api/predictions/energy` | 에너지 예측 |
| GET | `/api/predictions/energy/{date}` | 특정 일자 예측 |

### Maintenance API
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/maintenance` | 정비 일정 목록 |
| GET | `/api/maintenance?status=Scheduled` | 상태 필터링 |

### Health & Docs
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 서버 상태 확인 |
| GET | `/docs` | Swagger UI (자동 생성) |
| GET | `/redoc` | ReDoc 문서 |

## 파일 구조
```
api/
├── main.py              # FastAPI 앱 진입점
├── routers/
│   ├── equipment.py     # 장비 API
│   ├── sensors.py       # 센서 API
│   ├── anomalies.py     # 이상탐지 API
│   ├── predictions.py   # 예측 API
│   └── maintenance.py   # 정비 API
├── models/
│   ├── equipment.py     # Pydantic 모델
│   ├── sensor.py
│   ├── anomaly.py
│   ├── prediction.py
│   └── maintenance.py
├── services/
│   └── neo4j_service.py # Neo4j 비즈니스 로직
├── core/
│   ├── config.py        # 설정
│   └── database.py      # DB 연결
├── requirements.txt
└── README.md
```

## Response 형식
```json
{
  "success": true,
  "data": [...],
  "count": 10,
  "message": null
}
```

## 실행 방법
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## 예상 결과
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:8000/api/equipment` - JSON 응답
