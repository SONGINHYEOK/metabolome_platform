from django.core.management.base import BaseCommand
from core.models import Crop, Compound, EnvironmentData


class Command(BaseCommand):
    help = '샘플 데이터 시딩 (계획서 기반 작물·성분만 사용)'

    def handle(self, *args, **options):
        # 기존 데이터 삭제
        Crop.objects.all().delete()
        Compound.objects.all().delete()
        EnvironmentData.objects.all().delete()

        # ── 작물 데이터 (계획서 언급 작물) ──
        crops_data = [
            {'name_ko': '인삼', 'name_en': 'Ginseng', 'name_scientific': 'Panax ginseng', 'plant_part': '뿌리', 'origin': '금산', 'year': 2025},
            {'name_ko': '인삼', 'name_en': 'Ginseng', 'name_scientific': 'Panax ginseng', 'plant_part': '뿌리', 'origin': '풍기', 'year': 2025},
            {'name_ko': '당귀', 'name_en': 'Angelica', 'name_scientific': 'Angelica gigas', 'plant_part': '뿌리', 'origin': '평창', 'year': 2025},
            {'name_ko': '황기', 'name_en': 'Astragalus', 'name_scientific': 'Astragalus membranaceus', 'plant_part': '뿌리', 'origin': '정선', 'year': 2025},
            {'name_ko': '결명자', 'name_en': 'Cassia', 'name_scientific': 'Senna obtusifolia', 'plant_part': '종자', 'origin': '진도', 'year': 2025},
            {'name_ko': '단삼', 'name_en': 'Salvia', 'name_scientific': 'Salvia miltiorrhiza', 'plant_part': '뿌리', 'origin': '영주', 'year': 2025},
            {'name_ko': '상황버섯', 'name_en': 'Phellinus', 'name_scientific': 'Phellinus linteus', 'plant_part': '자실체', 'origin': '영월', 'year': 2025},
            {'name_ko': '동충하초', 'name_en': 'Cordyceps', 'name_scientific': 'Cordyceps militaris', 'plant_part': '자실체', 'origin': '횡성', 'year': 2025},
        ]

        crops = {}
        for cd in crops_data:
            c = Crop.objects.create(**cd)
            key = f"{cd['name_ko']}_{cd['origin']}"
            crops[key] = c

        # ── 성분 데이터 (계획서·레퍼런스 이미지 언급 성분) ──
        compounds_data = [
            # 인삼 (금산)
            {'crop_key': '인삼_금산', 'name': 'Ginsenoside Rg1', 'annotation_level': 'L1', 'source': 'IN-HOUSE', 'score': 96, 'similarity': 0.94, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 801.01, 'retention_time': 12.3},
            {'crop_key': '인삼_금산', 'name': 'Ginsenoside Rb1', 'annotation_level': 'L1', 'source': 'IN-HOUSE', 'score': 93, 'similarity': 0.92, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 1109.29, 'retention_time': 15.7},
            {'crop_key': '인삼_금산', 'name': 'Ginsenoside Re', 'annotation_level': 'L1', 'source': 'PUBLIC', 'score': 88, 'similarity': 0.89, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 947.15, 'retention_time': 11.2},
            {'crop_key': '인삼_금산', 'name': 'Ginsenoside Rc', 'annotation_level': 'L2', 'source': 'PUBLIC', 'score': 79, 'similarity': 0.82, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 1079.27, 'retention_time': 14.8},
            # 인삼 (풍기)
            {'crop_key': '인삼_풍기', 'name': 'Ginsenoside Rg1', 'annotation_level': 'L1', 'source': 'IN-HOUSE', 'score': 91, 'similarity': 0.90, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 801.01, 'retention_time': 12.5},
            {'crop_key': '인삼_풍기', 'name': 'Ginsenoside Rb1', 'annotation_level': 'L1', 'source': 'IN-HOUSE', 'score': 89, 'similarity': 0.88, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 1109.29, 'retention_time': 15.9},
            # 당귀
            {'crop_key': '당귀_평창', 'name': 'Decursin', 'annotation_level': 'L1', 'source': 'PUBLIC', 'score': 89, 'similarity': 0.91, 'qc_status': 'PASS', 'compound_class': 'Coumarin', 'molecular_weight': 328.36, 'retention_time': 18.4},
            {'crop_key': '당귀_평창', 'name': 'Decursinol angelate', 'annotation_level': 'L1', 'source': 'IN-HOUSE', 'score': 85, 'similarity': 0.87, 'qc_status': 'PASS', 'compound_class': 'Coumarin', 'molecular_weight': 328.36, 'retention_time': 17.1},
            {'crop_key': '당귀_평창', 'name': 'Nodakenin', 'annotation_level': 'L2', 'source': 'PUBLIC', 'score': 76, 'similarity': 0.80, 'qc_status': 'PASS', 'compound_class': 'Coumarin', 'molecular_weight': 408.40, 'retention_time': 9.6},
            # 황기
            {'crop_key': '황기_정선', 'name': 'Astragaloside IV', 'annotation_level': 'L2', 'source': 'IN-HOUSE', 'score': 84, 'similarity': 0.88, 'qc_status': 'PASS', 'compound_class': 'Saponin', 'molecular_weight': 784.97, 'retention_time': 20.1},
            {'crop_key': '황기_정선', 'name': 'Calycosin', 'annotation_level': 'L1', 'source': 'PUBLIC', 'score': 82, 'similarity': 0.85, 'qc_status': 'PASS', 'compound_class': 'Flavonoid', 'molecular_weight': 284.26, 'retention_time': 13.8},
            # 결명자
            {'crop_key': '결명자_진도', 'name': 'Chrysophanol', 'annotation_level': 'L1', 'source': 'PUBLIC', 'score': 87, 'similarity': 0.90, 'qc_status': 'PASS', 'compound_class': 'Anthraquinone', 'molecular_weight': 254.24, 'retention_time': 22.3},
            # 단삼
            {'crop_key': '단삼_영주', 'name': 'Tanshinone IIA', 'annotation_level': 'L1', 'source': 'IN-HOUSE', 'score': 90, 'similarity': 0.91, 'qc_status': 'PASS', 'compound_class': 'Diterpene', 'molecular_weight': 294.34, 'retention_time': 25.6},
            {'crop_key': '단삼_영주', 'name': 'Salvianolic acid B', 'annotation_level': 'L1', 'source': 'PUBLIC', 'score': 86, 'similarity': 0.88, 'qc_status': 'PASS', 'compound_class': 'Phenolic acid', 'molecular_weight': 718.61, 'retention_time': 16.2},
            # 상황버섯
            {'crop_key': '상황버섯_영월', 'name': 'Beta-glucan', 'annotation_level': 'L3', 'source': 'PUBLIC', 'score': 68, 'similarity': 0.76, 'qc_status': 'REVIEW', 'compound_class': 'Polysaccharide', 'molecular_weight': None, 'retention_time': None},
            # 동충하초
            {'crop_key': '동충하초_횡성', 'name': 'Cordycepin', 'annotation_level': 'L2', 'source': 'IN-HOUSE', 'score': 79, 'similarity': 0.82, 'qc_status': 'PASS', 'compound_class': 'Nucleoside', 'molecular_weight': 251.24, 'retention_time': 5.8},
        ]

        for cpd in compounds_data:
            crop = crops[cpd.pop('crop_key')]
            Compound.objects.create(crop=crop, **cpd)

        # ── 환경 데이터 ──
        env_data = [
            {'region': '강원도 평창군', 'avg_temperature': 13.2, 'avg_rainfall': 1240, 'soil_grade': 'B'},
            {'region': '충남 금산군', 'avg_temperature': 12.8, 'avg_rainfall': 1150, 'soil_grade': 'A'},
            {'region': '경북 영주시', 'avg_temperature': 11.5, 'avg_rainfall': 1080, 'soil_grade': 'B'},
            {'region': '전남 진도군', 'avg_temperature': 14.1, 'avg_rainfall': 1320, 'soil_grade': 'A'},
            {'region': '강원도 정선군', 'avg_temperature': 10.8, 'avg_rainfall': 1180, 'soil_grade': 'B'},
            {'region': '강원도 영월군', 'avg_temperature': 11.2, 'avg_rainfall': 1200, 'soil_grade': 'C'},
            {'region': '강원도 횡성군', 'avg_temperature': 11.0, 'avg_rainfall': 1160, 'soil_grade': 'B'},
        ]

        for ed in env_data:
            EnvironmentData.objects.create(**ed)

        self.stdout.write(self.style.SUCCESS(
            f'시딩 완료: 작물 {Crop.objects.count()}건, '
            f'성분 {Compound.objects.count()}건, '
            f'환경데이터 {EnvironmentData.objects.count()}건'
        ))
