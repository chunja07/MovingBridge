# 배포 가이드

## 현재 환경 구성

### 개발 환경 (Replit 프리뷰)
- **데이터베이스**: SQLite (`movingbridge_dev.db`)
- **보안**: HTTP 허용, 디버깅 활성화
- **용도**: 기능 개발 및 테스트
- **접근**: Replit 프리뷰 URL

### 운영 환경 (실제 배포)
- **데이터베이스**: PostgreSQL (Replit 제공)
- **보안**: HTTPS 강제, 보안 헤더 활성화
- **용도**: 실제 서비스 운영
- **접근**: 배포된 도메인 (movemove.co.kr)

## 배포 과정

1. **개발 단계**
   - Replit 프리뷰에서 기능 개발
   - SQLite 데이터베이스로 테스트
   - 기능 완성 확인

2. **배포 단계**
   ```bash
   # 환경 변수 설정
   export FLASK_ENV=production
   
   # 운영 데이터베이스 초기화 (최초 1회)
   python database_setup.py
   
   # 배포 실행
   python run_prod.py
   ```

3. **배포 후 확인**
   - HTTPS 접속 확인
   - 데이터베이스 연결 확인
   - 보안 헤더 적용 확인

## 주의사항

- **데이터 분리**: 개발용 SQLite와 운영용 PostgreSQL은 완전 분리
- **설정 자동 전환**: FLASK_ENV 변수로 자동 환경 감지
- **보안**: 운영 환경에서는 HTTPS 필수
- **테스트**: 프리뷰에서 충분히 테스트 후 배포