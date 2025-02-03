from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile_Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    foto = models.ImageField(upload_to='foto_investor/')
    ktp = models.ImageField(upload_to='ktp_images/')
    npwp = models.CharField(max_length=20)
    no_rek = models.CharField(max_length=20)

    def __str__(self):
        return self.fullname

class UMKM(models.Model):
    Jenis_umkm = models.CharField(max_length=150)
    nama_umkm = models.CharField(max_length=150)
    alamat_umkm = models.TextField()
    foto_umkm = models.ImageField(upload_to='foto_umkm/')
    deskripsi = models.TextField()
    dana = models.CharField(max_length=150)
    bagi_hasil = models.CharField(max_length=50, default="12% Per tahun")
    tenor = models.CharField(max_length=50, default="Per bulan")
    proposal = models.FileField(upload_to='proposals/')
    laporan_keuangan = models.FileField(upload_to='laporan_keuangan/')  

    def __str__(self):
        return self.nama_umkm 
    
class Webinar(models.Model):
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField()
    gambar = models.ImageField(upload_to='webinar_images/')
    tanggal = models.DateField(default=date.today)
    waktu = models.TimeField()
    pembicara = models.CharField(max_length=200)
    link_zoom = models.URLField()
    meeting_id = models.CharField(max_length=50)
    passcode = models.CharField(max_length=50)

    def __str__(self):
        return self.judul
    
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Profile_Investor, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]  # Menampilkan hanya 50 karakter pertama

    def get_wrapped_content(self):
        # Memastikan konten tidak terlalu panjang
        max_length = 100  # Batas panjang maksimum per baris
        return '\n'.join([self.text[i:i+max_length] for i in range(0, len(self.text), max_length)])

class Pendanaan(models.Model):
    STATUS_CHOICES = [
        ('Lancar', 'Lancar'),
        ('Terlambat 30-60 Hari', 'Terlambat 30-60 Hari'),
        ('Terlambat 61-90 Hari', 'Terlambat 61-90 Hari'),
        ('Kurang Lancar > 90 Hari', 'Kurang Lancar > 90 Hari'),
    ]

    investor = models.ForeignKey(Profile_Investor, on_delete=models.CASCADE, related_name='pendanaan_investor')
    umkm = models.ForeignKey(UMKM, on_delete=models.CASCADE, related_name='pendanaan_umkm')
    nominal_dana = models.IntegerField()
    bukti_transfer = models.ImageField(upload_to='bukti_transfer/')
    tanggal_pendanaan = models.DateTimeField()
    status_pendanaan = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"Pendanaan {self.investor.fullname} untuk {self.umkm.nama_umkm}"
    
@receiver(post_save, sender=Pendanaan)
def create_status_notification(sender, instance, created, **kwargs):
    # Jika status pendanaan diubah, buat notifikasi baru
    if not created and instance.status_pendanaan:  # Hanya jalankan jika bukan objek baru dan status tidak kosong
        text = (f"UMKM {instance.umkm.nama_umkm} melakukan pendanaan dengan status "
                f"{instance.get_status_pendanaan_display()}. Cek detailnya disini!")
        
        # Periksa apakah notifikasi dengan teks yang sama sudah ada sebelumnya
        if not Comment.objects.filter(
            author=instance.investor,  # Perbaiki ke instance Profile_Investor
            text=text
        ).exists():
            # Membuat notifikasi baru
            Comment.objects.create(
                author=instance.investor,  # Perbaiki ke instance Profile_Investor
                text=text,
            )
    
class WithdrawRequest(models.Model):
    investor = models.ForeignKey(Profile_Investor, on_delete=models.CASCADE)  # Menghubungkan dengan profile investor
    jumlah_tarik = models.IntegerField() # Jumlah uang yang ditarik
    rekening_tujuan = models.CharField(max_length=100)  # Nomor rekening tujuan

    created_at = models.DateTimeField(auto_now_add=True)  # Waktu pencairan diminta

    def __str__(self):
        return f"Withdraw {self.investor.user.username} - {self.jumlah_tarik}"
