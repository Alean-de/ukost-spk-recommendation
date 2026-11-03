from django.contrib.auth.models import User
from django.db.models import Count
import json
from .models import Kost, StudyProgram, Faculty, Facility, Policy, UserDetail


def dashboard_callback(request, context):
    context["cards"] = [
        {
            "title": "Total User",
            "metric": User.objects.count()
        },
        {
            "title": "Total Kost",
            "metric": Kost.objects.count(),
        },
        {
            "title": "Total Fasilitas",
            "metric": Facility.objects.count()
        },
        {
            "title": "Total Policy",
            "metric": Policy.objects.count()
        },
        {
            "title": "Fakultas",
            "metric": Faculty.objects.count()
        },
        {
            "title": "Program Studi",
            "metric": StudyProgram.objects.count()
        },
    ]

    fakultas_data = (
        UserDetail.objects
        .values('faculty__name')
        .annotate(total=Count('id'))
        .order_by('faculty__name')
    )

    labels = [f['faculty__name'] for f in fakultas_data]
    data = [f['total'] for f in fakultas_data]

    context["chart_user_fakultas"] = json.dumps({
        "labels": labels,
        "datasets": [
            {
                "label": "Jumlah User",
                "data": data,
                "backgroundColor": "var(--color-primary-600)",
            }
        ],
    })
    
    return context

    