# 특용작물 대사체 통합 디지털 플랫폼 — 프로토타입 개발 가이드

## ⚠️ 반드시 지켜야 할 원칙

1. **RFP와 계획서에 명시된 내용만 사용** — 없는 기능/콘텐츠 절대 추가 금지
2. **세부 로직 구현 X** — 과제 서류평가 통과 후 발표평가용 데모 수준
3. **디자인: 글씨 크게** — 기본 16px, 제목 24~32px, 핵심 수치 40px+
4. **레퍼런스 이미지 2장의 컨셉 유지** — 다크 네이비 헤더 + 화이트 바디 + 카드형
5. **인실리콕스 입장에서 개발하는 플랫폼** — 우리가 만드는 것
6. **2-Track 구조 필수** — 연구자용(Research Portal) / 대국민용(Public Portal) 분리

---

## 1. 기술 스택

| 항목 | 기술 | 비고 |
|------|------|------|
| 백엔드 | Django 5.x | Python 기반 |
| 프론트 | Django 템플릿 + Tailwind CSS (CDN) | 빌드 없이 CDN |
| 차트 | Chart.js (CDN) | 바차트, 비교차트 |
| DB | SQLite | Django 기본, 샘플 데이터용 |
| 아이콘 | Heroicons 또는 Lucide (CDN) | 선택 |

### Tailwind CDN 사용법 (base.html에 추가)
```html
<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          'navy': '#1a1f36',
          'navy-light': '#2d3348',
          'accent': '#2563eb',
          'accent-light': '#3b82f6',
        },
        fontSize: {
          'display': ['2.5rem', { lineHeight: '1.2' }],
          'heading': ['1.75rem', { lineHeight: '1.3' }],
          'subheading': ['1.25rem', { lineHeight: '1.4' }],
          'body-lg': ['1.125rem', { lineHeight: '1.6' }],
        }
      }
    }
  }
</script>
```

### Chart.js CDN
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

---

## 2. 프로젝트 구조

```
metabolome_platform/
├── manage.py
├── config/                        # Django 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                          # 메인 앱
│   ├── __init__.py
│   ├── models.py                  # DB 모델
│   ├── views.py                   # 뷰 함수
│   ├── urls.py                    # URL 라우팅
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_data.py       # python manage.py seed_data
├── templates/
│   ├── base.html                  # 공통 베이스 (Tailwind CDN, 폰트, 메타)
│   ├── landing.html               # 랜딩페이지 (2-Track 선택)
│   ├── research/
│   │   ├── base_research.html     # 연구자용 베이스 (네이비 헤더 "RESEARCH PORTAL")
│   │   ├── index.html             # 연구자 포털 메인
│   │   └── catalog.html           # Compound Catalog 페이지
│   └── public/
│       ├── base_public.html       # 대국민용 베이스 (네이비 헤더 "PUBLIC PORTAL")
│       ├── index.html             # 대국민 포털 메인
│       └── dashboard.html         # 작목 상세 대시보드
├── static/
│   ├── css/
│   │   └── custom.css             # 추가 커스텀 스타일
│   └── images/                    # 필요 시 정적 이미지
└── requirements.txt
```

---

## 3. URL 구조

```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# core/urls.py
urlpatterns = [
    path('', views.landing, name='landing'),                         # 랜딩
    path('research/', views.research_index, name='research_index'),   # 연구자 포털 메인
    path('research/catalog/', views.research_catalog, name='research_catalog'),  # Compound Catalog
    path('public/', views.public_index, name='public_index'),         # 대국민 포털 메인
    path('public/dashboard/', views.public_dashboard, name='public_dashboard'),  # 작목 대시보드
]
```

---

## 4. DB 모델 (간단하게, 발표용)

