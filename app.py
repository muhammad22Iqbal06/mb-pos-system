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
        # [Properti/Atribut Class] DATA BARANG WARUNG
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

    def proses_pembelian_multi(self, daftar_belanja, uang_bayar):
        """Metode inti OOP untuk memproses transaksi yang berisi banyak item sekaligus"""
        if not daftar_belanja:
            return {"status": "gagal", "pesan": "Keranjang belanja kosong!"}, 400

        total_harga_transaksi = 0
        barang_diupdate = []

        # Tahap 1: Validasi awal untuk semua item di dalam keranjang
        for item in daftar_belanja:
            id_barang = item.get('id_barang')
            jumlah_beli = int(item.get('jumlah', 0))

            if id_barang not in self.data_barang:
                return {"status": "gagal", "pesan": f"Barang dengan ID {id_barang} tidak ditemukan!"}, 404

            barang = self.data_barang[id_barang]
            if barang['stok'] < jumlah_beli:
                return {"status": "gagal", "pesan": f"Stok untuk {barang['nama']} tidak mencukupi!"}, 400

            total_harga_transaksi += (jumlah_beli * barang['harga'])
            # Simpan data sementara untuk eksekusi jika validasi lolos
            barang_diupdate.append((barang, jumlah_beli))

        # Validasi Uang Pembayaran
        if uang_bayar < total_harga_transaksi:
            return {"status": "gagal", "pesan": "Uang yang dibayar kurang!"}, 400

        # Tahap 2: Kondisi Sukses (Kurangi stok & update counter terjual)
        nama_barang_tercatat = []
        for barang, jumlah in barang_diupdate:
            barang['stok'] -= jumlah
            barang['terjual'] += jumlah
            nama_barang_tercatat.append(f"{barang['nama']} ({jumlah}x)")

        kembalian = uang_bayar - total_harga_transaksi
        waktu_sekarang = datetime.now().strftime("%H:%M:%S")

        # Masukkan ke dalam database riwayat laporan keuangan
        # Menggabungkan nama item menjadi satu string (misal: "Indomie Goreng (3x), Kopi Kapal Api (2x)")
        self.laporan_keuangan.append({
            "waktu": waktu_sekarang,
            "nama_barang": ", ".join(nama_barang_tercatat),
            "jumlah": sum(item[1] for item in barang_diupdate), # Total seluruh pcs barang
            "total_harga": total_harga_transaksi,
            "uang_bayar": uang_bayar,
            "kembalian": kembalian,
            "penjual": "Kasir Utama"
        })

        return {"status": "sukses", "pesan": "Transaksi berhasil!", "waktu": waktu_sekarang, "kembalian": kembalian}, 200

    def tambah_stok_gudang(self, id_barang, jumlah_tambah):
        """Metode untuk menambah stok barang lama (Menu Restock Gudang)"""
        if id_barang in self.data_barang:
            self.data_barang[id_barang]['stok'] += jumlah_tambah
            return {"status": "sukses", "pesan": "Stok berhasil ditambahkan!"}, 200
        return {"status": "gagal", "pesan": "Barang tidak ditemukan!"}, 404

    def daftarkan_produk_baru(self, nama, stok, harga):
        """Metode untuk mendaftarkan varian produk baru ke dalam daftar toko"""
        baru_id = str(len(self.data_barang) + 1)
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
    data_barang = layanan_toko.ambil_semua_produk()
    laporan_keuangan_list = layanan_toko.ambil_semua_laporan()

    total_riwayat = sum(log['total_harga'] for log in laporan_keuangan_list)
    
    performa_penjual = {
        "nama": "Kasir Utama",
        "total_transaksi": len(laporan_keuangan_list),
        "omzet_sekarang": total_riwayat
    }
    
    labels_bulan = ["Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    dataset_pendapatan = [total_riwayat, 0, 0, 0, 0, 0, 0] 
    dataset_profit = [int(total_riwayat * 0.6), 0, 0, 0, 0, 0, 0] 

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
    """Route API POST Baru: Menerima list object belanjaan multi-item langsung dari HTML"""
    # Menerima daftar item (array) dan jumlah uang fisik dari frontend
    daftar_belanja = request.json.get('daftar_belanja', [])
    uang_bayar = int(request.json.get('uang_bayar', 0))
    
    # Melemparkan data ke method pengolah multi-item
    hasil, status_code = layanan_toko.proses_pembelian_multi(daftar_belanja, uang_bayar)
    return jsonify(hasil), status_code

@app.route('/api/tambah-stok', methods=['POST'])
def tambah_stok():
    """Route API POST: Menerima input penambahan stok dari halaman Gudang HTML"""
    id_barang = request.json.get('id_barang')
    jumlah_tambah = int(request.json.get('jumlah'))
    
    hasil, status_code = layanan_toko.tambah_stok_gudang(id_barang, jumlah_tambah)
    return jsonify(hasil), status_code

@app.route('/api/barang-baru', methods=['POST'])
def barang_baru():
    """Route API POST: Menerima input pendaftaran produk baru dari form HTML"""
    nama = request.json.get('nama')
    stok = int(request.json.get('stok'))
    harga = int(request.json.get('harga'))
    
    hasil, status_code = layanan_toko.daftarkan_produk_baru(nama, stok, harga)
    return jsonify(hasil), status_code


# =================================================================
# BAGIAN 4: MENYALAKAN SERVER (Running Application)
# =================================================================
if __name__ == '__main__':
    app.run(debug=True)