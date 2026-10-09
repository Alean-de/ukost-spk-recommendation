from django.conf import settings
from django.db import models

# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address_detail = models.CharField(max_length=355)

    def __str__(self):
        return self.name

class Faculty(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class StudyProgram(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="study_programs")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.faculty.name}"

class UserDetail(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="studying_at")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="from_the_faculty")
    study_program = models.ForeignKey(StudyProgram, on_delete=models.CASCADE, related_name="from_the_study_program", blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    nim = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.nim})"

class Kost(models.Model):
    class GenderType(models.TextChoices):
        CAMPUR = 'Campur'
        PUTRA = 'Putra'
        PUTRI = 'Putri'

    gender_type = models.CharField(
        max_length=10,
        choices=GenderType.choices,
        default=GenderType.CAMPUR
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address_details = models.CharField(max_length=355)
    price = models.IntegerField()
    distance_to_campus_1 = models.IntegerField()
    distance_to_campus_2 = models.IntegerField()
    waiting_list = models.BooleanField(default=False)
    no_deposit_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Facility(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class KostPromotion(models.Model):
    kost = models.ForeignKey(Kost, on_delete=models.CASCADE, related_name="promotions")
    discount_name = models.CharField(max_length=255)
    is_first_month_promo = models.BooleanField(default=False)
    first_month_discount = models.IntegerField(default=0, help_text='Potongan harga pada bulan pertama')
    other_promo_label = models.CharField(max_length=255, blank=True, null=True)
    has_long_term_promo = models.BooleanField(default=False)
    long_term_promo_detail = models.CharField(max_length=255, blank=True, null=True)
    long_term_savings_amount = models.IntegerField(default=0, help_text='Jumlah penghematan sewa jangka panjang')

    def __str__(self):
        return f'{self.kost.name} - {self.discount_name}'

class KostFacility(models.Model):
    kost = models.ForeignKey(Kost, on_delete=models.CASCADE, related_name="kost_facilities")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="facility_kosts")

    class Meta:
        unique_together = ('kost', 'facility')

    def __str__(self):
        return f"{self.kost.name} - {self.facility.name}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_favorites")
    kost = models.ForeignKey(Kost, on_delete=models.CASCADE, related_name="favorited_by")
    time_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'kost')

    def __str__(self):
        return f"{self.user.username} - {self.kost.name}"

class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_histories")
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="histories")
    budget_limit = models.IntegerField()
    radius_limit = models.IntegerField()
    facility = models.JSONField()
    criteria_weight = models.JSONField()
    search_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Histories'

    def __str__(self):
        return f'History {self.user.username} - {self.search_time}'