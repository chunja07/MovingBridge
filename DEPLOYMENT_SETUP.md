# Replit Deployments 설정 가이드

## 필수 환경 변수 설정

Replit Deployments 페이지에서 다음 환경 변수들을 설정해야 합니다:

### 1. 필수 환경 변수
```
FLASK_ENV=production
SESSION_SECRET=your-very-secure-secret-key-here
```

### 2. 관리자 계정 (선택사항)
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-admin-password
```

### 3. 자동 제공되는 변수
- `DATABASE_URL`: Replit에서 자동으로 PostgreSQL 연결 정보 제공
- `REPLIT_DB_URL`: Replit 기본 데이터베이스 (사용하지 않음)

## 배포 설정 단계

1. **Replit Deployments 페이지 접속**
   - 프로젝트에서 "Deploy" 탭 클릭

2. **환경 변수 설정**
   - "Environment Variables" 섹션에서 위의 변수들 추가
   - `SESSION_SECRET`는 반드시 강력한 랜덤 문자열 사용

3. **도메인 설정**
   - Custom Domain: `movemove.co.kr`
   - SSL 인증서는 자동 발급됨

4. **배포 실행**
   - "Deploy" 버튼 클릭
   - 자동으로 운영 환경 설정 적용

## 주의사항

- **SESSION_SECRET**: 절대 기본값 사용 금지, 최소 32자 이상
- **FLASK_ENV**: 반드시 `production`으로 설정
- **데이터베이스**: PostgreSQL이 자동으로 생성됨
- **HTTPS**: 자동으로 강제 활성화됨

## 배포 후 확인사항

1. HTTPS 접속 확인
2. 데이터베이스 테이블 생성 확인
3. 관리자 로그인 확인
4. 보안 헤더 적용 확인

## 트러블슈팅

- 502 오류: 환경 변수 확인
- 데이터베이스 오류: DATABASE_URL 확인
- 로그인 불가: SESSION_SECRET 확인