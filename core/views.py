from django.shortcuts import render
from .models import Crop, Compound, EnvironmentData


def landing(request):
    crop_count = Crop.objects.values('name_ko').distinct().count()
    compound_count = Compound.objects.count()
    context = {
        'crop_count': crop_count,
        'compound_count': compound_count,
    }
    return render(request, 'landing.html', context)


def research_index(request):
    return render(request, 'research/index.html')


def research_catalog(request):
    crop_filter = request.GET.get('crop', '')
    part_filter = request.GET.get('part', '')
    origin_filter = request.GET.get('origin', '')
    qc_filter = request.GET.get('qc', '')

    compounds = Compound.objects.select_related('crop').all()

    if crop_filter:
        compounds = compounds.filter(crop__name_ko=crop_filter)
    if part_filter:
        compounds = compounds.filter(crop__plant_part=part_filter)
    if origin_filter:
        compounds = compounds.filter(crop__origin=origin_filter)
    if qc_filter:
        compounds = compounds.filter(qc_status=qc_filter)

    crops = Crop.objects.values_list('name_ko', flat=True).distinct()
    parts = Crop.objects.values_list('plant_part', flat=True).distinct()
    origins = Crop.objects.values_list('origin', flat=True).distinct()

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
    return render(request, 'public/index.html')


def public_dashboard(request):
    crop_a_name = request.GET.get('crop_a', '인삼')
    crop_b_name = request.GET.get('crop_b', '황기')

    crop_a = Crop.objects.filter(name_ko=crop_a_name).first()
    crop_b = Crop.objects.filter(name_ko=crop_b_name).first()

    compounds_a = list(Compound.objects.filter(crop=crop_a).values('name', 'score', 'compound_class')) if crop_a else []
    compounds_b = list(Compound.objects.filter(crop=crop_b).values('name', 'score', 'compound_class')) if crop_b else []

    env_data = None
    if crop_a:
        env_data = EnvironmentData.objects.filter(region__contains=crop_a.origin).first()
    if not env_data:
        env_data = EnvironmentData.objects.first()

    crops = Crop.objects.values_list('name_ko', flat=True).distinct()

    context = {
        'crop_a': crop_a,
        'crop_b': crop_b,
        'compounds_a': compounds_a,
        'compounds_b': compounds_b,
        'env_data': env_data,
        'crops': crops,
        'current_crop_a': crop_a_name,
        'current_crop_b': crop_b_name,
    }
    return render(request, 'public/dashboard.html', context)
