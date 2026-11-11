from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Kost, History
from .serializers import (
    KostSerializer, HistorySerializer, RecommendationInputSerializer,
)
from .services import apply_hard_filters, calculate_topsis
from .constants import PRIORITY_CRITERIA

class KostListAPI(generics.ListAPIView):
    queryset = Kost.objects.prefetch_related('kost_facilities__facility')
    serializer_class = KostSerializer

class KostDetailAPI(generics.RetrieveAPIView):
    queryset = Kost.objects.prefetch_related('kost_facilities__facility')
    serializer_class = KostSerializer
    lookup_url_kwarg = 'kost_id'

class RecommendationAPI(APIView):
    def post(self, request):
        s = RecommendationInputSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        priorities = {
            c['id']: d['priorities'].get(c['id'], 3) for c in PRIORITY_CRITERIA
        }

        queryset = apply_hard_filters(
            campus_id=d['univ'],
            room_type=d['room_type'],
            max_price=d.get('max_price'),
            max_distance=d.get('max_distance'),
            mandatory_facilities=d['facilities'],
        )
        results = calculate_topsis(
            kost=queryset,
            user_priorities=priorities,
            univ_id=d['univ'],
        )

        History.objects.create(
            user=request.user,
            university_id=d['univ'],
            gender=d['room_type'],
            budget_limit=d['max_price'] or 0,
            radius_limit=d['max_distance'] or 0,
            facility=d['facilities'],
            criteria_weight=priorities,

        )

        limit = int(request.query_params.get('limit', 5))
        data = [{
            'rank': r['rank'],
            'score': r['score'],
            'facility_score': r['facility_score'],
            'scores': r['scores'],
            'kost': KostSerializer(r['kost']).data,
        } for r in results[:limit]]

        return Response({'count': len(results), 'results': data})

class HistoryListAPI(generics.ListAPIView):
    serializer_class = HistorySerializer

    def get_queryset(self):
        return History.objects.filter(user=self.request.user).order_by('-search_time')