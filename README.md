# 🚗 Sistem Informasi Fleet Maintenance & Predictive Monitoring

Sistem berbasis web yang dirancang untuk memonitor kondisi mesin kendaraan secara real-time dan melakukan prediksi potensi kerusakan berdasarkan parameter operasional seperti suhu mesin dan RPM.

Aplikasi ini membantu perusahaan dalam melakukan **preventive maintenance** sehingga dapat mengurangi risiko kerusakan kendaraan secara mendadak.

---

## 🚀 Fitur Utama

- ✅ Manajemen data kendaraan
- ✅ Monitoring suhu mesin (temperature)
- ✅ Monitoring RPM mesin
- ✅ Prediksi kerusakan mesin berdasarkan parameter
- ✅ Notifikasi kondisi abnormal
- ✅ Riwayat maintenance kendaraan
- ✅ Dashboard monitoring

---

## 🧠 Sistem Prediksi

Sistem menggunakan pendekatan berbasis rule / model sederhana untuk menentukan kondisi mesin:

### Parameter:
- Suhu mesin (°C)
- RPM (Revolutions Per Minute)

### Contoh Analisis:

| Suhu | RPM | Status |
|------|-----|--------|
| Normal | Normal | Aman |
| Tinggi | Normal | Overheat |
| Normal | Tinggi | Overload |
| Tinggi | Tinggi | Risiko Kerusakan Tinggi |

---

## ⚠️ Contoh Prediksi Kerusakan

- 🔥 Overheat → kemungkinan kerusakan radiator / pendingin
- ⚙️ RPM tinggi → potensi keausan mesin
- 🚨 Kombinasi ekstrem → risiko kerusakan mesin serius

---

## 🛠️ Teknologi yang Digunakan

### Backend
- Laravel 11

### Frontend
- Bootstrap
- jQuery

### Database
- PostgreSQL

### Pendukung
- AJAX (real-time update)
- DataTables

---

## 🏗️ Arsitektur Sistem

- Frontend: Interface monitoring dashboard
- Backend: Pengolahan data & logika prediksi
- Database: Penyimpanan data kendaraan & sensor
- Model: Rule-based decision system

---

## ⚙️ Cara Instalasi

1. Clone repository:
```bash
git clone https://github.com/username/fleet-maintenance.git
