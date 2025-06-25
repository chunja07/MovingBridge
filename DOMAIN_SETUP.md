# 도메인 연결 설정 가이드

## 현재 상황
- 도메인: `movemove.co.kr`
- 등록업체: 가비아 (gabia.co.kr)
- 상태: 도메인 등록됨, DNS 레코드 미설정

## 해결 방법

### 1. 가비아 DNS 설정 (www 없이 사용)
가비아 관리자 페이지에서 다음 DNS 레코드를 추가하세요:

```
타입: A
호스트명: @
값: [Replit 배포 IP 주소]
TTL: 3600
```

### 1-1. 선택사항: www 리다이렉트 설정
사용자가 www.movemove.co.kr로 접속할 경우 대비:

```
타입: CNAME
호스트명: www
값: movemove.co.kr
TTL: 3600
```

### 2. Replit 배포 IP 확인
1. Replit Deployments 페이지에서 배포 완료 후
2. 배포된 앱의 IP 주소 확인
3. 해당 IP를 가비아 DNS에 등록

### 3. 대안: Replit DNS 사용
가비아에서 네임서버를 다음으로 변경:

```
ns1.replit.com
ns2.replit.com
```

그 후 Replit Deployments에서 Custom Domain 설정

## 확인 방법
DNS 전파 완료까지 최대 24-48시간 소요
```bash
# DNS 전파 확인
nslookup movemove.co.kr

# 웹사이트 접속 테스트
curl -I https://movemove.co.kr
```

## 주의사항
- DNS 전파는 시간이 걸림 (최대 48시간)
- HTTPS 인증서는 도메인 연결 후 자동 발급
- 중간에 설정 변경 시 전파 시간 초기화될 수 있음