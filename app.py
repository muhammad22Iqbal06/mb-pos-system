# =================================================================
# BAGIAN 1: IMPORT LIBRARY (Memasukkan Alat-Alat Tambahan)
# =================================================================
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Membuat aplikasi web server berbasis Flask
app = Flask(__name__)


# =================================================================
# BAGIAN 2: CLASS LAYANANTOKO (Penerapan Konsep OOP - Enkapsulasi)
# =================================================================
class LayananToko:
    def __init__(self):
        # [Properti/Atribut Class] DATA BARANG WARUNG (SURYA 16 SUDAH DIHAPUS)
        self.data_barang = {
            "1": {"nama": "Indomie Goreng", "stok": 50, "harga": 3500, "terjual": 0},
            "2": {"nama": "Kopi Kapal Api", "stok": 40, "harga": 2000, "terjual": 0},
            "3": {"nama": "Teh Pucuk Harum", "stok": 30, "harga": 4000, "terjual": 0},
            "4": {"nama": "Aqua Botol 600ml", "stok": 45, "harga": 3500, "terjual": 0}
        }
        # [Properti/Atribut Class] Tempat menampung daftar riwayat transaksi kasir
        self.laporan_keuangan = []

    def ambil_semua_produk(self):
        """Metode untuk mengambil seluruh data barang yang ada di toko"""
        return self.data_barang

    def ambil_semua_laporan(self):
        """Metode untuk mengambil semua catatan riwayat transaksi kasir"""
        return self.laporan_keuangan

    def proses_pembelian(self, id_barang, jumlah_beli, uang_bayar):
        """Metode inti OOP untuk memproses validasi dan transaksi belanja kasir"""
        # Cek apakah ID barang yang dikirim kasir ada di dalam menu toko
        if id_barang not in self.data_barang:
            return {"status": "gagal", "pesan": "Barang tidak ditemukan!"}, 404
            
        # Mengambil data produk berdasarkan ID yang dipilih
        barang = self.data_barang[id_barang]
        # Menghitung total harga: jumlah barang dikali harga satuan
        total_harga = jumlah_beli * barang['harga']
        
        # Validasi 1: Cek apakah stok fisik di toko mencukupi
        if barang['stok'] < jumlah_beli:
            return {"status": "gagal", "pesan": "Stok tidak mencukupi!"}, 400
            
        # Validasi 2: Cek apakah uang yang diserahkan pembeli kurang
        if uang_bayar < total_harga:
            return {"status": "gagal", "pesan": "Uang yang dibayar kurang!"}, 400
            
        # KONDISI SUKSES: Kurangi stok barang dan tambah angka terjual di memori
        barang['stok'] -= jumlah_beli
        barang['terjual'] += jumlah_beli
        # Menghitung uang kembalian untuk pembeli
        kembalian = uang_bayar - total_harga
        
        # Menyusun data nota belanja baru dan memasukkannya ke dalam list riwayat laporan
        self.laporan_keuangan.append({
            "waktu": datetime.now().strftime("%H:%M:%S"), # Mencatat jam transaksi otomatis
            "nama_barang": barang['nama'],
            "jumlah": jumlah_beli,
            "total_harga": total_harga,
            "uang_bayar": uang_bayar,
            "kembalian": kembalian,
            "penjual": "Kasir Utama"
        })
        # Mengembalikan status sukses ke route server
        return {"status": "sukses", "pesan": "Transaksi berhasil!"}, 200

    def tambah_stok_gudang(self, id_barang, jumlah_tambah):
        """Metode untuk menambah stok barang lama (Menu Restock Gudang)"""
        if id_barang in self.data_barang:
            # Tambah jumlah stok lama dengan jumlah pasokan baru yang masuk
            self.data_barang[id_barang]['stok'] += jumlah_tambah
            return {"status": "sukses", "pesan": "Stok berhasil ditambahkan!"}, 200
        return {"status": "gagal", "pesan": "Barang tidak ditemukan!"}, 404

    def daftarkan_produk_baru(self, nama, stok, harga):
        """Metode untuk mendaftarkan varian produk baru ke dalam daftar toko"""
        # Membuat ID baru otomatis dalam bentuk string berdasarkan jumlah barang saat ini + 1
        baru_id = str(len(self.data_barang) + 1)
        # Memasukkan data produk baru ke objek dictionary toko
        self.data_barang[baru_id] = {"nama": nama, "stok": stok, "harga": harga, "terjual": 0}
        return {"status": "sukses", "pesan": "Produk baru berhasil didaftarkan!"}, 200


