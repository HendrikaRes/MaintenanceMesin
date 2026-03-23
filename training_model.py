import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Buat Data Latih (Dummy Data Logika Teknik)
# Pola: 
# - Suhu > 80 atau Voltase < 200 -> Warning/Critical
# - RPM > 3000 -> Overheat
# - Normal range -> Normal

data = {
    'suhu':    [60, 65, 55, 70, 85, 90, 95, 100, 60, 50, 82, 40, 110, 75, 78],
    'rpm':     [1200, 1300, 1100, 1400, 1600, 2000, 0, 0, 3500, 1200, 1500, 1200, 1400, 2800, 2900],
    'voltase': [220, 221, 219, 220, 210, 200, 0, 0, 220, 220, 190, 220, 220, 180, 215],
    'status':  [
        'Normal', 'Normal', 'Normal', 'Normal', 
        'Warning (Perlu Cek)', 'Overheat', 'Critical (Rusak)', 'Critical (Rusak)', 
        'Overheat', 'Normal', 'Warning (Perlu Cek)', 'Normal', 'Critical (Rusak)', 'Warning (Perlu Cek)', 'Warning (Perlu Cek)'
    ]
}

df = pd.DataFrame(data)

# 2. Pisahkan Fitur (X) dan Target (y)
X = df[['suhu', 'rpm', 'voltase']]
y = df['status']

# 3. Pilih Model: Random Forest (Cocok untuk klasifikasi data sensor)
model = RandomForestClassifier(n_estimators=100, random_state=42)

# 4. Latih Model
print("Sedang melatih model AI...")
model.fit(X, y)

# 5. Simpan Model ke File
joblib.dump(model, 'model_maintenance.pkl')
print("✅ Model berhasil disimpan sebagai 'model_maintenance.pkl'")
print("Coba prediksi [Suhu=95, RPM=0, Volt=0]:", model.predict([[95, 0, 0]]))