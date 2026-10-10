from django import forms
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.forms import User
from django.contrib.auth.forms import UserCreationForm
from .models import Faculty, University, UserDetail

class StudentRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label='Nama Lengkap',
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': 'reg_nama',
                'placeholder': 'Nama Lengkap Sesuai KTM',
                'class': 'form-control'
            }
        ),
    )

    nim = forms.CharField(
        label='Nim',
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': 'reg_nim',
                'placeholder': 'Contoh: 412021000',
                'class': 'form-control'
            }
        ),
    )

    university = forms.ModelChoiceField(
        queryset=University.objects.all(),
        required=True,
        empty_label='Pilih Kampus Utama Anda',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        required=True,
        empty_label='Pilih Fakultas Anda',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(
            attrs={
                'id': 'reg_email',
                'placeholder': 'Masukkan Email Civitas',
                'class': 'form-control'
            }
        )
    )

    password1 = forms.CharField(
        label='Kata Sandi',
        widget=forms.PasswordInput(
            attrs={
                'id': 'reg_pass',
                'class': 'form-control',
                'placeholder': '••••••••',
            }
        ),
    )
    password2 = forms.CharField(
        label='Konfirmasi Sandi',
        widget=forms.PasswordInput(
            attrs={
                'id': 'reg_confirm',
                'class': 'form-control',
                'placeholder': '••••••••',
            }
        ),
    )

    class Meta:
        model = User
        fields = ['email']

    def clean_nim(self):
        nim = self.cleaned_data['nim']
        if User.objects.filter(username=nim).exists():
            raise forms.ValidationError('Nim ini sudah terdaftar.')
        return nim

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['nim']
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data.get('full_name', '').strip()

        if full_name:
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = (
                name_parts[1] if len(name_parts) > 1 else ''
            )

        if commit:
            with transaction.atomic():
                user.save() 
                UserDetail.objects.create(
                    user=user,
                    nim=self.cleaned_data['nim'],
                    university=self.cleaned_data['university'],
                    faculty=self.cleaned_data['faculty']
                )

        return user

class StudentLoginForm(forms.Form):
    nim = forms.CharField(
        label='NIM',
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': '',
                'placeholder': 'Masukkan NIM',
                'class': 'form-control'
            }
        )
    )
    
    university = forms.ModelChoiceField(
        queryset=University.objects.all(),
        required=True,
        empty_label='Pilih Kampus Utama Anda',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label='Kata Sandi',
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'id': '',
                'placeholder': '••••••••',
                'class': 'form_control'
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        nim = cleaned_data.get('nim')
        university = cleaned_data.get('university')
        password = cleaned_data.get('password')

        if nim and password and university:
            try:
                user_detail = UserDetail.objects.select_related('user').get(
                    nim=nim,
                    university=university
                )

                user_obj = user_detail.user

                user = authenticate(username=user_obj.username, password=password)

                if user is None:
                    raise forms.ValidationError('Nim/Universitas atau Password Anda Salah')
                if not user.is_active:
                    raise forms.ValidationError('Akun Ini Sudah Tidak Aktif')
                cleaned_data['user'] = user
            except UserDetail.DoesNotExist:
                raise forms.ValidationError('NIM/Universitas atau Password Anda Salah')

        return cleaned_data
