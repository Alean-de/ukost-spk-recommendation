"""
URL routing for U Kost application.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Main pages
    path('', views.home_view, name='home'),
    path('cari-kost/', views.cari_kost_view, name='cari_kost'),
    path('cari-kost/fasilitas/', views.fasilitas_view, name='fasilitas'),
    path('cari-kost/prioritas/', views.prioritas_view, name='prioritas'),
    path('rekomendasi/', views.rekomendasi_view, name='rekomendasi'),
    path('kost/<int:kost_id>/', views.detail_kost_view, name='detail_kost'),
    path('bandingkan/', views.bandingkan_view, name='bandingkan'),
    path('favorit/', views.favorit_view, name='favorit'),
    path('riwayat/', views.riwayat_view, name='riwayat'),

    # API endpoints
    path('api/kost/', views.api_kost_list, name='api_kost_list'),
    path('api/kost/<int:kost_id>/', views.api_kost_detail, name='api_kost_detail'),
]
