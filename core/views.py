import json
import logging
import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Crop, Compound, EnvironmentData
from . import ai_service

logger = logging.getLogger('core')


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '-')


def landing(request):
    logger.info("PAGE  landing | ip=%s", _client_ip(request))
    crop_count = Crop.objects.values('name_ko').distinct().count()
    compound_count = Compound.objects.count()
    context = {
        'crop_count': crop_count,
        'compound_count': compound_count,
    }
    return render(request, 'landing.html', context)


def research_index(request):
    logger.info("PAGE  research_index | ip=%s", _client_ip(request))
    context = {
        'compound_count': Compound.objects.count(),
        'crop_count': Crop.objects.values('name_ko').distinct().count(),
    }
    return render(request, 'research/index.html', context)


def research_catalog(request):
    logger.info("PAGE  research_catalog | ip=%s filters={crop=%s, part=%s, origin=%s, qc=%s}",
                _client_ip(request),
                request.GET.get('crop', ''), request.GET.get('part', ''),
                request.GET.get('origin', ''), request.GET.get('qc', 'PASS'))
    crop_filter = request.GET.get('crop', '')
    part_filter = request.GET.get('part', '')
    origin_filter = request.GET.get('origin', '')
    year_filter = request.GET.get('year', '')
    qc_filter = request.GET.get('qc', 'PASS')

    compounds = Compound.objects.select_related('crop').all()

    if crop_filter:
        compounds = compounds.filter(crop__name_ko=crop_filter)
    if part_filter:
        compounds = compounds.filter(crop__plant_part=part_filter)
    if origin_filter:
        compounds = compounds.filter(crop__origin=origin_filter)
    if year_filter:
        compounds = compounds.filter(crop__year=int(year_filter))
    if qc_filter:
        compounds = compounds.filter(qc_status=qc_filter)

    crops = Crop.objects.values_list('name_ko', flat=True).distinct()
    parts = Crop.objects.values_list('plant_part', flat=True).distinct()
    origins = Crop.objects.values_list('origin', flat=True).distinct()
    years = Crop.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'compounds': compounds,
        'crops': crops,
        'parts': parts,
        'origins': origins,
        'years': years,
        'current_crop': crop_filter,
        'current_part': part_filter,
        'current_origin': origin_filter,
        'current_year': year_filter,
        'current_qc': qc_filter,
        'total_count': Compound.objects.count(),
    }
    return render(request, 'research/catalog.html', context)


def public_index(request):
    logger.info("PAGE  public_index | ip=%s", _client_ip(request))
    context = {
        'crop_count': Crop.objects.values('name_ko').distinct().count(),
    }
    return render(request, 'public/index.html', context)


def public_dashboard(request):
    crop_a_name = request.GET.get('crop_a', '인삼')
    crop_b_name = request.GET.get('crop_b', '황기')
    logger.info("PAGE  public_dashboard | ip=%s compare=%s vs %s",
                _client_ip(request), crop_a_name, crop_b_name)

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
        'compounds_a_json': json.dumps(compounds_a),
        'compounds_b_json': json.dumps(compounds_b),
        'env_data': env_data,
        'crops': crops,
        'current_crop_a': crop_a_name,
        'current_crop_b': crop_b_name,
    }
    return render(request, 'public/dashboard.html', context)


# ========== AI API Views ==========

@csrf_exempt
def api_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body)
        messages = body.get('messages', [])
        if not messages:
            return JsonResponse({'error': 'messages required'}, status=400)
        last_msg = messages[-1].get('content', '')[:100]
        logger.info("API   chat | ip=%s msg_count=%d last=\"%s\"",
                     _client_ip(request), len(messages), last_msg)
        t0 = time.time()
        result = ai_service.chat_completion(messages)
        elapsed = time.time() - t0
        if 'error' in result:
            logger.warning("API   chat ERROR | %.1fs | %s", elapsed, result['error'])
        else:
            logger.info("API   chat OK | %.1fs | reply=%s...",
                        elapsed, result.get('content', '')[:80])
        return JsonResponse(result)
    except json.JSONDecodeError:
        logger.warning("API   chat | invalid JSON | ip=%s", _client_ip(request))
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def api_interpret_compound(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body)
        compound_data = body.get('compound', {})
        if not compound_data:
            return JsonResponse({'error': 'compound data required'}, status=400)
        name = compound_data.get('name', '?')
        crop = compound_data.get('crop', '?')
        logger.info("API   interpret_compound | ip=%s compound=%s crop=%s",
                     _client_ip(request), name, crop)
        t0 = time.time()
        result = ai_service.interpret_compound(compound_data)
        elapsed = time.time() - t0
        if 'error' in result:
            logger.warning("API   interpret_compound ERROR | %.1fs | %s", elapsed, result['error'])
        else:
            logger.info("API   interpret_compound OK | %.1fs | %s", elapsed, name)
        return JsonResponse(result)
    except json.JSONDecodeError:
        logger.warning("API   interpret_compound | invalid JSON | ip=%s", _client_ip(request))
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def api_interpret_dashboard(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body)
        dashboard_data = body.get('dashboard', {})
        if not dashboard_data:
            return JsonResponse({'error': 'dashboard data required'}, status=400)
        crop_a = dashboard_data.get('crop_a', {}).get('name', '?')
        crop_b = dashboard_data.get('crop_b', {}).get('name', '?')
        logger.info("API   interpret_dashboard | ip=%s compare=%s vs %s",
                     _client_ip(request), crop_a, crop_b)
        t0 = time.time()
        result = ai_service.interpret_dashboard(dashboard_data)
        elapsed = time.time() - t0
        if 'error' in result:
            logger.warning("API   interpret_dashboard ERROR | %.1fs | %s", elapsed, result['error'])
        else:
            logger.info("API   interpret_dashboard OK | %.1fs | %s vs %s", elapsed, crop_a, crop_b)
        return JsonResponse(result)
    except json.JSONDecodeError:
        logger.warning("API   interpret_dashboard | invalid JSON | ip=%s", _client_ip(request))
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
