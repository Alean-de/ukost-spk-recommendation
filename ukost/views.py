"""
Views for U Kost application.
Handles all page rendering and mock data processing.
"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .mock_data import (
    get_all_kost, get_kost_by_id, get_recommended_kost,
    get_kost_for_landing, CAMPUS_DATA, FAKULTAS_DATA,
    FACILITIES_LIST, PRIORITY_CRITERIA, MOCK_HISTORY, MOCK_KOST_DATA
)


def login_view(request):
    """Login page."""
    if request.method == 'POST':
        # Mock authentication - accept any credentials
        nim = request.POST.get('nim', '')
        password = request.POST.get('password', '')

        if nim and password:
            request.session['is_authenticated'] = True
            request.session['user'] = {
                'nim': nim,
                'name': 'Jonathan Agustinus',
                'campus': 'UKRIDA Kampus 1',
                'fakultas': 'Fakultas Teknik & Ilmu Komputer',
                'email': f'{nim}@student.ukrida.ac.id',
            }
            return redirect('home')
        else:
            return render(request, 'auth/login.html', {
                'error': 'NIM dan Password harus diisi.',
                'campus_data': CAMPUS_DATA,
                'fakultas_data': FAKULTAS_DATA,
            })

    return render(request, 'auth/login.html', {
        'campus_data': CAMPUS_DATA,
        'fakultas_data': FAKULTAS_DATA,
    })


def register_view(request):
    """Registration page."""
    if request.method == 'POST':
        # Mock registration
        request.session['registration_success'] = True
        return redirect('login')

    return render(request, 'auth/register.html', {
        'campus_data': CAMPUS_DATA,
        'fakultas_data': FAKULTAS_DATA,
    })


def logout_view(request):
    """Logout and clear session."""
    request.session.flush()
    return redirect('login')


def home_view(request):
    """Landing page / Homepage."""
    preview_kost = get_kost_for_landing()
    context = {
        'preview_kost': preview_kost,
        'user': request.session.get('user', {}),
    }
    return render(request, 'home/index.html', context)


def cari_kost_view(request):
    """Search preferences - Step 1: Basic Needs."""
    context = {
        'campus_data': CAMPUS_DATA,
        'step': 1,
        'user': request.session.get('user', {}),
    }
    return render(request, 'search/preference.html', context)


def fasilitas_view(request):
    """Search preferences - Step 2: Facilities."""
    context = {
        'facilities': FACILITIES_LIST,
        'step': 2,
        'user': request.session.get('user', {}),
    }
    return render(request, 'search/fasilitas.html', context)


def prioritas_view(request):
    """Search preferences - Step 3: Priority."""
    context = {
        'criteria': PRIORITY_CRITERIA,
        'step': 3,
        'user': request.session.get('user', {}),
    }
    return render(request, 'search/prioritas.html', context)


def rekomendasi_view(request):
    """Recommendation results page."""
    recommended = get_recommended_kost(5)
    all_kost = get_all_kost()
    context = {
        'recommended': recommended,
        'all_kost': all_kost,
        'all_kost_json': json.dumps([{
            'id': k['id'],
            'name': k['name'],
            'price': k['price'],
            'price_display': k['price_display'],
            'distance': k['distance'],
            'rating': k['rating'],
            'room_type': k['room_type'],
            'facilities': k['facilities'],
            'score': k['score'],
            'scores': k['scores'],
            'rank': k['rank'],
            'address': k['address'],
            'wifi': k['wifi'],
            'bathroom': k['bathroom'],
            'ac': k['ac'],
            'security': k['security'],
            'cctv': k['cctv'],
            'availability': k['availability'],
        } for k in all_kost]),
        'user': request.session.get('user', {}),
    }
    return render(request, 'recommendation/result.html', context)


def detail_kost_view(request, kost_id):
    """Detail page for a specific kost."""
    kost = get_kost_by_id(kost_id)
    if not kost:
        return redirect('rekomendasi')

    # Find adjacent kost for navigation
    all_kost = get_recommended_kost(8)
    current_index = None
    for i, k in enumerate(all_kost):
        if k['id'] == kost_id:
            current_index = i
            break

    prev_kost = all_kost[current_index - 1] if current_index and current_index > 0 else None
    next_kost = all_kost[current_index + 1] if current_index is not None and current_index < len(all_kost) - 1 else None

    # Similar kost (exclude current)
    similar = [k for k in all_kost if k['id'] != kost_id][:3]

    context = {
        'kost': kost,
        'prev_kost': prev_kost,
        'next_kost': next_kost,
        'similar_kost': similar,
        'total_kost': len(MOCK_KOST_DATA),
        'user': request.session.get('user', {}),
    }
    return render(request, 'kost/detail.html', context)


def bandingkan_view(request):
    """Comparison page."""
    all_kost = get_all_kost()
    context = {
        'all_kost': all_kost,
        'all_kost_json': json.dumps([{
            'id': k['id'],
            'name': k['name'],
            'price': k['price'],
            'price_display': k['price_display'],
            'distance': k['distance'],
            'rating': k['rating'],
            'room_type': k['room_type'],
            'room_size': k['room_size'],
            'facilities': k['facilities'],
            'score': k['score'],
            'scores': k['scores'],
            'wifi': k['wifi'],
            'wifi_speed': k.get('wifi_speed', '-'),
            'bathroom': k['bathroom'],
            'ac': k['ac'],
            'security': k['security'],
            'cctv': k['cctv'],
            'parking': k['parking'],
            'kitchen': k['kitchen'],
            'laundry': k['laundry'],
            'electricity_included': k['electricity_included'],
            'access_24h': k['access_24h'],
            'address': k['address'],
            'availability': k['availability'],
        } for k in all_kost]),
        'user': request.session.get('user', {}),
    }
    return render(request, 'comparison/index.html', context)


def favorit_view(request):
    """Favorites and History page."""
    all_kost = get_all_kost()
    context = {
        'all_kost': all_kost,
        'all_kost_json': json.dumps([{
            'id': k['id'],
            'name': k['name'],
            'price': k['price'],
            'price_display': k['price_display'],
            'distance': k['distance'],
            'rating': k['rating'],
            'room_type': k['room_type'],
            'facilities': k['facilities'],
            'score': k['score'],
            'address': k['address'],
            'availability': k['availability'],
            'owner_phone': k.get('owner_phone', ''),
        } for k in all_kost]),
        'history': MOCK_HISTORY,
        'history_json': json.dumps(MOCK_HISTORY),
        'user': request.session.get('user', {}),
    }
    return render(request, 'archive/index.html', context)


def riwayat_view(request):
    """Redirect to favorit page with history tab active."""
    return redirect('/favorit/?tab=riwayat')


# API endpoints for AJAX operations
@require_http_methods(["GET"])
def api_kost_list(request):
    """API to get all kost data as JSON."""
    return JsonResponse({'kost': [{
        'id': k['id'],
        'name': k['name'],
        'price': k['price'],
        'price_display': k['price_display'],
        'distance': k['distance'],
        'rating': k['rating'],
        'room_type': k['room_type'],
        'facilities': k['facilities'],
        'score': k['score'],
    } for k in get_all_kost()]})


@require_http_methods(["GET"])
def api_kost_detail(request, kost_id):
    """API to get single kost data as JSON."""
    kost = get_kost_by_id(kost_id)
    if kost:
        return JsonResponse({'kost': kost})
    return JsonResponse({'error': 'Kost not found'}, status=404)
