from django.conf import settings
from django.db import models

# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    address_detail = models.CharField(max_length=355)

    class Meta:
        verbose_name_plural = 'Universities'

    def __str__(self):
        return self.name

class Faculty(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
            verbose_name_plural = 'Faculties'

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
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor WhatsApp/HP")
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Bio / Deskripsi Singkat")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Foto Profil")

    def __str__(self):
        return f"{self.user.username} ({self.nim})"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                return self.avatar.url
            except Exception:
                return None
        return None

class Cluster(models.Model):
    cluster = models.CharField(max_length=255)

class Kost(models.Model):
    class GenderType(models.TextChoices):
        CAMPUR = 'Campur'
        PUTRA = 'Putra'
        PUTRI = 'Putri'

    id = models.CharField(max_length=20, primary_key=True)
    cluster_id = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='kost_list', null=True, blank=True)
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
        return f"{self.name} - {self.cluster_id}"

class Facility(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Facilities'

    def __str__(self):
        return self.name

    @property
    def icon(self):
        icon_map = {
            'wifi': 'fas fa-wifi',
            'kamar mandi': 'fas fa-bath',
            'ac': 'fas fa-snowflake',
            'parkir': 'fas fa-car',
            'security': 'fas fa-shield-alt',
            'cctv': 'fas fa-video',
            'dapur': 'fas fa-utensils',
            'laundry': 'fas fa-tshirt',
            'listrik': 'fas fa-bolt',
            'akses 24': 'fas fa-clock',
            'furnitur': 'fas fa-couch',
            'kasur': 'fas fa-bed',
            'jendela': 'fas fa-window-maximize',
        }
        name_lower = self.name.lower()
        for key, val in icon_map.items():
            if key in name_lower:
                return val
        return 'fas fa-check-circle'

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
        verbose_name_plural = 'Kost Facilities'

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
    gender = models.CharField(max_length=10, choices=Kost.GenderType.choices, default=Kost.GenderType.CAMPUR)
    budget_limit = models.IntegerField()
    radius_limit = models.IntegerField()
    facility = models.JSONField()
    criteria_weight = models.JSONField()
    search_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Histories'

    def __str__(self):
        return f'History {self.user.username} - {self.search_time}'