# INSTANSIASI: Membuat satu objek nyata bernama 'layanan_toko' dari cetakan Class di atas
layanan_toko = LayananToko()


# =================================================================
# BAGIAN 3: ROUTE / CONTROLLER (Gerbang API Flask untuk HTML)
# =================================================================

@app.route('/')
def index():
    """Route Utama: Mengarahkan browser agar langsung merender visual index.html"""
    return render_template('index.html')

@app.route('/api/dashboard-data', methods=['GET'])
def get_data():
    """Route API GET: Mengirimkan semua data terbaru untuk dipasang di dashboard & Chart.js"""
    # Memanggil data dari objek OOP layanan_toko
    data_barang = layanan_toko.ambil_semua_produk()
    laporan_keuangan_list = layanan_toko.ambil_semua_laporan()

    # Menghitung otomatis total omzet pendapatan dari seluruh transaksi yang sukses
    total_riwayat = sum(log['total_harga'] for log in laporan_keuangan_list)
    
    # Menyusun rangkuman data performa kasir
    performa_penjual = {
        "nama": "Kasir Utama",
        "total_transaksi": len(laporan_keuangan_list),
        "omzet_sekarang": total_riwayat
    }
    
    # Menyiapkan susunan bulan dan data angka untuk dikirim ke diagram grafik Chart.js
    labels_bulan = ["Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    dataset_pendapatan = [total_riwayat, 0, 0, 0, 0, 0, 0] # Grafik pendapatan bulan ini
    dataset_profit = [int(total_riwayat * 0.6), 0, 0, 0, 0, 0, 0] # Grafik taksiran profit bersih (60%)

    # Mengirimkan seluruh paket data di atas dalam format JSON ke JavaScript di HTML
    return jsonify({
        "barang": data_barang,
        "total_pendapatan": total_riwayat,
        "laporan": laporan_keuangan_list,
        "penjual": performa_penjual,
        "chart_bulanan": {
            "labels": labels_bulan,
            "pendapatan": dataset_pendapatan,
            "profit": dataset_profit
        }
    })

@app.route('/api/beli', methods=['POST'])
def proses_beli():
    """Route API POST: Menerima data transaksi kasir dari tombol 'Bayar' di HTML"""
    # Menangkap data JSON yang dikirimkan oleh browser
    id_barang = request.json.get('id_barang')
    jumlah_beli = int(request.json.get('jumlah'))
    uang_bayar = int(request.json.get('uang_bayar'))
    
    # Melemparkan data kiriman tersebut ke metode logika transaksi di objek OOP kita
    hasil, status_code = layanan_toko.proses_pembelian(id_barang, jumlah_beli, uang_bayar)
    # Mengembalikan respon hasil transaksi berupa status sukses/gagal ke browser
    return jsonify(hasil), status_code

@app.route('/api/tambah-stok', methods=['POST'])
def tambah_stok():
    """Route API POST: Menerima input penambahan stok dari halaman Gudang HTML"""
    id_barang = request.json.get('id_barang')
    jumlah_tambah = int(request.json.get('jumlah'))
    
    # Memproses penambahan stok lewat metode objek OOP layanan_toko
    hasil, status_code = layanan_toko.tambah_stok_gudang(id_barang, jumlah_tambah)
    return jsonify(hasil), status_code

@app.route('/api/barang-baru', methods=['POST'])
def barang_baru():
    """Route API POST: Menerima input pendaftaran produk baru dari form HTML"""
    nama = request.json.get('nama')
    stok = int(request.json.get('stok'))
    harga = int(request.json.get('harga'))
    
    # Memproses pembuatan produk baru lewat metode objek OOP layanan_toko
    hasil, status_code = layanan_toko.daftarkan_produk_baru(nama, stok, harga)
    return jsonify(hasil), status_code


# =================================================================
# BAGIAN 4: MENYALAKAN SERVER (Running Application)
# =================================================================
if __name__ == '__main__':
    # Menjalankan server lokal Flask dengan fitur 'debug=True' agar auto-reload saat disave
    app.run(debug=True)