# 특용작물 대사체 통합 디지털 플랫폼

특용작물 대사체 통합 데이터 생산·표준화 및 디지털 활용기술 개발을 위한 프로토타입 웹 플랫폼입니다.

## 2-Track 구조

| Track | 대상 | 핵심 기능 |
|-------|------|-----------|
| **Research Portal** | 연구자 | Compound Catalog, AI 원산지 판별, 표준 데이터 패키지, QC 검증 |
| **Public Portal** | 대국민 (소비자·농업인·지자체) | 작목 대시보드, 성분 신뢰지수, 성분 백과, 지역별 성분 지도 |

## 기술 스택

- **Backend**: Django 5.x (Python)
- **Frontend**: Django 템플릿 + Tailwind CSS (CDN)
- **Chart**: Chart.js (CDN)
- **DB**: SQLite (샘플 데이터)
- **Font**: Noto Sans KR (Google Fonts CDN)

## 실행 방법

```bash
# 의존성 설치
pip install django

# DB 마이그레이션
python manage.py migrate

# 샘플 데이터 시딩
python manage.py seed_data

# 서버 실행
python manage.py runserver 6321
```

http://127.0.0.1:6321/ 접속

## 페이지 구조

```
/                       랜딩페이지 (2-Track 선택)
/research/              연구자 포털 메인
/research/catalog/      Compound Catalog (3-컬럼: 필터 | 목록 | 상세)
/public/                대국민 포털 메인
/public/dashboard/      작목 상세 대시보드 (3-컬럼: 비교 | 차트 | AI해설)
```

## 프로젝트 구조

```
metabolome_platform/
├── config/                 Django 프로젝트 설정
├── core/                   메인 앱
│   ├── models.py           Crop, Compound, EnvironmentData
│   ├── views.py            뷰 함수
│   ├── urls.py             URL 라우팅
│   └── management/commands/
│       └── seed_data.py    샘플 데이터 시딩
├── templates/
│   ├── base.html           공통 베이스 (Tailwind, Chart.js, 폰트)
│   ├── landing.html        랜딩페이지
│   ├── research/
│   │   ├── index.html      연구자 포털 메인
│   │   └── catalog.html    Compound Catalog
│   └── public/
│       ├── index.html      대국민 포털 메인
│       └── dashboard.html  작목 상세 대시보드
└── static/
    ├── css/
    └── images/
```

## 샘플 데이터

계획서 기반 7종 작물, 16종 성분:

| 작물 | 주요 성분 |
|------|-----------|
| 인삼 | Ginsenoside Rg1, Rb1, Re, Rc |
| 당귀 | Decursin, Decursinol angelate, Nodakenin |
| 황기 | Astragaloside IV, Calycosin |
| 결명자 | Chrysophanol |
| 단삼 | Tanshinone IIA, Salvianolic acid B |
| 상황버섯 | Beta-glucan |
| 동충하초 | Cordycepin |
