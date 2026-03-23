# 🚗 Aplikasi Fleet Maintenance & Monitoring Mesin

Aplikasi berbasis Python menggunakan framework **Flet** untuk memonitor kondisi mesin kendaraan dan memprediksi potensi kerusakan berdasarkan parameter suhu dan RPM.

Sistem ini dirancang untuk membantu proses **preventive maintenance** agar kerusakan kendaraan dapat dideteksi lebih awal.

---

## 🚀 Fitur Utama

- ✅ Monitoring suhu mesin
- ✅ Monitoring RPM mesin
- ✅ Prediksi kondisi mesin secara otomatis
- ✅ Halaman Kelola Meisn
- ✅ Halaman Kelola Operator
- ✅ Halaman Kelola Log Peforma
- ✅ Halaman Cetak Rekap Data
- ✅ Dashboard monitoring sederhana
- ✅ Riwayat kondisi mesin

---

## 🧠 Sistem Prediksi

Sistem menggunakan pendekatan **rule-based** untuk menentukan kondisi mesin berdasarkan:

- Suhu mesin (°C)
- RPM mesin

### 📊 Klasifikasi Kondisi

| Suhu | RPM | Status |
|------|-----|--------|
| Normal | Normal | Aman |
| Tinggi | Normal | Overheat |
| Normal | Tinggi | Overload |
| Tinggi | Tinggi | Risiko Kerusakan Tinggi |

---

## ⚠️ Prediksi Kerusakan

- 🔥 Overheat → kemungkinan masalah pada radiator / sistem pendingin
- ⚙️ RPM tinggi → potensi keausan mesin
- 🚨 Kombinasi ekstrem → risiko kerusakan mesin serius

---

## 🛠️ Teknologi yang Digunakan

- Python
- Flet (UI Framework)
- Database Mysql
- (Opsional jika ada:)
  - Pandas
  - NumPy
    

---

## 🏗️ Arsitektur Sistem

- UI: Flet (Frontend + Backend dalam satu aplikasi)
- Logic: Python (Rule-based prediction)
- Data: Input manual / simulasi sensor

---

## ⚙️ Cara Menjalankan Aplikasi

1. Clone repository:
```bash
git clone https://github.com/username/fleet-maintenance-flet.git
