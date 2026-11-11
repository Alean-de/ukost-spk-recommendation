"""
Views for U Kost application.
Handles all page rendering and mock data processing.
"""
import json
import re
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .mock_data import (
    get_all_kost, get_kost_by_id, get_recommended_kost,
    get_kost_for_landing, CAMPUS_DATA, FAKULTAS_DATA,
    FACILITIES_LIST, MOCK_HISTORY, MOCK_KOST_DATA
)
from .forms import StudentRegisterForm, StudentLoginForm
from .models import (
    University, Faculty, StudyProgram, Facility,
    History, Kost, Favorite, UserDetail
)
from .services import apply_hard_filters, calculate_topsis
from .constants import PRIORITY_CRITERIA
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def login_view(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('home')

    error = None
    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            detail = getattr(user, 'profile', None)
            request.session['user'] = {
                'name': user.get_full_name() or user.username,
                'nim': detail.nim if detail else user.username,
                'email': user.email,
                'campus': detail.university.name if detail and detail.university else 'UKRIDA',
                'faculty': detail.faculty.name if detail and detail.faculty else '',
                'study_program': detail.study_program.name if detail and detail.study_program else '',
                'avatar_url': detail.avatar_url if detail else None,
                'phone': detail.phone_number if detail else '',
            }
            request.session.modified = True
            return redirect('home')
        else:
            errors = form.non_field_errors()
            if errors:
                error = errors[0]
            else:
                error = 'NIM, Kampus, atau Kata Sandi yang dimasukkan tidak sesuai.'
    else:
        form = StudentLoginForm()

    return render(request, 'auth/login.html', {'form': form, 'error': error})


def register_view(request):
    """Registration page."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(
                    request, 'Registrasi Berhasil! Akun mahasiswa Anda telah dibuat. Silakan masuk.'
                )
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Terjadi kendala saat pendaftaran: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = StudentRegisterForm()

    return render(request, 'auth/register.html', {'form': form})

@login_required
def logout_view(request):
    """Logout and clear session."""
    logout(request)
    request.session.flush()
    messages.info(request, 'Anda telah berhasil keluar dari akun U Kost. Silakan masuk kembali.')
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
    campus = University.objects.filter(id=campus_id).first()
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
        'campus': campus,
        'prefs': prefs,
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
    """Redirect to profile page with favorites tab active."""
    return redirect('/profil/?tab=favorit')

@login_required
def riwayat_view(request):
    """Redirect to profile page with history tab active."""
    return redirect('/profil/?tab=riwayat')

@login_required
def profile_view(request):
    """Mahasiswa User Profile page."""
    detail = getattr(request.user, 'profile', None)
    if not detail:
        first_univ = University.objects.first()
        first_faculty = Faculty.objects.first()
        first_prodi = StudyProgram.objects.first()
        detail, _ = UserDetail.objects.get_or_create(
            user=request.user,
            defaults={
                'nim': request.user.username,
                'university': first_univ,
                'faculty': first_faculty,
                'study_program': first_prodi,
            }
        )

    tab = request.GET.get('tab', 'biodata')
    if tab not in ['biodata', 'edit', 'security', 'favorit', 'riwayat']:
        tab = 'biodata'

    if request.method == 'POST':
        action = request.POST.get('action')

        # ----------------------------------------------------
        # 1. Action: Upload / Update Foto Profil (Avatar)
        # ----------------------------------------------------
        if action == 'update_avatar':
            avatar_file = request.FILES.get('avatar')
            if not avatar_file:
                messages.error(request, 'Silakan pilih berkas foto profil terlebih dahulu.')
                return redirect('/profil/?tab=edit')

            ext = avatar_file.name.split('.')[-1].lower() if '.' in avatar_file.name else ''
            if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                messages.error(request, 'Format foto tidak didukung. Harap unggah format JPG, JPEG, PNG, atau WebP.')
                return redirect('/profil/?tab=edit')

            if avatar_file.size > 2 * 1024 * 1024:
                messages.error(request, 'Ukuran foto terlalu besar. Maksimum ukuran yang diizinkan adalah 2 MB.')
                return redirect('/profil/?tab=edit')

            if detail.avatar:
                try:
                    detail.avatar.delete(save=False)
                except Exception:
                    pass

            detail.avatar = avatar_file
            detail.save()
            detail.refresh_from_db()

            # Refresh user session
            sess_user = request.session.get('user', {})
            sess_user['avatar_url'] = detail.avatar_url
            request.session['user'] = sess_user
            request.session.modified = True

            messages.success(request, 'Foto profil Anda berhasil diperbarui!')
            return redirect('/profil/?tab=edit')

        # ----------------------------------------------------
        # 2. Action: Hapus / Reset Foto Profil ke Default
        # ----------------------------------------------------
        elif action == 'delete_avatar':
            if detail.avatar:
                try:
                    detail.avatar.delete(save=False)
                except Exception:
                    pass
                detail.avatar = None
                detail.save()
                detail.refresh_from_db()

                sess_user = request.session.get('user', {})
                sess_user['avatar_url'] = None
                request.session['user'] = sess_user
                request.session.modified = True

                messages.success(request, 'Foto profil berhasil dihapus dan dikembalikan ke avatar default.')
            else:
                messages.info(request, 'Foto profil saat ini sudah menggunakan avatar default.')
            return redirect('/profil/?tab=edit')

        # ----------------------------------------------------
        # 3. Action: Update Informasi Akun & Biodata
        # ----------------------------------------------------
        elif action == 'update_profile':
            full_name = request.POST.get('full_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            bio = request.POST.get('bio', '').strip()
            univ_id = request.POST.get('university')
            faculty_id = request.POST.get('faculty')
            prodi_id = request.POST.get('study_program')

            # Validasi Nama Lengkap
            if not full_name:
                messages.error(request, 'Nama lengkap wajib diisi.')
                return redirect('/profil/?tab=edit')
            if len(full_name) < 2:
                messages.error(request, 'Nama lengkap terlalu pendek (minimal 2 karakter).')
                return redirect('/profil/?tab=edit')

            # Validasi Username
            if username:
                if len(username) < 3 or len(username) > 30:
                    messages.error(request, 'Username harus terdiri dari 3 hingga 30 karakter.')
                    return redirect('/profil/?tab=edit')
                if not re.match(r'^[a-zA-Z0-9_.]+$', username):
                    messages.error(request, 'Username hanya boleh berisi huruf, angka, garis bawah (_), atau titik.')
                    return redirect('/profil/?tab=edit')
                if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                    messages.error(request, f'Username "{username}" sudah digunakan akun lain. Silakan pilih username lain.')
                    return redirect('/profil/?tab=edit')
                request.user.username = username

            # Validasi Email
            if not email:
                messages.error(request, 'Alamat email wajib diisi.')
                return redirect('/profil/?tab=edit')
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messages.error(request, 'Format alamat email tidak valid.')
                return redirect('/profil/?tab=edit')
            if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Alamat email ini sudah terdaftar pada akun lain.')
                return redirect('/profil/?tab=edit')

            # Validasi Nomor Telepon / HP
            if phone_number:
                cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone_number)
                if not re.match(r'^\+?[0-9]{9,16}$', cleaned_phone):
                    messages.error(request, 'Format nomor telepon/WhatsApp tidak valid. Contoh: 08123456789 atau +628123456789.')
                    return redirect('/profil/?tab=edit')
                detail.phone_number = phone_number
            else:
                detail.phone_number = ''

            # Validasi Bio
            if len(bio) > 500:
                messages.error(request, 'Bio tidak boleh lebih dari 500 karakter.')
                return redirect('/profil/?tab=edit')
            detail.bio = bio

            # Simpan perubahan User (auth.User)
            parts = full_name.split(' ', 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ''
            request.user.email = email
            request.user.save()

            # Tangani upload foto jika diupload bersamaan di form ini
            avatar_uploaded = False
            if 'avatar' in request.FILES and request.FILES['avatar']:
                av = request.FILES['avatar']
                ext = av.name.split('.')[-1].lower() if '.' in av.name else ''
                if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif'] and av.size <= 2 * 1024 * 1024:
                    if detail.avatar:
                        try:
                            detail.avatar.delete(save=False)
                        except Exception:
                            pass
                    detail.avatar = av
                    avatar_uploaded = True
                elif av.size > 2 * 1024 * 1024:
                    messages.warning(request, 'Ukuran foto melebihi 2 MB dan tidak ikut tersimpan.')

            # Simpan akademik
            if univ_id:
                detail.university_id = univ_id
            if faculty_id:
                detail.faculty_id = faculty_id
            if prodi_id:
                detail.study_program_id = prodi_id
            detail.save()
            detail.refresh_from_db()

            # Refresh Session
            request.session['user'] = {
                'name': request.user.get_full_name() or request.user.username,
                'nim': detail.nim,
                'email': request.user.email,
                'campus': detail.university.name if detail.university else 'UKRIDA',
                'faculty': detail.faculty.name if detail.faculty else '',
                'study_program': detail.study_program.name if detail.study_program else '',
                'avatar_url': detail.avatar_url,
                'phone': detail.phone_number or '',
                'bio': detail.bio or '',
            }
            request.session.modified = True

            if avatar_uploaded:
                messages.success(request, 'Foto profil dan informasi akun Anda berhasil diperbarui!')
            else:
                messages.success(request, 'Informasi akun profil berhasil diperbarui!')
            return redirect('/profil/?tab=edit')

        # ----------------------------------------------------
        # 4. Action: Ganti Kata Sandi (Password)
        # ----------------------------------------------------
        elif action == 'change_password':
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not old_password:
                messages.error(request, 'Harap masukkan kata sandi saat ini.')
                return redirect('/profil/?tab=security')

            if not request.user.check_password(old_password):
                messages.error(request, 'Kata sandi saat ini yang Anda masukkan salah.')
                return redirect('/profil/?tab=security')

            if len(new_password) < 8:
                messages.error(request, 'Kata sandi baru minimal harus terdiri dari 8 karakter.')
                return redirect('/profil/?tab=security')

            if old_password == new_password:
                messages.error(request, 'Kata sandi baru tidak boleh sama dengan kata sandi saat ini.')
                return redirect('/profil/?tab=security')

            has_letter = any(c.isalpha() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            if not (has_letter and has_digit):
                messages.error(request, 'Kata sandi baru harus mengombinasikan huruf dan angka demi keamanan akun.')
                return redirect('/profil/?tab=security')

            if new_password != confirm_password:
                messages.error(request, 'Konfirmasi kata sandi baru tidak cocok dengan kata sandi baru.')
                return redirect('/profil/?tab=security')

            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Kata sandi akun Anda berhasil diperbarui! Gunakan kata sandi baru untuk login berikutnya.')
            return redirect('/profil/?tab=security')

        # ----------------------------------------------------
        # 5. Action: Hapus Favorit
        # ----------------------------------------------------
        elif action == 'remove_favorite':
            kost_id = request.POST.get('kost_id')
            Favorite.objects.filter(user=request.user, kost_id=kost_id).delete()
            messages.info(request, 'Kost berhasil dihapus dari daftar favorit.')
            return redirect('/profil/?tab=favorit')

        # ----------------------------------------------------
        # 6. Action: Bersihkan Riwayat Pencarian SPK
        # ----------------------------------------------------
        elif action == 'clear_history':
            History.objects.filter(user=request.user).delete()
            messages.info(request, 'Riwayat pencarian berhasil dibersihkan.')
            return redirect('/profil/?tab=riwayat')

    # Fetch user details
    favorites = Favorite.objects.filter(user=request.user).select_related('kost').order_by('-time_added')
    histories = History.objects.filter(user=request.user).select_related('university').order_by('-search_time')
    universities = University.objects.all()
    faculties = Faculty.objects.all()
    study_programs = StudyProgram.objects.all()
    all_kost = get_all_kost()

    all_kost_json = json.dumps([{
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
    } for k in all_kost])

    history_list = []
    for h in histories:
        crit_text = ', '.join([f"{k.capitalize()}: {v}" for k, v in (h.criteria_weight or {}).items()]) if h.criteria_weight else 'Prioritas Seimbang'
        history_list.append({
            'id': h.id,
            'date': h.search_time.strftime('%d %B %Y'),
            'time': h.search_time.strftime('%H:%M WIB'),
            'campus': h.university.name if h.university else 'UKRIDA',
            'gender': h.gender or 'Semua',
            'budget': f"Rp{h.budget_limit:,}".replace(',', '.') if h.budget_limit else 'Rp2.000.000',
            'distance': f"{h.radius_limit / 1000:.1f} km" if h.radius_limit and h.radius_limit >= 1000 else f"{h.radius_limit or 3000} m",
            'priority': crit_text,
            'results_count': 5,
        })
    if not history_list:
        history_list = MOCK_HISTORY

    history_json = json.dumps(history_list)

    context = {
        'student': request.user,
        'profile': detail,
        'favorites': favorites,
        'histories': histories,
        'history_list': history_list,
        'all_kost': all_kost,
        'all_kost_json': all_kost_json,
        'history_json': history_json,
        'favorite_count': favorites.count(),
        'history_count': len(history_list),
        'universities': universities,
        'faculties': faculties,
        'study_programs': study_programs,
        'active_tab': tab,
        'user': request.session.get('user', {
            'name': request.user.get_full_name() or request.user.username,
            'nim': detail.nim,
            'avatar_url': detail.avatar_url,
        }),
    }
    return render(request, 'profile/index.html', context)
