from django.contrib import admin
from .models import Profile_Investor, UMKM, Webinar, Pendanaan
from .models import Comment, WithdrawRequest
# Register your models here.
admin.site.register(Profile_Investor)
admin.site.register(Webinar)
admin.site.register(Pendanaan)
admin.site.register(WithdrawRequest)
    

@admin.register(UMKM)
class UMKMAdmin(admin.ModelAdmin):
    list_display = ("Jenis_umkm", "nama_umkm", "alamat_umkm", "foto_umkm", "deskripsi", "dana", "bagi_hasil", "tenor", "proposal", "laporan_keuangan") 


@admin.register(Comment)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'created_at')  # Field yang akan ditampilkan di daftar admin
    search_fields = ('text', 'author__username')  # Menambahkan pencarian berdasarkan text dan nama pengguna
    list_filter = ('created_at',)  # Menambahkan filter berdasarkan waktu pembuatan
    ordering = ('-created_at',)  # Mengurutkan komentar berdasarkan waktu terbaru