```python
# core/models.py

class Crop(models.Model):
    """특용작물"""
    name_ko = models.CharField(max_length=100)        # 인삼, 당귀, 황기 등
    name_en = models.CharField(max_length=100)        # Ginseng, Angelica 등
    name_scientific = models.CharField(max_length=200) # 학명
    plant_part = models.CharField(max_length=50)       # 뿌리, 종자, 지상부 등
    origin = models.CharField(max_length=100)          # 금산, 풍기, 중국 등
    year = models.IntegerField(default=2025)

    def __str__(self):
        return f"{self.name_ko} ({self.name_en})"


class Compound(models.Model):
    """대사체 성분"""
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='compounds')
    name = models.CharField(max_length=200)            # Ginsenoside Rg1 등
    annotation_level = models.CharField(max_length=10)  # L1, L2, L3
    source = models.CharField(max_length=20)            # IN-HOUSE, PUBLIC
    score = models.IntegerField(default=0)              # 0~100
    similarity = models.FloatField(default=0.0)         # 0~1
    qc_status = models.CharField(max_length=20)         # PASS, REVIEW, FAIL

    # 성분 정보 (간단히)
    compound_class = models.CharField(max_length=100, blank=True)  # Saponin, Flavonoid 등
    molecular_weight = models.FloatField(null=True, blank=True)
    retention_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class EnvironmentData(models.Model):
    """지역·환경 지표 (공공API 연계 예시용)"""
    region = models.CharField(max_length=100)           # 강원도 평창군 등
    avg_temperature = models.FloatField()               # 연평균 기온 (°C)
    avg_rainfall = models.FloatField()                  # 연평균 강수량 (mm)
    soil_grade = models.CharField(max_length=10)        # A, B, C 등급

    def __str__(self):
        return self.region
```

---

## 5. 샘플 시드 데이터

```python
# core/management/commands/seed_data.py
# python manage.py seed_data 로 실행

# 계획서에 언급된 작물 사용:
# 인삼(Ginseng), 당귀(Angelica), 황기(Astragalus), 결명자(Cassia),
# 단삼(Salvia), 상황버섯(Phellinus), 동충하초(Cordyceps)

# 계획서에 언급된 성분 사용:
# Ginsenoside Rg1, Decursin, Astragaloside IV, Baicalin,
# Beta-glucan, Cordycepin 등

# 환경 데이터:
# 강원도 평창군, 충남 금산군, 경북 영주시, 전남 진도군 등
```

**시드 데이터는 계획서/레퍼런스 이미지에 나온 작물·성분명만 사용할 것.**

---

## 6. 각 페이지별 구현 상세

### 6-1. 랜딩페이지 (landing.html)

**레이아웃:**
- 상단: 플랫폼 제목 (큰 글씨)
  - "특용작물 대사체 통합 디지털 플랫폼"
  - 부제: "특용작물 대사체 통합 데이터 생산·표준화 및 디지털 활용기술 개발"
- 중단: 핵심 수치 카드 3개 (큰 숫자)
  - "80종" — 특용작물 대사체 DB 구축 목표
  - "50종" — 신규 대사체 데이터 생산
  - "2-Track" — 연구자/대국민 서비스 분리
- 하단: 2-Track 선택 카드 (큰 클릭 영역)
  - 좌측 카드: "RESEARCH PORTAL — 연구자용 서비스" → /research/
  - 우측 카드: "PUBLIC PORTAL — 대국민 서비스" → /public/

**디자인:**
- 배경: 화이트 또는 매우 밝은 그레이
- 카드: 그림자 + 호버 효과
- 2-Track 선택 카드는 크게 (최소 높이 200px)

---

### 6-2. Research Portal — 메인 (research/index.html)

**레이아웃:**
- 네이비 헤더: "RESEARCH PORTAL 연구자용 서비스" + 우측 "2-TRACK: RESEARCH" 배지
- 검색 바: "Search sample, compound, feature"
- 브레드크럼: HOME > METABOLOMICS DB > RESEARCH PORTAL
- 주요 기능 카드 (계획서 표-4 기반):
  1. "Compound Catalog" — 데이터 탐색·검색 → /research/catalog/
  2. "AI 기반 원산지 판별" — 활용모델 (화면만, 동작X)
  3. "표준 데이터 패키지" — 다운로드 및 API (화면만)
  4. "QC 검증 및 버전관리" — 릴리즈 관리 (화면만)

---

### 6-3. Research Portal — Compound Catalog (research/catalog.html)

**★ 레퍼런스 이미지 KakaoTalk_Photo_001 기반으로 구현 ★**

**3-컬럼 레이아웃:**

**좌측 사이드바 (조건 기반 탐색 FILTERS):**
- 작목 (CROP): 드롭다운 — 전체 선택, 인삼, 당귀, 황기 등
- 부위 (PLANT PART): 드롭다운 — 전체 선택, 뿌리, 종자, 지상부
- 산지 (ORIGIN): 드롭다운 — 전체 선택, 금산, 풍기, 중국 등
- 연도 (YEAR): 드롭다운 — 전체 선택, 2025 등
- QC 상태 (QC STATUS): 드롭다운 — PASS (기본값)

