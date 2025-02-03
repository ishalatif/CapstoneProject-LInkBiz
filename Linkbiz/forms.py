from django import forms
from .models import Profile_Investor, WithdrawRequest
from.models import Pendanaan
from django.contrib.auth.models import User

class FirstRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = Profile_Investor
        fields = ['fullname', 'email', 'password', 'phone']  # Tambahkan 'email' di sini

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Email sudah digunakan. Silakan pilih email lain.")
        return email
    
class SecondRegisterForm(forms.ModelForm):

    class Meta():
        model = Profile_Investor
        fields = ['ktp', 'npwp', 'no_rek', 'foto']

class PengaturanForm(forms.ModelForm):
    class Meta:
        model = Profile_Investor
        fields = ['foto']  

class PendanaanForm(forms.ModelForm):
    class Meta:
        model = Pendanaan
        fields = ['bukti_transfer']

class WithdrawRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawRequest
        fields = ['jumlah_tarik', 'rekening_tujuan']
        widgets = {
            'jumlah_tarik': forms.NumberInput(attrs={'placeholder': 'Jumlah Tarik'}),
            'rekening_tujuan': forms.TextInput(attrs={'placeholder': 'Nomor Rekening Tujuan'}),
        }

    def clean_jumlah_tarik(self):
        jumlah_tarik = self.cleaned_data.get('jumlah_tarik')
        if jumlah_tarik <= 0:
            raise forms.ValidationError("Jumlah tarik harus lebih besar dari nol.")
        return jumlah_tarik

    def clean_rekening_tujuan(self):
        rekening_tujuan = self.cleaned_data.get('rekening_tujuan')
        if len(rekening_tujuan) < 10:
            raise forms.ValidationError("Nomor rekening tidak valid.")
        return rekening_tujuan