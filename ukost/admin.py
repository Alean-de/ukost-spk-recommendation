from django.contrib import admin
from .models import (
    University,
    Faculty,
    StudyProgram,
    UserDetail,
    Kost,
    Facility,
    KostPromotion,
    KostFacility,
    Favorite,
    History
)

# Register your models here.
@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'nim', 'university', 'faculty', 'study_program')
    search_fields = ('user__username', 'nim', 'user__email')


@admin.register(Kost)
class KostAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender_type', 'price', 'location')
    list_filter = ('gender_type', 'waiting_list', 'no_deposit_required')
    search_fields = ('name', 'location')


@admin.register(StudyProgram)
class StudyProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')
    list_filter = ('faculty',)

admin.site.register(University)
admin.site.register(Faculty)
admin.site.register(Facility)
admin.site.register(KostPromotion)
admin.site.register(KostFacility)
admin.site.register(Favorite)
admin.site.register(History)
