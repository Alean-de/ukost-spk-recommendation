from django.contrib import admin
from unfold.sites import UnfoldAdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    University,
    Faculty,
    StudyProgram,
    UserDetail,
    Kost,
    Facility,
    KostPromotion,
    KostFacility,
    Cluster,
    Policy,
    KostPolicy,
)

class KostFacilityInline(TabularInline):
    model = KostFacility
    extra = 1
    autocomplete_fields = ["facility"]

class KostPolicyInline(TabularInline):
    model = KostPolicy
    extra = 1
    autocomplete_fields = ["policy"]

class KostPromotionInline(TabularInline):
    model = KostPromotion
    extra = 1

class FacultyInline(TabularInline):
    model = Faculty
    extra = 1

class StudyProgramInline(TabularInline):
    model = StudyProgram
    extra = 1

# Register your models here.
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_superuser", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(Kost)
class KostAdmin(ModelAdmin):
    list_display = ("name", "gender_type", "room_size", "electricity_type", "price", "location", "waiting_list", "no_deposit_required")
    list_filter = ("gender_type", "electricity_type", "waiting_list", "no_deposit_required")
    search_fields = ("name", "location")
    inlines = [
        KostFacilityInline, 
        KostPolicyInline,
        KostPromotionInline
        ]


@admin.register(UserDetail)
class UserDetailAdmin(ModelAdmin):
    list_display = ('nim', 'university', 'faculty')
    search_fields = ('nim', 'user__first_name', 'user__last_name')
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'user':
            field.label_from_instance = (
                lambda u: f"{u.username} - {u.get_full_name() or '(tanpa nama)'}"
            )
        return field
       
@admin.register(StudyProgram)
class StudyProgramAdmin(ModelAdmin):
    list_display = ("name", "faculty")
    list_filter = ("faculty",)
    search_fields = ("name", "faculty__name",)

@admin.register(University)
class UniversityAdmin(ModelAdmin):
    list_display = ("name", "location", "address_detail")
    search_fields = ("name", "location")
    # inlines = [FacultyInline]

@admin.register(Faculty)
class FacultyAdmin(ModelAdmin):
    list_display = ("name", )
    inlines = [StudyProgramInline]

@admin.register(Facility)
class FacilityAdmin(ModelAdmin):
    list_display = ("name", )
    search_fields = ("name",)

@admin.register(Cluster)
class ClusterAdmin(ModelAdmin):
    list_display = ("cluster", )

@admin.register(Policy)
class PolicyAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)