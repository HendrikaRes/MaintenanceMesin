import pymysql
from flet import *

# =========================================================
# 🔹 KONEKSI DATABASE
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_perawatan_mesin_uas" # ✅ Pastikan Database Benar
    )

# =========================================================
# 🔹 HALAMAN KELOLA LAPORAN OPERATOR (KOMPLAIN)
# =========================================================
def kelola_laporan_operator_view(page: Page):

    selected_id = {"id": None}

    # ================= STATE =================
    current_page = {"value": 1}
    limit_per_page = 5
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    
    # 1. Dropdown Pilih Mesin
    def buat_dropdown_mesin():
        try:
            buka_koneksi = koneksi_database()
            perintahSQL = buka_koneksi.cursor()
            perintahSQL.execute("SELECT id_mesin, kode_aset, nama_mesin FROM mesin ORDER BY nama_mesin ASC")
            hasil = perintahSQL.fetchall()
            perintahSQL.close(); buka_koneksi.close()

            return Dropdown(
                label="Mesin Bermasalah",
                hint_text="Pilih Mesin...",
                prefix_icon=Icons.PRECISION_MANUFACTURING,
                width=300,
                enable_filter=True,
                options=[dropdown.Option(key=str(row[0]), text=f"{row[2]} ({row[1]})") for row in hasil],
                border_color=Colors.BLUE_GREY_400
            )
        except: return Dropdown(label="Error DB", width=300)

    # 2. Dropdown Tingkat Urgensi
    def buat_dropdown_urgensi():
        return Dropdown(
            label="Tingkat Urgensi",
            options=[
                dropdown.Option("Rendah (Low)"),
                dropdown.Option("Sedang (Medium)"),
                dropdown.Option("Tinggi (High)"),
                dropdown.Option("Kritis (Critical)"),
            ],
            prefix_icon=Icons.WARNING,
            width=300,
            border_color=Colors.BLUE_GREY_400
        )

    input_id_mesin = buat_dropdown_mesin()
    input_keluhan = TextField(label="Deskripsi Kerusakan / Keluhan", multiline=True, min_lines=3, prefix_icon=Icons.NOTE_ALT, width=300, border_color=Colors.BLUE_GREY_400)
    input_urgensi = buat_dropdown_urgensi()
    notif = Text("")

    # ================= CRUD LOGIC =================
    input_cari = TextField(hint_text="Cari Keluhan...", prefix_icon=Icons.SEARCH, width=250, border_radius=20, on_change=lambda e: proses_cari(e))

    def bersihkan_form():
        nonlocal input_id_mesin, input_urgensi
        input_keluhan.value = ""
        selected_id["id"] = None
        
        # Reset Dropdowns
        input_id_mesin = buat_dropdown_mesin()
        form_content.controls[1] = input_id_mesin
        input_urgensi = buat_dropdown_urgensi()
        form_content.controls[3] = input_urgensi
        
        page.update()

    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data()
        page.update()

    def simpan_laporan(e):
        if not input_id_mesin.value or not input_keluhan.value or not input_urgensi.value:
            notif.value = "⚠️ Semua data wajib diisi!"
            notif.color = Colors.RED
            page.update()
            return

        try:
            db = koneksi_database()
            cur = db.cursor()

            if selected_id["id"]:  # UPDATE
                cur.execute("""
                    UPDATE laporan_operator 
                    SET id_mesin=%s, keluhan_kerusakan=%s, tingkat_urgensi=%s 
                    WHERE id_laporan=%s
                """, (input_id_mesin.value, input_keluhan.value, input_urgensi.value, selected_id["id"]))
                notif.value = "✅ Laporan Diperbarui"
            else:  # INSERT
                cur.execute("""
                    INSERT INTO laporan_operator (id_mesin, keluhan_kerusakan, tingkat_urgensi, tanggal_entri) 
                    VALUES (%s, %s, %s, NOW())
                """, (input_id_mesin.value, input_keluhan.value, input_urgensi.value))
                notif.value = "✅ Laporan Terkirim"

            db.commit(); cur.close(); db.close()
            notif.color = Colors.GREEN
            bersihkan_form()
            muat_data()
            page.update()
        except Exception as err:
            notif.value = f"Error: {err}"; notif.color = Colors.RED; page.update()

    def hapus_laporan(id):
        def confirm(e):
            try:
                db = koneksi_database(); cur = db.cursor()
                cur.execute("DELETE FROM laporan_operator WHERE id_laporan=%s", (id,))
                db.commit(); db.close()
                page.close(dlg); muat_data(); page.update()
            except: pass
        dlg = AlertDialog(title=Text("Hapus Laporan?"), actions=[TextButton("Ya", on_click=confirm), TextButton("Batal", on_click=lambda e: page.close(dlg))])
        page.open(dlg)

    def edit_laporan(row):
        selected_id["id"] = row[0]
        input_id_mesin.value = str(row[5]) # ID Mesin hidden
        input_keluhan.value = row[2]
        input_urgensi.value = row[3]
        notif.value = "✏️ Mode Edit"; notif.color = Colors.ORANGE
        page.update()

    # ================= TABEL =================
    tabel = DataTable(
        border=border.all(1, Colors.GREY_300),
        heading_row_color=Colors.BLUE_GREY_50,
        columns=[
            DataColumn(Text("No")),
            DataColumn(Text("Mesin")),
            DataColumn(Text("Keluhan")),
            DataColumn(Text("Urgensi")),
            DataColumn(Text("Waktu")),
            DataColumn(Text("Aksi")),
        ],
        rows=[]
    )
    
    info_page = Text()

    def muat_data():
        tabel.rows.clear()
        try:
            db = koneksi_database(); cur = db.cursor()
            kw = f"%{keyword_cari['value']}%"
            
            # Hitung Total
            cur.execute("""
                SELECT COUNT(*) FROM laporan_operator l JOIN mesin m ON l.id_mesin = m.id_mesin 
                WHERE m.nama_mesin LIKE %s OR l.keluhan_kerusakan LIKE %s
            """, (kw, kw))
            total_data["value"] = cur.fetchone()[0]
            
            offset = (current_page["value"] - 1) * limit_per_page
            
            # Ambil Data
            cur.execute("""
                SELECT l.id_laporan, m.nama_mesin, l.keluhan_kerusakan, l.tingkat_urgensi, l.tanggal_entri, l.id_mesin
                FROM laporan_operator l JOIN mesin m ON l.id_mesin = m.id_mesin 
                WHERE m.nama_mesin LIKE %s OR l.keluhan_kerusakan LIKE %s
                ORDER BY l.tanggal_entri DESC LIMIT %s OFFSET %s
            """, (kw, kw, limit_per_page, offset))
            
            for i, row in enumerate(cur.fetchall()):
                no = offset + i + 1
                bg_color = Colors.GREEN
                if "Sedang" in row[3]: bg_color = Colors.ORANGE
                elif "Tinggi" in row[3]: bg_color = Colors.RED_400
                elif "Kritis" in row[3]: bg_color = Colors.RED_900

                tabel.rows.append(DataRow(cells=[
                    DataCell(Text(no)),
                    DataCell(Text(row[1], weight="bold")),
                    DataCell(Text(row[2])),
                    DataCell(Container(content=Text(row[3], color="white", size=11), bgcolor=bg_color, padding=5, border_radius=5)),
                    DataCell(Text(str(row[4]))),
                    DataCell(Row([
                        IconButton(Icons.EDIT, icon_color="blue", on_click=lambda e, r=row: edit_laporan(r)),
                        IconButton(Icons.DELETE, icon_color="red", on_click=lambda e, id=row[0]: hapus_laporan(id))
                    ]))
                ]))
            db.close()
            total_hal = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
            info_page.value = f"Hal {current_page['value']} / {total_hal}"
        except Exception as e: print(e)

    def paging(mode):
        total_hal = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        if mode == "prev" and current_page["value"] > 1: current_page["value"] -= 1
        elif mode == "next" and current_page["value"] < total_hal: current_page["value"] += 1
        muat_data(); page.update()

    muat_data()

    # ================= LAYOUT UTAMA =================
    form_content = Column(spacing=15, controls=[
        Container(padding=10, bgcolor=Colors.BLUE_GREY_50, border_radius=10, content=Row([Icon(Icons.REPORT, color=Colors.RED_800), Text("Form Laporan Kerusakan", weight="bold")])),
        input_id_mesin,
        input_keluhan,
        input_urgensi,
        Divider(),
        Row([
            ElevatedButton("Kirim Laporan", icon=Icons.SEND, bgcolor=Colors.RED_800, color=Colors.WHITE, on_click=simpan_laporan),
            ElevatedButton("Reset", icon=Icons.REFRESH, on_click=lambda e: bersihkan_form())
        ]),
        notif
    ])

    return Container(
        expand=True, padding=20,
        content=Row(
            vertical_alignment=CrossAxisAlignment.START,
            controls=[
                # Kiri: Form
                Container(width=350, padding=20, bgcolor="white", border_radius=15, shadow=BoxShadow(blur_radius=10, color="black12"), content=Column(scroll=ScrollMode.AUTO, controls=[form_content])),
                # Kanan: Tabel
                Container(expand=True, padding=20, bgcolor="white", border_radius=15, shadow=BoxShadow(blur_radius=10, color="black12"), 
                    content=Column(expand=True, controls=[
                        Row([Text("Daftar Laporan Masuk", size=20, weight="bold", color=Colors.BLUE_GREY_900), input_cari], alignment="spaceBetween"),
                        Divider(),
                        Container(expand=True, content=Column(scroll=ScrollMode.AUTO, controls=[Row(scroll=ScrollMode.ALWAYS, controls=[tabel])])),
                        Divider(),
                        Row([ElevatedButton("<", on_click=lambda e: paging("prev")), info_page, ElevatedButton(">", on_click=lambda e: paging("next"))], alignment="center")
                    ])
                )
            ]
        )
    )