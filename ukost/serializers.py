from rest_framework import serializers
from .models import Kost, History
from .constants import PRIORITY_CRITERIA

class KostSerializer(serializers.ModelSerializer):
    facilities = serializers.SerializerMethodField()

    class Meta:
        model = Kost
        fields = [
            'id', 'name', 'gender_type', 'location', 'address_details',
            'price', 'distance_to_campus_1', 'distance_to_campus_2',
            'waiting_list', 'no_deposit_required', 'facilities',
        ]

    def get_facilities(self, obj):
        return [kf.facility.name for kf in obj.kost_facilities.all()]

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = [
            'id', 'university', 'gender', 'budget_limit', 'radius_limit',
            'facility', 'criteria_weight', 'search_time',
        ]

class RecommendationInputSerializer(serializers.Serializer):
    univ = serializers.IntegerField()
    room_type = serializers.ChoiceField(
        choices=['Semua', 'Putra', 'Putri', 'Campur'], default='Semua'
    )
    max_price = serializers.IntegerField(required=False, min_value=0)
    max_distance = serializers.IntegerField(required=False, min_value=0)
    facilities = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    priorities = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        required=False, default=dict,
    )