**중앙 (COMPOUND CATALOG):**
- 상단: "총 N건 중 예시: 6개 표시"
- 테이블 행 (각 행에):
  - 성분명 + 유래 작물명
  - Annotation Level 배지 (L1, L2, L3)
  - Source 배지 (IN-HOUSE: 노란색, PUBLIC: 파란색)
  - Score (S:0.94 형식)
  - 점수 (96, 89, 84 등 큰 숫자)
  - QC Status (PASS: 녹색, REVIEW: 주황)
- "+ VIEW MORE" 버튼

**우측 상세 패널 (성분 선택 시):**
- 성분명 + LEVEL 배지
- 유래: "(인삼 유래 예시)"
- 메타: 작목, 부위, 산지, 연도
- 탭: 개요 | 스펙트럼 | QC | 다운로드 및 API | 분석
- 활용모델 (RESEARCH MODEL):
  - ○ 원산지 판별(모델)
  - ○ 성분 특성 및 패턴 분석
- 근거 및 해석:
  - TOP 3 CONTRIBUTION (가로 바: Saponin 65%, Sugar 25% 등)
- QUICK ANALYSIS:
  - 원산지 판별 결과 [HIGH] 배지
  - SCORE: 96, SIMILARITY: 0.94
- 데이터 패키지 다운로드 버튼

**하단 (전문가용 근거 분석 CONCEPT IMAGE):**
- 3개 카드: A) ANNOTATION LEVEL, B) LIBRARY MATCH, C) SCORE
- 이 영역은 이미지 placeholder 또는 간단한 도식으로 처리

---

### 6-4. Public Portal — 메인 (public/index.html)

**레이아웃:**
- 네이비 헤더: "PUBLIC PORTAL 대국민 서비스" + 검색바 + 우측 "2-TRACK: PUBLIC" 배지 + "RELEASE V1.0"
- "50종 DB 구축 · 80종 확장" 배지 (노란색/초록색)
- 주요 기능 카드 (계획서 표-5 기반):
  1. "작목 상세 대시보드" — 탐색 및 비교 → /public/dashboard/
  2. "성분 기반 원산지·진위성 신뢰지수" — 소비자용 (화면만)
  3. "특용작물 성분 백과" — 쉬운 언어 (화면만)
  4. "지역별 성분 지도" — 메타볼로믹스 지리정보 (화면만)

---

### 6-5. Public Portal — 작목 상세 대시보드 (public/dashboard.html)

**★ 레퍼런스 이미지 KakaoTalk_Photo_002 기반으로 구현 ★**

**3-컬럼 레이아웃:**

**좌측 사이드바 (탐색 및 비교):**
- 탭 3개: 작목 | 성분 | 지역
- 작목 선택: 드롭다운 (인삼 Ginseng 등)
- 성분 선택: 드롭다운 (Ginsenoside All 등)
- 비교 타겟 (P1):
  - TARGET A: 인삼 (뿌리) [ROOT] 배지
  - ⇌ 아이콘
  - TARGET B: 황기 (뿌리) [ROOT] 배지
- "비교 분석 적용" 버튼 (네이비, 큰 버튼)

**중앙:**
- **작목 상세 대시보드** 제목 + [N=1,240] 배지
  - 부제: "인삼 vs 황기 분석 데이터 및 공공 API 연계 지표"
- **지역·환경 지표** 카드 (가로 3개, API 기반 표시):
  - 📍 지역·환경 지표: 강원도 평창군
  - 연평균 기온: 13.2 °C (큰 숫자)  — "API 기반"
  - 연평균 강수량: 1,240 mm (큰 숫자) — "API 기반"
  - 토양질 지수: B등급 (큰 글자) — "API 기반"
- **성분 분포 요약** (가로 바 차트 — Chart.js):
  - Rg1, Rb1, Re, Rc 등 성분별 바
- **비교 결과 분석** (그룹 바 차트 — Chart.js):
  - 인삼 vs 황기 성분별 비교

- **대국민 산출물 미리보기 (P4 CARD):**
  - 카드 형태: 작물 이미지 placeholder + "인삼 핵심 성분 요약 카드"
  - 설명: "대중이 이해하기 쉬운 용어로 풀어낸 인삼 핵심 성분 분석 및 효능 정보 카드입니다."
  - [더보기] 링크, 다운로드 아이콘

