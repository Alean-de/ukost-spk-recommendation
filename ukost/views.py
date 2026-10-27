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
    FACILITIES_LIST, MOCK_HISTORY, MOCK_KOST_DATA
)
from .forms import StudentRegisterForm, StudentLoginForm
from .models import University, Facility, History
from .services import apply_hard_filters, calculate_topsis
from .constants import PRIORITY_CRITERIA
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

def login_view(request):
    """Login page."""
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('home')
    else:
        form = StudentLoginForm()


    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    """Registration page."""
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Registrasi Berhasil'
            )
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = StudentRegisterForm()

    return render(request, 'auth/register.html', {'form': form})

@login_required
def logout_view(request):
    """Logout and clear session."""
    request.session.flush()
    return redirect('login')

@login_required
def home_view(request):
    """Landing page / Homepage."""
    preview_kost = get_kost_for_landing()
    context = {
        'preview_kost': preview_kost,
        'user': request.session.get('user', {}),
    }
    return render(request, 'home/index.html', context)

@login_required
def cari_kost_view(request):
    if request.method == 'POST':
        request.session['search_prefs'] = {
            'campus': request.POST.get('campus'),
            'room_type': request.POST.get('room_type', 'Semua'),
            'max_price': request.POST.get('max_price'),
            'max_distance': request.POST.get('max_distance'),
        }
        return redirect('fasilitas')
    campuses = University.objects.all()
    return render(request, 'search/preference.html', {'campus_data': campuses, 'step': 1})

@login_required
def fasilitas_view(request):
    if request.method == 'POST':
        prefs = request.session.get('search_prefs')
        if not prefs:
            return redirect('cari_kost')
        prefs['facilities'] = request.POST.getlist('facilities')
        request.session['search_prefs'] = prefs
        return redirect('prioritas')
    facilities = Facility.objects.all()
    return render(request, 'search/fasilitas.html', {'facilities': facilities, 'step': 2})

@login_required
def prioritas_view(request):
    if request.method == 'POST':
        prefs = request.session.get('search_prefs')
        if not prefs:
            return redirect('cari_kost')

        priorities = {
            crit['id']: int(request.POST.get(f"priority_{crit['id']}", 3))
            for crit in PRIORITY_CRITERIA
        }
        prefs['priorities'] = priorities
        request.session['search_prefs'] = prefs

        History.objects.create(
            user=request.user,
            university_id=prefs.get('campus'),
            gender=prefs.get('room_type', 'Semua'),
            budget_limit=int(prefs.get('max_price') or 0),
            radius_limit=int(float(prefs.get('max_distance') or 0)),
            facility=prefs.get('facilities', []),
            criteria_weight=priorities,
        )
        return redirect('rekomendasi')
    return render(request, 'search/prioritas.html', {'criteria': PRIORITY_CRITERIA, 'step': 3})

@login_required
def rekomendasi_view(request):
    prefs = request.session.get('search_prefs')
    if not prefs or 'priorities' not in prefs:
        return redirect('cari_kost')

    campus_id = prefs.get('campus')
    room_type = prefs.get('room_type', 'Semua')
    max_price = prefs.get('max_price')
    max_distance = prefs.get('max_distance')
    mandatory = [int(f) for f in prefs.get('facilities', []) if str(f).isdigit()]
    user_priorities = {
        crit['id']: int(prefs['priorities'].get(crit['id'], 3))
        for crit in PRIORITY_CRITERIA
    }

    filtered_kosts = apply_hard_filters(
        campus_id=campus_id,
        room_type=room_type,
        max_price=max_price,
        max_distance=max_distance,
        mandatory_facilities=mandatory,
    )
    results = calculate_topsis(
        kost=filtered_kosts,
        user_priorities=user_priorities,
        univ_id=campus_id,
    )

    context = {
        'recommended': results[:5],
        'all_kost': results,
        'user': request.session.get('user', {}),
    }
    return render(request, 'recommendation/result.html', context)

@login_required
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

@login_required
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

@login_required
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

@login_required
def riwayat_view(request):
    """Redirect to favorit page with history tab active."""
    return redirect('/favorit/?tab=riwayat')