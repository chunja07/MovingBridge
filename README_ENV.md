# 환경 설정 가이드

## 개발 환경 vs 운영 환경

### 개발 환경 (Development)
- **데이터베이스**: SQLite (`movingbridge_dev.db`)
- **보안**: HTTPS 비활성화, CSP 완화
- **디버깅**: DEBUG=True, 상세 로깅
- **실행 방법**: `python run_dev.py`

### 운영 환경 (Production)
- **데이터베이스**: PostgreSQL (DATABASE_URL 필요)
- **보안**: HTTPS 강제, 엄격한 CSP
- **디버깅**: DEBUG=False, 최소 로깅
- **실행 방법**: `python run_prod.py`

## 환경 변수 설정

### 개발 환경에서 필요한 환경 변수
```bash
SESSION_SECRET=your-secret-key-here
FLASK_ENV=development
```

### 운영 환경에서 필요한 환경 변수
```bash
SESSION_SECRET=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=production
```

## 데이터베이스 초기화

### 개발 환경
```bash
python init_dev_db.py
```

### 운영 환경
```bash
python database_setup.py
```

## 서버 실행

### 개발 서버
```bash
python run_dev.py
```

### 운영 서버
```bash
python run_prod.py
```

## 환경별 특징

| 기능 | 개발 환경 | 운영 환경 |
|------|-----------|-----------|
| 데이터베이스 | SQLite | PostgreSQL |
| HTTPS | 비활성화 | 강제 활성화 |
| CSP | 완화된 정책 | 엄격한 정책 |
| 디버깅 | 활성화 | 비활성화 |
| 로깅 레벨 | DEBUG | INFO |
| 쿠키 보안 | 완화 | 엄격 |

## 배포 전 체크리스트

1. 환경 변수 설정 확인
2. 데이터베이스 연결 테스트
3. 보안 설정 검증
4. 성능 테스트 수행