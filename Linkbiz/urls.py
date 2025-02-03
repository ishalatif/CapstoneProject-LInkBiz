from django.urls import path
from . import views

app_name = 'linkbiz'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('pusban/', views.pusban_view, name='pusban'),
    path('snk/', views.snk_view, name='snk'),
    path('register_first/', views.register_first, name='register_first'),
    path('register_second/', views.register_second, name='register_second'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('daftarumkm/', views.daftarumkm_view, name='daftarumkm'),
    path('aktivitas/', views.aktivitas_view, name='aktivitas'),
    path('pengaturan/', views.pengaturan_view, name='pengaturan'),
    path('portofolio/', views.portofolio_view, name='portofolio'),
    path('profile/', views.profile_view, name='profile'),

    path('lupa_password/', views.lupa_password_form, name='lupa_password'),

    path('danai/', views.danai_view, name='danai'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('danaisekarang/<int:umkm_id>/', views.danaisekarang_view, name='danaisekarang'),
    path('kategoritampil/', views.kategoritampil_view, name='kategoritampil'),
    path('tentangmitra/<int:umkm_id>/', views.tentangmitra_view, name='tentangmitra'),
    path('proposalmitra/<int:umkm_id>/', views.proposalmitra_view, name='proposalmitra'),
    path('laporanbulanan/', views.laporanbulanan_view, name='laporanbulanan'),
    path('save-comment/', views.save_comment, name='save_comment'),
    path('payment-process/', views.payment_process, name='payment_process'),
    path('umkm/<int:umkm_id>/pendanaan/', views.unggah_pendanaan, name='unggah_pendanaan'),
    path('notif/', views.notif_view, name='notif'),
    path('ringkasan/', views.ringkasan_view, name='ringkasan'),
      path('download/<str:file_type>/<int:umkm_id>/', views.download_file, name='download_file'),

]
