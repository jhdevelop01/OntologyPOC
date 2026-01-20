# 서버 실행 가이드

## 사전 요구사항
- Docker Desktop 설치 및 실행 중

---

## 1. 터미널(iTerm2) 열기

## 2. 프로젝트 디렉토리로 이동
```bash
cd /Users/mckim64/Projects/OntologyPOC
```

## 3. 자주 쓰는 명령어

| 작업 | 명령어 |
|------|--------|
| **서버 시작** | `docker compose up -d` |
| **서버 중지** | `docker compose down` |
| **로그 보기** | `docker compose logs -f` |
| **상태 확인** | `docker compose ps` |
| **완전 초기화** | `docker compose down -v` |

## 4. 헬퍼 스크립트 사용 (선택)
```bash
./scripts/run.sh start      # 시작 + 준비 대기
./scripts/run.sh stop       # 중지
./scripts/run.sh import     # 온톨로지 임포트
./scripts/run.sh shell      # cypher-shell 열기
./scripts/run.sh validate   # TTL 파일 검증
```

## 5. 브라우저 접속
서버 시작 후 약 30~40초 대기:
```
http://localhost:17474
```

### 로그인 정보
| 항목 | 값 |
|------|-----|
| Connect URL | `neo4j://localhost:17687` |
| Username | `neo4j` |
| Password | `password123` |

---

## 전체 실행 예시

```bash
# 1. 터미널에서 프로젝트로 이동
cd /Users/mckim64/Projects/OntologyPOC

# 2. 서버 시작
docker compose up -d

# 3. 30초 대기 후 브라우저 열기
open http://localhost:17474

# 4. 작업 끝나면 중지
docker compose down
```

---

## 온톨로지 임포트 (최초 1회 또는 초기화 후)

```bash
docker exec -i neo4j-upw cypher-shell -u neo4j -p password123 < neo4j/import-docker.cypher
```

또는:
```bash
./scripts/run.sh import
```