**우측 패널 (AI 요약·비교·해설):**
- 헤더: "AI 요약·비교·해설" + "대국민 AI 콘텐츠 (근거 포함)" 배지
- **AI 해설 콘텐츠:**
  - "인삼은 황기 대비 사포닌(Rg1) 1.2배 높음. 지역 기후가 성분 축적에 기여함." [더보기]
- **활용 시나리오:**
  - 🏛 정책: 지역별 지표 요약, 정책용 보고자료
  - 🏭 산업: 후보 성분 비교, R&D 의사결정 참고
  - 🌾 농업인: 재배 환경 이해, 현장 의사결정 보조
- **활용모델 (현장 활용):**
  - · 원산지 확인 및 위변조 이해
  - · 성분 기반 품질 선택 가이드
  - · 환경 기반 해석(공공 API)
- **불확실성 및 해상도 안내:**
  - ⓘ "분석 결과는 표본 및 해상도에 따라 차이가 있을 수 있음." [상세]

**하단 바:**
- 카드 및 리포트 (OUTPUT DOWNLOADS):
  - [📋 요약 카드] [⇌ 비교 카드] 버튼
  - [대중용 요약 카드 저장] [📄 대중용 리포트(PDF) 출력] [정책용 요약 리포트(PDF)] 버튼

---

## 7. 디자인 시스템

### 색상 (레퍼런스 이미지 기반)
```
네이비 (헤더/주요 배경): #1a1f36
네이비 라이트 (호버):     #2d3348
블루 액센트:              #2563eb
블루 라이트:              #3b82f6
노란 배지 (IN-HOUSE):     #f59e0b / bg-yellow-100
파란 배지 (PUBLIC):        #3b82f6 / bg-blue-100
녹색 (PASS):              #10b981
주황 (REVIEW):            #f97316
빨간 (FAIL):              #ef4444
회색 배경:                #f8fafc
카드 배경:                #ffffff
텍스트:                   #1e293b
보조 텍스트:              #64748b
```

### 타이포그래피 (글씨 크게 원칙)
```
플랫폼 제목:    text-3xl ~ text-4xl (30~36px) font-bold
페이지 제목:    text-2xl ~ text-3xl (24~30px) font-bold
섹션 제목:      text-xl (20px) font-semibold
카드 핵심 수치:  text-4xl ~ text-5xl (36~48px) font-bold
본문:           text-base ~ text-lg (16~18px)
보조/캡션:      text-sm (14px) text-gray-500
```

### 레이아웃 패턴
```
네이비 헤더 (고정):        h-16, bg-navy, 좌: 로고/타이틀, 중: 검색바, 우: 2-TRACK 배지
3-컬럼 (catalog/dashboard): 좌 w-64 | 중 flex-1 | 우 w-96
카드:                      bg-white rounded-lg shadow-sm border p-6
배지:                      px-3 py-1 rounded-full text-sm font-medium
버튼 (Primary):            bg-navy text-white px-6 py-3 rounded-lg text-lg
```

### 헤더 구조 (두 포털 공통)
```html
<!-- Research Portal 헤더 -->
<header class="bg-navy text-white h-16 flex items-center px-6 justify-between">
  <div class="flex items-center gap-4">
    <h1 class="text-xl font-bold">RESEARCH PORTAL</h1>
    <span class="text-sm text-gray-300">연구자용 서비스</span>
  </div>
  <div><!-- 검색바 --></div>
  <span class="border border-blue-400 text-blue-400 px-3 py-1 rounded text-sm">2-TRACK: RESEARCH</span>
</header>

<!-- Public Portal 헤더 -->
<header class="bg-navy text-white h-16 flex items-center px-6 justify-between">
  <div class="flex items-center gap-4">
    <h1 class="text-xl font-bold">PUBLIC PORTAL</h1>
    <span class="text-sm text-gray-300">대국민 서비스</span>
  </div>
  <div><!-- 검색바 --></div>
  <div class="flex gap-2">
    <span class="bg-blue-600 text-white px-3 py-1 rounded text-sm">2-TRACK: PUBLIC</span>
    <span class="border border-gray-400 text-gray-300 px-3 py-1 rounded text-sm">RELEASE V1.0</span>
  </div>
</header>
```

---

## 8. 개발 순서 (Claude Code 작업 순서)

