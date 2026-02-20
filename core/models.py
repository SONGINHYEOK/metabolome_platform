from django.db import models


class Crop(models.Model):
    """특용작물"""
    name_ko = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    name_scientific = models.CharField(max_length=200, blank=True)
    plant_part = models.CharField(max_length=50)
    origin = models.CharField(max_length=100)
    year = models.IntegerField(default=2025)

    def __str__(self):
        return f"{self.name_ko} ({self.name_en})"

    class Meta:
        ordering = ['name_ko']


class Compound(models.Model):
    """대사체 성분"""
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='compounds')
    name = models.CharField(max_length=200)
    annotation_level = models.CharField(max_length=10)
    source = models.CharField(max_length=20)
    score = models.IntegerField(default=0)
    similarity = models.FloatField(default=0.0)
    qc_status = models.CharField(max_length=20)
    compound_class = models.CharField(max_length=100, blank=True)
    molecular_weight = models.FloatField(null=True, blank=True)
    retention_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-score']


class EnvironmentData(models.Model):
    """지역·환경 지표 (공공API 연계 예시용)"""
    region = models.CharField(max_length=100)
    avg_temperature = models.FloatField()
    avg_rainfall = models.FloatField()
    soil_grade = models.CharField(max_length=10)

    def __str__(self):
        return self.region
