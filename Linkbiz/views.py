from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from Linkbiz.forms import FirstRegisterForm, SecondRegisterForm, PengaturanForm, PendanaanForm, WithdrawRequestForm
from Linkbiz.models import Profile_Investor, UMKM, Webinar, Pendanaan, Comment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.http import FileResponse, Http404
from .models import UMKM
import logging
from datetime import date

def home_view(request):
    return render(request, 'homepage/home.html')

def about_view(request):
    return render(request, 'homepage/about.html')

def pusban_view(request):
    return render(request, 'homepage/pusban.html')

def snk_view(request):
    return render(request, 'homepage/snk.html')

def register_first(request):
    if request.method == 'POST':
        form = FirstRegisterForm(request.POST)
        if form.is_valid():
             # Simpan user terlebih dahulu
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # Buat Profile_Investor terkait dengan user
            profile = Profile_Investor.objects.create(
                user=user,
                fullname=form.cleaned_data['fullname'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone']
            )
            # Lakukan login otomatis jika diperlukan
            login(request, user)
            return redirect('linkbiz:register_second')
    else:
        form = FirstRegisterForm()

    return render(request, 'homepage/register_first.html', {'form': form})

def register_second(request):
    if request.method == 'POST':
        form = SecondRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.profile_investor
            profile.ktp = form.cleaned_data['ktp']
            profile.npwp = form.cleaned_data['npwp']
            profile.no_rek = form.cleaned_data['no_rek']
            profile.foto = form.cleaned_data['foto']
            profile.save()
            return redirect('linkbiz:login')
    else:
        form = SecondRegisterForm()
    return render(request, 'homepage/register_second.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('linkbiz:dashboard')
        else:
            return render(request, 'login.html', {'error': 'Email atau Password Salah!'})
    return render(request, 'homepage/login.html')

def logout_view(request):
    logout(request)
    return redirect('linkbiz:login')

@login_required
def dashboard_view(request):
    webinars = Webinar.objects.all()
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    # Hitung jumlah UMKM yang sudah didanai oleh investor
    pendanaan_investor = Pendanaan.objects.filter(investor=profile_investor)
    jumlah_umkm_didanai = pendanaan_investor.values('umkm').distinct().count()

    # Hitung total dana yang sudah didanai oleh investor
    total_dana_mendanai = sum(pendanaan.nominal_dana for pendanaan in pendanaan_investor)

    bunga_lancar = total_dana_mendanai * 0.12  # 12% bunga
    total_lancar = bunga_lancar  # Mitra Lancar: hanya bunga

    context = {
        'profile_investor': profile_investor,
        'webinars': webinars,
        'jumlah_umkm_didanai': jumlah_umkm_didanai,
        'total_dana_mendanai': total_dana_mendanai,
        'total_lancar': total_lancar,
    }

    
    # Lanjutkan dengan render dashboard jika Profile_Investor ada
    return render(request, 'investor/dashboard.html', context)

def daftarumkm_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    jenis_filter = request.GET.get('filter', 'Semua')

    # Dapatkan daftar UMKM yang sudah didanai oleh investor
    umkm_sudah_didanai = Pendanaan.objects.filter(investor=profile_investor).values_list('umkm_id', flat=True)

    if jenis_filter == 'Semua':
        umkm_list = UMKM.objects.exclude(id__in=umkm_sudah_didanai)
    else:
        umkm_list = UMKM.objects.filter(Jenis_umkm=jenis_filter).exclude(id__in=umkm_sudah_didanai)

    return render(request, 'investor/daftarumkm.html', {
        'umkm_list': umkm_list, 
        'selected_filter': jenis_filter, 
        'profile_investor': profile_investor})

def aktivitas_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    # Ambil semua pendanaan yang diberikan oleh investor
    pendanaan_list = Pendanaan.objects.filter(investor=profile_investor)
    
    # Hitung total dana yang sudah didanai oleh investor
    total_dana_mendanai = sum(pendanaan.nominal_dana for pendanaan in pendanaan_list)

    # Kirim data pendanaan dan total dana ke template
    context = {
        'profile_investor': profile_investor,
        'pendanaan_list': pendanaan_list,
        'total_dana_mendanai': total_dana_mendanai,
    }
    
    return render(request, 'investor/aktivitas.html', context)

def pengaturan_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    if request.method == 'POST' and request.FILES.get('foto'):
        form = PengaturanForm(request.POST, request.FILES, instance=profile_investor)
        if form.is_valid():
            form.save()
            return redirect('linkbiz:pengaturan')
    else:
        form = PengaturanForm(instance=profile_investor)
    
    return render(request, 'investor/pengaturan.html', {'form': form, 'profile_investor': profile_investor})

def portofolio_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    # Ambil semua pendanaan yang diberikan oleh investor
    pendanaan_list = Pendanaan.objects.filter(investor=profile_investor)
    
    # Hitung total dana yang sudah didanai oleh investor
    total_dana_mendanai = sum(pendanaan.nominal_dana for pendanaan in pendanaan_list)

    # Kirim data pendanaan dan total dana ke template
    context = {
        'profile_investor': profile_investor,
        'pendanaan_list': pendanaan_list,
        'total_dana_mendanai': total_dana_mendanai,
    }
    
    return render(request, 'investor/portofolio.html', context)

def withdraw_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    # Hitung kembali profit_lancar dari data pendanaan
    pendanaan_investor = Pendanaan.objects.filter(investor=profile_investor, status_pendanaan='Lancar')
    profit_lancar = sum((pendanaan.nominal_dana + pendanaan.nominal_dana * 0.12) for pendanaan in pendanaan_investor)
    
    if request.method == 'POST':
        form = WithdrawRequestForm(request.POST)
        if form.is_valid():
            withdraw_request = form.save(commit=False)
            withdraw_request.investor = profile_investor  # Menyimpan investor yang sedang login
            withdraw_request.save()  # Simpan permintaan withdraw ke database

            # Update status pendanaan dan set profit_lancar ke 0
            pendanaan_investor.update(status_pendanaan='Ditutup')
            
            # Menyimpan status dalam session atau menampilkan pesan sukses
            request.session['total_profit_ditarik'] = True
            messages.success(request, "Penarikan berhasil! Dana telah ditransfer.")

            return redirect('linkbiz:kategoritampil')  # Redirect ke halaman yang sesuai
    else:
        form = WithdrawRequestForm()
    
    context = {
        'profile_investor': profile_investor,
        'profit_lancar': profit_lancar,
        'form': form
    }

    return render(request, 'investor/withdraw.html', context)

def profile_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    if request.method == 'POST' and request.FILES.get('foto'):
        form = PengaturanForm(request.POST, request.FILES, instance=profile_investor)
        if form.is_valid():
            form.save()
            return redirect('linkbiz:profile')
    else:
        form = PengaturanForm(instance=profile_investor)
    return render(request, 'investor/profile.html', {'profile_investor': profile_investor})

def lupa_password_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        try:
            user = User.objects.get(email=email)
            if new_password1 != new_password2:
                messages.error(request, "Password baru tidak cocok.")
                return redirect('linkbiz:lupa_password')
            if len(new_password1) < 8:
                messages.error(request, "Password baru harus minimal 8 karakter.")
                return redirect('linkbiz:lupa_password')

            user.set_password(new_password1)
            user.save()
            messages.success(request, "Password berhasil diubah. Silakan login dengan password baru.")
            return redirect('linkbiz:login')
        except User.DoesNotExist:
            messages.error(request, "Email tidak ditemukan.")
            return redirect('linkbiz:lupa_password')
    return render(request, 'homepage/lupa_password_form.html')

def danai_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    return render(request, 'investor/danai.html', {'profile_investor': profile_investor})

def danaisekarang_view(request, umkm_id):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')

    umkm = UMKM.objects.get(id=umkm_id)
    return render(request, 'investor/danaisekarang.html', {'profile_investor': profile_investor,'umkm': umkm})

def unggah_pendanaan(request, umkm_id):
    umkm = get_object_or_404(UMKM, id=umkm_id)

    # Mendapatkan objek Profile_Investor yang terkait dengan user yang sedang login
    profile_investor = get_object_or_404(Profile_Investor, user=request.user)
    
    if request.method == 'POST':
        form = PendanaanForm(request.POST, request.FILES)
        if form.is_valid():
            pendanaan = form.save(commit=False)
            pendanaan.investor = profile_investor
            pendanaan.umkm = umkm
            
            # Pastikan field `tanggal_pendanaan` diisi (gunakan tanggal hari ini)
            pendanaan.tanggal_pendanaan = date.today()

            # Konversi nilai dana dari CharField ke Integer (pastikan nilai valid)
            try:
                umkm.dana = int(umkm.dana.replace(".", ""))
            except ValueError:
                umkm.dana = 0  # Default jika terjadi kesalahan konversi

            pendanaan.nominal_dana = umkm.dana
            pendanaan.save()
            messages.success(request, "Pendanaan berhasil dikirim!")
            return redirect('linkbiz:portofolio')  # Ganti dengan URL tujuan setelah sukses
    else:
        form = PendanaanForm()
    
    return render(request, 'investor/danaisekarang.html', {'form': form, 'umkm': umkm})

def kategoritampil_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    # Hitung jumlah UMKM yang sudah didanai oleh investor dan Filter pendanaan hanya untuk investor yang sedang login
    pendanaan_investor = Pendanaan.objects.filter(investor=profile_investor)
    jumlah_umkm_didanai = pendanaan_investor.values('umkm').distinct().count()
    
    jumlah_umkm_didanai_lancar = pendanaan_investor.filter(status_pendanaan='Lancar').count()
    jumlah_umkm_didanai_terlambat_30_60 = pendanaan_investor.filter(status_pendanaan='Terlambat 30-60 Hari').count()
    jumlah_umkm_didanai_terlambat_61_90 = pendanaan_investor.filter(status_pendanaan='Terlambat 61-90 Hari').count()
    jumlah_umkm_didanai_kurang_lancar = pendanaan_investor.filter(status_pendanaan='Kurang Lancar > 90 Hari').count()

    pendanaan_investor_lancar = pendanaan_investor.filter(status_pendanaan='Lancar')
    total_lancar = sum( pendanaan.nominal_dana * 0.12 for pendanaan in pendanaan_investor_lancar)
    profit_lancar = sum( (pendanaan.nominal_dana + pendanaan.nominal_dana * 0.12) for pendanaan in pendanaan_investor_lancar)
    
    if request.session.get('total_profit_ditarik'):
        totalprofit = 0
        profit_lancar = 0
        total_lancar = 0
        del request.session['total_profit_ditarik']  # Hapus flag setelah digunakan
    else:
        totalprofit = total_lancar

    pendanaan_investor_terlambat_30_60 = pendanaan_investor.filter(status_pendanaan='Terlambat 30-60 Hari')
    total_terlambat_30_60 = sum( (pendanaan.nominal_dana * 0.12 + pendanaan.nominal_dana * 0.02) for pendanaan in pendanaan_investor_terlambat_30_60)
    profit_terlambat_30_60 = sum( (pendanaan.nominal_dana + pendanaan.nominal_dana * 0.12 + pendanaan.nominal_dana * 0.02) for pendanaan in pendanaan_investor_terlambat_30_60)
    
    pendanaan_investor_terlambat_61_90 = pendanaan_investor.filter(status_pendanaan='Terlambat 61-90 Hari')
    total_terlambat_61_90 = sum( (pendanaan.nominal_dana * 0.12 + pendanaan.nominal_dana * 0.05) for pendanaan in pendanaan_investor_terlambat_61_90)
    profit_terlambat_61_90 = sum( (pendanaan.nominal_dana + pendanaan.nominal_dana * 0.12  + pendanaan.nominal_dana * 0.05) for pendanaan in pendanaan_investor_terlambat_61_90)

    pendanaan_investor_kurang_lancar = pendanaan_investor.filter(status_pendanaan='Kurang Lancar > 90 Hari')
    total_kurang_lancar = sum( (pendanaan.nominal_dana * 0.12 + pendanaan.nominal_dana * 0.10) for pendanaan in pendanaan_investor_kurang_lancar)
    profit_kurang_lancar = sum( (pendanaan.nominal_dana + pendanaan.nominal_dana * 0.12 + pendanaan.nominal_dana * 0.10) for pendanaan in pendanaan_investor_kurang_lancar)
    
    totalprofit = total_lancar+total_kurang_lancar+total_terlambat_30_60+total_terlambat_61_90+total_kurang_lancar


    context = {
        'profile_investor': profile_investor,
        'jumlah_umkm_didanai': jumlah_umkm_didanai,
        'total_lancar': total_lancar,
        'total_terlambat_30_60': total_terlambat_30_60,
        'total_terlambat_61_90': total_terlambat_61_90,
        'total_kurang_lancar': total_kurang_lancar,
        'profit_lancar': profit_lancar,
        'profit_terlambat_30_60': profit_terlambat_30_60,
        'profit_terlambat_61_90': profit_terlambat_61_90,
        'profit_kurang_lancar': profit_kurang_lancar,
        'totalprofit': totalprofit,
        'jumlah_umkm_didanai_lancar': jumlah_umkm_didanai_lancar,
        'jumlah_umkm_didanai_terlambat_30_60': jumlah_umkm_didanai_terlambat_30_60,
        'jumlah_umkm_didanai_terlambat_61_90': jumlah_umkm_didanai_terlambat_61_90,
        'jumlah_umkm_didanai_kurang_lancar': jumlah_umkm_didanai_kurang_lancar
    }

    return render(request, 'investor/kategoritampil.html', context)

def proposalmitra_view(request, umkm_id):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')

    umkm = UMKM.objects.get(id=umkm_id)
    return render(request, 'investor/proposalmitra.html', {'profile_investor': profile_investor,'umkm': umkm})

def tentangmitra_view(request, umkm_id):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')

    umkm = UMKM.objects.get(id=umkm_id)

    # Logika perhitungan
    try:
        modal = int(umkm.dana.replace('.', '').replace(',', '').replace('Rp ', ''))  # Ubah dana ke integer
    except ValueError:
        modal = 0  # Jika dana tidak valid, atur modal ke 0
    
    bagi_hasil = modal * 0.12  # 12% dari modal
    total_pembayaran = modal + bagi_hasil
    jumlah_angsuran = total_pembayaran / 12  # Contoh: Tenor default 12 bulan

    # Fungsi untuk memformat angka ke format Rupiah
    def format_rupiah(amount):
        return f"{round(amount):,}".replace(",", ".")

    context = {
        'profile_investor': profile_investor,
        'umkm': umkm,
        'modal': format_rupiah(modal),
        'bagi_hasil': format_rupiah(bagi_hasil),
        'jumlah_angsuran': format_rupiah(jumlah_angsuran),
    }

    return render(request, 'investor/tentangmitra.html', context)

def laporanbulanan_view(request): 
    try:
        # Get the investor profile of the logged-in user
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # If not found, redirect to login page
        return redirect('linkbiz:login')

    # Fetch the Pendanaan instances related to this investor
    pendanaan_list = Pendanaan.objects.filter(investor=profile_investor)

    # Gather the related UMKM names from Pendanaan
    daftar_umkm = []
    for pendanaan in pendanaan_list:
        daftar_umkm.append({
            'nama_umkm': pendanaan.umkm.nama_umkm,  # Access UMKM through Pendanaan
            'id_umkm': pendanaan.umkm.id
        })

    # Pass daftar_umkm to the template
    return render(request, 'investor/laporanbulanan.html', {
        'profile_investor': profile_investor,
        'daftar_umkm': daftar_umkm,
    })


def notif_view(request):
    try:
        # Ambil instansi Profile_Investor yang terkait dengan user yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada Profile_Investor untuk user ini, redirect ke halaman login
        return redirect('linkbiz:login')

    # Ambil semua pendanaan yang sudah dilakukan oleh investor
    pendanaan_list = Pendanaan.objects.filter(investor=profile_investor)

    # Tambahkan notifikasi (komentar) untuk setiap pendanaan yang berhasil
    for pendanaan in pendanaan_list:
        # Buat teks notifikasi untuk setiap pendanaan yang berhasil
        notif_text = (f"Berhasil berinvestasi sebesar Rp {pendanaan.nominal_dana:,} "
                      f"kepada {pendanaan.umkm.nama_umkm}. Cek detailnya disini!")

        # Periksa apakah komentar dengan teks yang sama sudah ada sebelumnya
        if not Comment.objects.filter(author=profile_investor, text=notif_text).exists():
            # Membuat komentar baru sebagai notifikasi hanya jika belum ada sebelumnya
            Comment.objects.create(
                author=profile_investor,  # Gunakan profile_investor sebagai author
                text=notif_text,
            )

    # Ambil komentar yang sudah dibuat untuk ditampilkan di notifikasi
    notifications = Comment.objects.filter(author=profile_investor).order_by('-created_at')

    # Render halaman dengan data yang diperlukan
    return render(request, 'investor/notif.html', {
        'profile_investor': profile_investor,
        'notifications': notifications
    })

def ringkasan_view(request):
    try:
        # Coba ambil Profile_Investor terkait pengguna yang sedang login
        profile_investor = Profile_Investor.objects.get(user=request.user)
    except Profile_Investor.DoesNotExist:
        # Jika tidak ada, redirect ke halaman registrasi kedua atau halaman lain
        return redirect('linkbiz:login')
    
    return render(request, 'investor/ringkasan.html', {'profile_investor': profile_investor})

def save_comment(request):
    if request.method == "POST":
        comment_text = request.POST.get("comment_text")
        month = request.POST.get("month")
        year = request.POST.get("year")
        umkm_name = request.POST.get("umkm")

        # Validasi input
        if not comment_text or not month or not year or not umkm_name:
            return JsonResponse({'success': False, 'error': 'Semua data harus diisi.'}, status=400)

        # Dapatkan Profile_Investor dari request.user
        profile_investor = get_object_or_404(Profile_Investor, user=request.user)

        # Dapatkan UMKM berdasarkan nama
        umkm = get_object_or_404(UMKM, nama_umkm=umkm_name)

        # Simpan komentar
        comment = Comment.objects.create(
            text=f"Anda mengirim komentar untuk UMKM {umkm.nama_umkm} pada bulan {month} {year}: {comment_text}",
            author=profile_investor,  # Gunakan Profile_Investor
        )

        # Kirim respons JSON
        return JsonResponse({
            'success': True,
            'comment': {
                'text': comment.text,
                'author': comment.author.user.username,  # Ambil username dari User terkait
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })

    # Jika bukan POST, kirim error
    return JsonResponse({'success': False, 'error': 'Gagal menyimpan komentar.'}, status=400)

def payment_process(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment-method')
        return redirect('linkbiz:dashboard')
    return render(request, 'error.html')

def download_file(request, file_type, umkm_id):
    try:
        # Ambil UMKM berdasarkan ID
        umkm = UMKM.objects.get(id=umkm_id)

        # Tentukan file yang akan diunduh berdasarkan file_type
        if file_type == 'proposal':
            file = umkm.proposal
        elif file_type == 'laporan':
            file = umkm.laporan_keuangan
        else:
            raise Http404("File tidak ditemukan")

        # Kembalikan file sebagai respons download
        response = FileResponse(file.open(), as_attachment=True)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{file.name}"'
        return response
    except UMKM.DoesNotExist:
        raise Http404("UMKM tidak ditemukan")
