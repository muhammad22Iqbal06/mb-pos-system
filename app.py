from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

data_barang = {
    "1": {"nama": "Kopi Susu", "stok": 50, "harga": 15000, "terjual": 0},
    "2": {"nama": "Roti Bakar", "stok": 30, "harga": 12000, "terjual": 0},
    "3": {"nama": "Kentang Goreng", "stok": 40, "harga": 10000, "terjual": 0}
}

laporan_keuangan = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard-data', methods=['GET'])
def get_data():
    total_riwayat = sum(log['total_harga'] for log in laporan_keuangan)
    
    performa_penjual = {
        "nama": "Kasir Utama",
        "total_transaksi": len(laporan_keuangan),
        "omzet_sekarang": total_riwayat
    }
    
    labels_bulan = ["Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    dataset_pendapatan = [total_riwayat, 0, 0, 0, 0, 0, 0]
    dataset_profit = [int(total_riwayat * 0.6), 0, 0, 0, 0, 0, 0]

    return jsonify({
        "barang": data_barang,
        "total_pendapatan": total_riwayat,
        "laporan": laporan_keuangan,
        "penjual": performa_penjual,
        "chart_bulanan": {
            "labels": labels_bulan,
            "pendapatan": dataset_pendapatan,
            "profit": dataset_profit
        }
    })

@app.route('/api/beli', methods=['POST'])
def proses_beli():
    id_barang = request.json.get('id_barang')
    jumlah_beli = int(request.json.get('jumlah'))
    uang_bayar = int(request.json.get('uang_bayar'))
    
    if id_barang in data_barang:
        barang = data_barang[id_barang]
        total_harga = jumlah_beli * barang['harga']
        
        if barang['stok'] < jumlah_beli:
            return jsonify({"status": "gagal", "pesan": "Stok tidak mencukupi!"}), 400
            
        if uang_bayar < total_harga:
            return jsonify({"status": "gagal", "pesan": "Uang yang dibayar kurang!"}), 400
            
        barang['stok'] -= jumlah_beli
        barang['terjual'] += jumlah_beli
        
        kembalian = uang_bayar - total_harga
        
        laporan_keuangan.append({
            "waktu": datetime.now().strftime("%H:%M:%S"),
            "nama_barang": barang['nama'],
            "jumlah": jumlah_beli,
            "total_harga": total_harga,
            "uang_bayar": uang_bayar,
            "kembalian": kembalian,
            "penjual": "Kasir Utama"
        })
        
        return jsonify({"status": "sukses", "pesan": "Transaksi berhasil!"})
        
    return jsonify({"status": "gagal", "pesan": "Barang tidak ditemukan!"}), 404

@app.route('/api/tambah-stok', methods=['POST'])
def tambah_stok():
    id_barang = request.json.get('id_barang')
    jumlah_tambah = int(request.json.get('jumlah'))
    
    if id_barang in data_barang:
        data_barang[id_barang]['stok'] += jumlah_tambah
        return jsonify({"status": "sukses", "pesan": "Stok berhasil ditambahkan!"})
    return jsonify({"status": "gagal", "pesan": "Barang tidak ditemukan!"}), 404

@app.route('/api/barang-baru', methods=['POST'])
def barang_baru():
    nama = request.json.get('nama')
    stok = int(request.json.get('stok'))
    harga = int(request.json.get('harga'))
    
    baru_id = str(len(data_barang) + 1)
    data_barang[baru_id] = {"nama": nama, "stok": stok, "harga": harga, "terjual": 0}
    return jsonify({"status": "sukses", "pesan": "Produk baru berhasil didaftarkan!"})

if __name__ == '__main__':
    app.run(debug=True)