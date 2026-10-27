import numpy as np
from django.db.models import Q
from .models import Kost
from .constants import PRIORITY_CRITERIA, FACILITY_WEIGHTS


def apply_hard_filters(campus_id, room_type=None, max_price=None, max_distance=None, mandatory_facilities=None):
    """
    Melakukan query penyaringan awal di database.
    Mengembalikan QuerySet kost yang lolos kriteria mutlak.
    """
    filters = Q()

    if room_type and room_type != 'Semua' and room_type != 'Campur/Bebas':
        filters &= Q(gender_type=room_type)

    if max_price:
        filters &= Q(price__lte=float(max_price))

    if max_distance:
        if str(campus_id) == '2':
            filters &= Q(distance_to_campus_2__lte=float(max_distance))
        else:
            filters &= Q(distance_to_campus_1__lte=float(max_distance))

    return Kost.objects.filter(filters)

def calculate_facility_score(kost_facility_ids, user_facility_ids):
    if not user_facility_ids:
        return 100.0

    user_max_weight = sum(FACILITY_WEIGHTS.get(fac_id, 3.0) for fac_id in user_facility_ids)
    if user_max_weight == 0:
        return 100.0

    matched_ids = set(kost_facility_ids).intersection(set(user_facility_ids))
    matched_weight = sum(FACILITY_WEIGHTS.get(fac_id, 3.0) for fac_id in matched_ids)

    return (matched_weight / user_max_weight) * 100.0

def calculate_topsis(kost, user_facilities, user_priorities, univ_id=None):
    if not kost :
        return []

    kost_list = list(kost)
    user_fac_ids = [int(f) for f in user_facilities if str(f).isdigit()]

    criteria_keys = ['harga', 'jarak', 'fasilitas']
    criteria_types = {
        'harga': -1,
        'jarak': -1,
        'fasilitas': 1,
    }

    # Normalisasi Bobot
    total_priority = sum(user_priorities.get(k, 3) for k in criteria_keys)
    if total_priority == 0:
        weights = np.array([1 / 3, 1 / 3, 1 / 3])
    else:
        weights = np.array([
            user_priorities.get(k, 3) / total_priority for k in criteria_keys
        ])

    # Pembentukan Matriks Keputusan (X) ukuran N x 3
    matrix =[]
    for k in kost_list:
        dist_val = k.distance_to_campus_2 if str(univ_id) == '2' else k.distance_to_campus_1
        kost_fac_ids = list(k.kost_facilities.values_list('facility_id', flat=True))
        fac_score = calculate_facility_score(kost_fac_ids, user_fac_ids)
        matrix.append([
            float(k.price),
            float(dist_val),
            fac_score,
        ])

    X = np.array(matrix, dtype=float)
    num_houses, num_criteria = X.shape

    norm_factors = np.sqrt(np.sum(X**2, axis=0))
    norm_factors[norm_factors == 0] = 1.0
    R = X / norm_factors

    Y = R * weights

    A_pos = np.zeros(num_criteria)
    A_neg = np.zeros(num_criteria)

    for j, key in enumerate(criteria_keys):
        if criteria_types[key] == 1:
            A_pos[j] = np.max(Y[:, j])
            A_neg[j] = np.min(Y[:, j])
        else:
            A_pos[j] = np.min(Y[:, j])
            A_neg[j] = np.max(Y[:, j])

    D_pos = np.sqrt(np.sum((Y - A_pos) ** 2, axis=1))
    D_neg = np.sqrt(np.sum((Y - A_neg) ** 2, axis=1))

    denom = D_pos + D_neg
    denom[denom == 0] = 1.0
    V = D_neg / denom
    if num_houses == 1:
        V = np.array([1.0])

    # 8. Pengurutan Rangking
    min_price = X[:, 0].min()
    min_dist = X[:, 1].min()

    results = []
    for i, k in enumerate(kost_list):
        price, dist, fac = X[i]
        results.append({
            'kost': k,
            'score': round(float(V[i]), 4),
            'facility_score': round(float(fac), 2),
            'id': k.id,
            'price': int(price),
            'price_display': 'Rp' + f"{int(price):,}".replace(',', '.'),
            'distance': dist,
            'room_type': k.gender_type,
            'facilities': list(
                k.kost_facilities.values_list('facility__name', flat=True)
            ),
            'scores': {
                'harga': round(min_price / price * 100) if price else 0,
                'jarak': round(min_dist / dist * 100) if dist else 100,
                'fasilitas': round(fac),
                'keamanan': 0,
            },
        })

    results.sort(key=lambda item: item['score'], reverse=True)
    for rank, item in enumerate(results, start=1):
        item['rank'] = rank

    return results
    