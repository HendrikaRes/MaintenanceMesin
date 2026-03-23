import pymysql
from flet import *
import joblib
import os

# =========================================================
# 🔹 KONEKSI DATABASE
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_perawatan_mesin_uas"
    )

# =========================================================
# 🔹 HALAMAN KELOLA LOG PERFORMA & SENSOR
# =========================================================
def kelola_log_performa_view(page: Page):

    selected_id = {"id": None}
    
    # 🧠 Load Model AI (Cek apakah file ada)
    model_ai = None
    if os.path.exists("model_maintenance.pkl"):
        model_ai = joblib.load("model_maintenance.pkl")

    # ================= PAGINATION & SEARCH STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    
    # 1. Dropdown Pilih Mesin
    def buat_dropdown_mesin():
        try:
            buka_koneksi = koneksi_database()
            perintahSQL = buka_koneksi.cursor()
            perintahSQL.execute("""
                SELECT id_mesin, kode_aset, nama_mesin, tipe_mesin
                FROM mesin ORDER BY nama_mesin ASC
            """)
            hasil = perintahSQL.fetchall()
            perintahSQL.close()
            buka_koneksi.close()

            return Dropdown(
                label="Pilih Mesin",
                hint_text="Cari Mesin...",
                prefix_icon=Icons.PRECISION_MANUFACTURING,
                width=360,
                enable_filter=True,
                enable_search=True,
                options=[dropdown.Option(key=str(row[0]), text=f"{row[1]} - {row[2]} ({row[3]})") for row in hasil],
                border_color=Colors.BLUE_GREY_400
            )
        except:
            return Dropdown(label="Error DB", width=360)
    
    # 2. Dropdown Status
    def buat_dropdown_status():
        return Dropdown(
            label="Status Kondisi",
            options=[
                dropdown.Option("Normal"),
                dropdown.Option("Warning (Perlu Cek)"),
                dropdown.Option("Critical (Rusak)"),
                dropdown.Option("Overheat"),
            ],
            prefix_icon=Icons.MONITOR_HEART,
            width=360,
            border_color=Colors.BLUE_GREY_400
        )

    # Definisi Input
    input_id_mesin = buat_dropdown_mesin()
    
    # Input Sensor (Lebar dikecilkan agar muat sebaris)
    input_suhu = TextField(label="Suhu (°C)", prefix_icon=Icons.THERMOSTAT, width=110, keyboard_type=KeyboardType.NUMBER, border_color=Colors.BLUE_GREY_400)
    input_rpm = TextField(label="RPM", prefix_icon=Icons.SPEED, width=110, keyboard_type=KeyboardType.NUMBER, border_color=Colors.BLUE_GREY_400)
    input_voltase = TextField(label="Volt (V)", prefix_icon=Icons.BOLT, width=110, keyboard_type=KeyboardType.NUMBER, border_color=Colors.BLUE_GREY_400)
    
    input_status = buat_dropdown_status()
    input_rekomendasi = TextField(label="Rekomendasi / Tindakan", prefix_icon=Icons.TIPS_AND_UPDATES, width=360, multiline=True, border_color=Colors.BLUE_GREY_400)
    input_durasi = TextField(label="Durasi (Jam)", prefix_icon=Icons.TIMER, width=360, keyboard_type=KeyboardType.NUMBER, border_color=Colors.BLUE_GREY_400)

    notif_log = Text("")

    # ================= 🤖 FITUR AI PREDICTION =================
    def prediksi_ai(e):
        if not model_ai:
            notif_log.value = "⚠️ Model AI belum dilatih (jalankan training_model.py dulu)"
            notif_log.color = Colors.ORANGE
            page.update()
            return

        if not input_suhu.value or not input_rpm.value or not input_voltase.value:
            notif_log.value = "⚠️ Isi Suhu, RPM, dan Voltase dulu!"
            notif_log.color = Colors.RED
            page.update()
            return

        try:
            # Ambil data input
            val_suhu = float(input_suhu.value)
            val_rpm = float(input_rpm.value)
            val_volt = float(input_voltase.value)

            # 1. Prediksi STATUS (Machine Learning)
            data_baru = [[val_suhu, val_rpm, val_volt]]
            hasil_prediksi_status = model_ai.predict(data_baru)[0]
            
            # Update Kolom Status Otomatis
            input_status.value = hasil_prediksi_status
            
            # 2. Generate REKOMENDASI (Logic Cerdas)
            rekomendasi_list = []

            # Cek Suhu
            if val_suhu > 90: rekomendasi_list.append("🔴 SUHU KRITIS: Matikan mesin, cek coolant.")
            elif val_suhu > 80: rekomendasi_list.append("🟠 SUHU TINGGI: Cek sirkulasi udara.")

            # Cek RPM
            if val_rpm > 3000: rekomendasi_list.append("🔴 OVERSPEED: Turunkan beban kerja.")
            elif val_rpm < 500 and val_rpm > 0: rekomendasi_list.append("🟠 UNDERSPEED: Cek suplai daya.")
            elif val_rpm == 0: rekomendasi_list.append("⚫ MOTOR MATI: Cek kabel power.")

            # Cek Voltase
            if val_volt < 200: rekomendasi_list.append("⚡ UNDERVOLTAGE: Cek stabiliser/genset.")
            elif val_volt > 240: rekomendasi_list.append("⚡ OVERVOLTAGE: Bahaya konsleting.")

            # Gabungkan Hasil
            if "Normal" in hasil_prediksi_status and not rekomendasi_list:
                input_rekomendasi.value = "✅ Kondisi Prima. Lakukan maintenance rutin."
            elif not rekomendasi_list:
                input_rekomendasi.value = "⚠️ Lakukan inspeksi visual menyeluruh."
            else:
                input_rekomendasi.value = " + ".join(rekomendasi_list)

            notif_log.value = f"🤖 Analisis Selesai: {hasil_prediksi_status}"
            notif_log.color = Colors.BLUE
            page.update()

        except Exception as err:
            notif_log.value = f"Error AI: {err}"
            notif_log.color = Colors.RED
            page.update()

    # ================= CRUD FUNGSI LAINNYA =================
    input_cari = TextField(hint_text="Cari...", prefix_icon=Icons.SEARCH, on_change=lambda e: proses_cari(e), width=350, border_radius=20)

    def bersihkan_form():
        nonlocal input_id_mesin, input_status
        input_suhu.value = ""
        input_rpm.value = ""
        input_voltase.value = ""
        input_rekomendasi.value = ""
        input_status.value = None
        input_durasi.value = ""
        selected_id["id"] = None
        
        # Reset Dropdowns
        dropdown_mesin_baru = buat_dropdown_mesin()
        idx_mesin = form_content.controls[1].content.controls.index(input_id_mesin) if isinstance(form_content.controls[1], Container) else form_content.controls.index(input_id_mesin)
        
        # Trick: Rebuild Form karena Flet dropdown kadang nyangkut
        input_id_mesin.value = None
        input_status.value = None
        page.update()

    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_log()
        page.update()

    def simpan_log(e):
        if not input_id_mesin.value or not input_status.value:
            notif_log.value = "❌ Mesin dan Status wajib dipilih!"
            notif_log.color = Colors.RED
            page.update()
            return
        try:
            db = koneksi_database()
            cur = db.cursor()
            if selected_id["id"]:
                cur.execute("UPDATE log_performa SET suhu_mesin=%s, rpm_motor=%s, voltase=%s, status_kondisi=%s, rekomendasi=%s, durasi_maintenance=%s WHERE id_log=%s",
                            (input_suhu.value, input_rpm.value, input_voltase.value, input_status.value, input_rekomendasi.value, input_durasi.value, selected_id["id"]))
                notif_log.value = "✅ Data diupdate"
            else:
                cur.execute("INSERT INTO log_performa (suhu_mesin, rpm_motor, voltase, status_kondisi, rekomendasi, durasi_maintenance, tanggal_entri, id_mesin) VALUES (%s,%s,%s,%s,%s,%s,NOW(),%s)",
                            (input_suhu.value, input_rpm.value, input_voltase.value, input_status.value, input_rekomendasi.value, input_durasi.value, input_id_mesin.value))
                notif_log.value = "✅ Data disimpan"
            db.commit()
            cur.close()
            db.close()
            notif_log.color = Colors.GREEN_700
            muat_data_log()
            page.update()
        except Exception as err:
            notif_log.value = f"Error: {err}"
            notif_log.color = Colors.RED
            page.update()

    def konfirmasi_hapus(id):
        def hapus(e):
            try:
                db = koneksi_database()
                cur = db.cursor()
                cur.execute("DELETE FROM log_performa WHERE id_log=%s", (id,))
                db.commit()
                db.close()
                page.close(dlg)
                muat_data_log()
                page.update()
            except: pass
        dlg = AlertDialog(title=Text("Hapus?"), actions=[TextButton("Ya", on_click=hapus), TextButton("Batal", on_click=lambda e: page.close(dlg))])
        page.open(dlg)

    def edit_log(row):
        selected_id["id"] = row[0]
        input_id_mesin.value = str(row[1])
        input_suhu.value = str(row[2])
        input_rpm.value = str(row[3])
        input_voltase.value = str(row[4])
        input_status.value = row[5]
        input_rekomendasi.value = row[6]
        input_durasi.value = str(row[7])
        notif_log.value = "✏️ Mode Edit"
        notif_log.color = Colors.ORANGE
        page.update()

    # ================= TABEL DATA =================
    tabel_log = DataTable(
        border=border.all(1, Colors.GREY_200),
        vertical_lines=border.BorderSide(1, Colors.GREY_200),
        heading_row_color=Colors.BLUE_GREY_50,
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("Mesin")),
            DataColumn(Text("Suhu")),
            DataColumn(Text("RPM")),
            DataColumn(Text("Volt")),
            DataColumn(Text("Status")),
            DataColumn(Text("Rekomendasi")),
            DataColumn(Text("Durasi")),
            DataColumn(Text("Waktu")),
            DataColumn(Text("Aksi")),
        ],
        rows=[]
    )

    info_halaman = Text()

    def muat_data_log():
        tabel_log.rows.clear()
        try:
            db = koneksi_database()
            cur = db.cursor()
            kw = f"%{keyword_cari['value']}%"
            # JOIN Query
            cur.execute("""
                SELECT l.id_log, l.id_mesin, l.suhu_mesin, l.rpm_motor, l.voltase, 
                       l.status_kondisi, l.rekomendasi, l.durasi_maintenance, l.tanggal_entri, 
                       m.nama_mesin, m.kode_aset 
                FROM log_performa l JOIN mesin m ON l.id_mesin = m.id_mesin 
                WHERE l.status_kondisi LIKE %s OR m.nama_mesin LIKE %s 
                ORDER BY l.tanggal_entri DESC LIMIT 10
            """, (kw, kw))
            
            for index, row in enumerate(cur.fetchall()):
                no_urut = index + 1
                bg_color = Colors.GREEN
                if "Warning" in str(row[5]): bg_color = Colors.ORANGE
                elif "Critical" in str(row[5]) or "Overheat" in str(row[5]): bg_color = Colors.RED

                tabel_log.rows.append(DataRow(cells=[
                    DataCell(Text(no_urut)),
                    DataCell(Column([Text(row[9], weight="bold"), Text(row[10], size=10, color="grey")])),
                    DataCell(Text(row[2])), DataCell(Text(row[3])), DataCell(Text(row[4])),
                    DataCell(Container(content=Text(row[5], color="white", size=11), bgcolor=bg_color, padding=5, border_radius=5)),
                    DataCell(Text(row[6])), DataCell(Text(f"{row[7]} Jam")), DataCell(Text(str(row[8]))),
                    DataCell(Row([
                        IconButton(Icons.EDIT, icon_color="blue", on_click=lambda e, r=row: edit_log(r)),
                        IconButton(Icons.DELETE, icon_color="red", on_click=lambda e, i=row[0]: konfirmasi_hapus(i))
                    ]))
                ]))
            db.close()
        except Exception as e: print(e)

    muat_data_log()

    # ================= LAYOUT UTAMA =================
    # Kita simpan layout form dalam variabel agar bisa diakses
    form_content = Column(
        spacing=15,
        controls=[
            Container(padding=10, bgcolor=Colors.BLUE_GREY_50, border_radius=10, content=Row([Icon(Icons.SENSORS), Text("Input Log Sensor", weight="bold")])),
            input_id_mesin,
            # Baris Input Sensor (Suhu, RPM, Volt)
            Row([input_suhu, input_rpm, input_voltase], alignment="spaceBetween"),
            
            # 🔥 TOMBOL AI DISINI 🔥
            ElevatedButton(
                "Prediksi Status & Rekomendasi (AI)", 
                icon=Icons.SMART_TOY, 
                bgcolor=Colors.PURPLE_700, 
                color=Colors.WHITE, 
                style=ButtonStyle(shape=RoundedRectangleBorder(radius=8)),
                height=45,
                width=360,
                on_click=prediksi_ai
            ),

            Divider(),
            Container(padding=10, bgcolor=Colors.BLUE_GREY_50, border_radius=10, content=Row([Icon(Icons.ANALYTICS), Text("Hasil Analisis", weight="bold")])),
            input_status,
            input_rekomendasi,
            input_durasi,
            Row([
                ElevatedButton("Simpan Log", icon=Icons.SAVE, bgcolor=Colors.BLUE_GREY_800, color=Colors.WHITE, on_click=simpan_log, height=45),
                ElevatedButton("Reset", icon=Icons.REFRESH, bgcolor=Colors.WHITE, color=Colors.BLACK, on_click=lambda e: bersihkan_form(), height=45),
            ]),
            notif_log,
        ]
    )

    return Container(
        expand=True, padding=20,
        content=Row(
            spacing=20,
            vertical_alignment=CrossAxisAlignment.START,
            controls=[
                # Kiri: Form Input
                Container(
                    width=400, padding=25, bgcolor="white", border_radius=15, shadow=BoxShadow(blur_radius=15, color="black12"),
                    content=Column(scroll=ScrollMode.AUTO, controls=[form_content])
                ),
                # Kanan: Tabel Data
                Container(
                    expand=True, padding=25, bgcolor="white", border_radius=15, shadow=BoxShadow(blur_radius=15, color="black12"),
                    content=Column(expand=True, controls=[
                        Row([Text("Riwayat Log Performa", size=20, weight="bold", color=Colors.BLUE_GREY_900), input_cari], alignment="spaceBetween"),
                        Divider(),
                        # 🔥 FIX SCROLL HORIZONTAL
                        Container(expand=True, content=Column(scroll=ScrollMode.AUTO, controls=[
                            Row(scroll=ScrollMode.ALWAYS, controls=[tabel_log])
                        ])),
                    ])
                )
            ]
        )
    )