### Phase 1: 프로젝트 기반
```bash
# 1. Django 프로젝트 생성
django-admin startproject config .
python manage.py startapp core

# 2. settings.py 설정 (INSTALLED_APPS, TEMPLATES, STATIC 등)
# 3. models.py 작성
# 4. makemigrations + migrate
# 5. seed_data 커맨드 작성 및 실행
```

### Phase 2: 템플릿 뼈대
```
1. base.html — Tailwind CDN, Chart.js CDN, 공통 메타, 폰트
2. landing.html — 랜딩페이지 완성
3. base_research.html — 연구자용 베이스 레이아웃 (네이비 헤더)
4. base_public.html — 대국민용 베이스 레이아웃 (네이비 헤더)
```

### Phase 3: 핵심 페이지
```
5. research/index.html — 연구자 포털 메인
6. research/catalog.html — ★ Compound Catalog (3-컬럼, 핵심)
7. public/index.html — 대국민 포털 메인
8. public/dashboard.html — ★ 작목 대시보드 (3-컬럼, 핵심)
```

### Phase 4: 스타일 마무리
```
9. 전체 스타일 통일 및 다듬기
10. 차트 데이터 연동 (Chart.js)
11. 반응 없는 버튼/링크에 "개발 예정" 표시 또는 비활성화 처리
```

---

## 9. views.py 기본 구조

```python
from django.shortcuts import render
from .models import Crop, Compound, EnvironmentData


def landing(request):
    """랜딩페이지"""
    crop_count = Crop.objects.values('name_ko').distinct().count()
    compound_count = Compound.objects.count()
    context = {
        'crop_count': crop_count,
        'compound_count': compound_count,
    }
    return render(request, 'landing.html', context)


def research_index(request):
    """연구자 포털 메인"""
    return render(request, 'research/index.html')


def research_catalog(request):
    """Compound Catalog — 필터 + 목록 + 상세"""
    # GET 파라미터로 필터
    crop_filter = request.GET.get('crop', '')
    part_filter = request.GET.get('part', '')
    origin_filter = request.GET.get('origin', '')
    qc_filter = request.GET.get('qc', 'PASS')

    compounds = Compound.objects.select_related('crop').all()

    if crop_filter:
        compounds = compounds.filter(crop__name_ko=crop_filter)
    if part_filter:
        compounds = compounds.filter(crop__plant_part=part_filter)
    if origin_filter:
        compounds = compounds.filter(crop__origin=origin_filter)
    if qc_filter:
        compounds = compounds.filter(qc_status=qc_filter)

    # 필터 옵션용
    crops = Crop.objects.values_list('name_ko', flat=True).distinct()
    parts = Crop.objects.values_list('plant_part', flat=True).distinct()
    origins = Crop.objects.values_list('origin', flat=True).distinct()

    # 상세 보기 (선택된 성분)
    selected_id = request.GET.get('selected', None)
    selected_compound = None
    if selected_id:
        selected_compound = Compound.objects.select_related('crop').filter(id=selected_id).first()

    context = {
        'compounds': compounds,
        'selected': selected_compound,
        'crops': crops,
        'parts': parts,
        'origins': origins,
        'current_crop': crop_filter,
        'current_part': part_filter,
        'current_origin': origin_filter,
        'current_qc': qc_filter,
    }
    return render(request, 'research/catalog.html', context)


def public_index(request):
    """대국민 포털 메인"""
    return render(request, 'public/index.html')


def public_dashboard(request):
    """작목 상세 대시보드"""
    crop_a_name = request.GET.get('crop_a', '인삼')
    crop_b_name = request.GET.get('crop_b', '황기')

    crop_a = Crop.objects.filter(name_ko=crop_a_name).first()
    crop_b = Crop.objects.filter(name_ko=crop_b_name).first()

    compounds_a = Compound.objects.filter(crop=crop_a) if crop_a else []
    compounds_b = Compound.objects.filter(crop=crop_b) if crop_b else []

    # 환경 데이터
    env_data = EnvironmentData.objects.first()  # 기본값

    crops = Crop.objects.values_list('name_ko', flat=True).distinct()

    context = {
        'crop_a': crop_a,
        'crop_b': crop_b,
        'compounds_a': compounds_a,
        'compounds_b': compounds_b,
        'env_data': env_data,
        'crops': crops,
    }
    return render(request, 'public/dashboard.html', context)
```

---

## 10. 계획서 기반 콘텐츠 (그대로 사용할 텍스트)

### 연구자용 콘텐츠 (표-4 기반)
| 콘텐츠 | 설명 |
|--------|------|
| 스펙트럼 레퍼런스 라이브러리 포털 | GNPS/MetaboLights/MoNA 호환 메타데이터 |
| 표준화 패키지 자동 리포트 | MSI 레벨(동정 신뢰도) + QC 지표 자동 출력 |
| AI 기반 후보물질 추천/주석 도우미 | 지표성분 캘리브레이션 → unknown 구조 후보 추천 |
| 원료 QC 대시보드 | 지표성분 규격 + 배치 간 변동 |
| 작물-부위-생육-환경 비교 워크벤치 | 1차+2차 통합 분석 템플릿 |

### 대국민용 콘텐츠 (표-5 기반)
| 대상 | 콘텐츠 |
|------|--------|
| 소비자 | 성분 기반 원산지·진위성 신뢰지수 |
| 소비자 | 내가 산 특용작물 성분카드(QR 연동) |
| 소비자 | 가공·조리·건조 방식에 따른 성분 변화 가이드 |
| 농업인 | 수확 적기·품질 등급 예측(간편 진단) |
| 농업인/지자체 | 지역별 성분 지도(메타볼로믹스 지리정보) |
| 일반 | 특용작물 성분 백과(쉬운 언어) |

### 활용 시나리오 텍스트 (대시보드 우측)
```
🏛 정책: 지역별 지표 요약, 정책용 보고자료
🏭 산업: 후보 성분 비교, R&D 의사결정 참고
🌾 농업인: 재배 환경 이해, 현장 의사결정 보조
```

### 플랫폼 코어 기능 (계획서 p.29)
```
- 통합 대사체 DB (표준 데이터 패키지)
- QC 검증 및 버전관리 (릴리즈 관리)
- 검색 및 색인 (Search Index)
- AI 분석 활용 엔진
- API 제공
- 요약 및 리포트 생성
```

---

## 11. 주의사항 (절대 금지)

- ❌ 계획서/RFP에 없는 기능 추가하지 말 것
- ❌ 실제 AI 모델 로직 구현하지 말 것 (UI만)
- ❌ 실제 API 연동하지 말 것 (더미 데이터로)
- ❌ 로그인/회원가입 구현하지 말 것
- ❌ 모바일 반응형에 시간 쓰지 말 것 (데스크탑 시연)
- ❌ 작물명·성분명을 임의로 만들지 말 것 (계획서에 나온 것만)
- ✅ 동작하지 않는 버튼은 "개발 예정" 또는 disabled 처리
- ✅ 차트는 샘플 데이터로 시각적 효과만 보여줄 것
- ✅ 레퍼런스 이미지의 레이아웃·배치·색상 최대한 따를 것

---

## 12. 실행 방법

```bash
cd metabolome_platform
pip install django
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data    # 샘플 데이터 시딩
python manage.py runserver
# → http://127.0.0.1:8000/ 접속
```

---

## 13. 레퍼런스 이미지 요약 (Claude Code에서 참고)

### KakaoTalk_Photo_001 (Research Portal - Compound Catalog)
- 3-컬럼: 좌측 필터 | 중앙 테이블 | 우측 상세
- 다크 네이비 헤더, "RESEARCH PORTAL 연구자용 서비스"
- 브레드크럼: HOME > METABOLOMICS DB > RESEARCH PORTAL
- 테이블 행: 성분명 + 유래작물, L1/L2/L3 배지, IN-HOUSE/PUBLIC 배지, 스코어, QC
- 우측: 탭(개요/스펙트럼/QC/다운로드/분석), 활용모델, 근거·해석, TOP3 바, 원산지 판별 결과

### KakaoTalk_Photo_002 (Public Portal - Dashboard)
- 3-컬럼: 좌측 탐색·비교 | 중앙 대시보드 | 우측 AI해설
- 다크 네이비 헤더, "PUBLIC PORTAL 대국민 서비스"
- 지역·환경 지표 카드 (기온/강수/토양, 큰 숫자, "API 기반" 표시)
- 성분 분포 바차트 + 비교 결과 그룹 바차트
- 대국민 산출물 카드 미리보기 (인삼 이미지 + 설명)
- 우측: AI 해설, 활용 시나리오, 활용모델, 불확실성 안내
- 하단: 요약카드/비교카드/리포트 다운로드 버튼
