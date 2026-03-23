import pymysql
from flet import *
from datetime import date

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
# 🔹 HALAMAN KELOLA MESIN
# =========================================================
def kelola_mesin_view(page: Page):

    selected_id = {"id": None}  # State untuk mode edit

    # ================= PAGINATION & SEARCH STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    def buat_dropdown_tipe():
        return Dropdown(
            label="Tipe Mesin",
            options=[
                dropdown.Option("Hidrolik"),
                dropdown.Option("Listrik"),
            ],
            prefix_icon=Icons.CATEGORY,
            width=360,
            border_color=Colors.BLUE_GREY_400
        )

    # Definisi Input Field
    inputan_kode_aset = TextField(label="Kode Aset", prefix_icon=Icons.QR_CODE, width=360, border_color=Colors.BLUE_GREY_400)
    inputan_nama_mesin = TextField(label="Nama Mesin", prefix_icon=Icons.PRECISION_MANUFACTURING, width=360, border_color=Colors.BLUE_GREY_400)
    inputan_tipe_mesin = buat_dropdown_tipe()
    
    inputan_tgl_beli = TextField(label="Tanggal Beli", prefix_icon=Icons.CALENDAR_TODAY, read_only=True, width=250, border_color=Colors.BLUE_GREY_400)
    
    # Logic Date Picker
    def pilih_tanggal(e):
        if e.control.value:
            inputan_tgl_beli.value = e.control.value.strftime("%Y-%m-%d")
            inputan_tgl_beli.update()

    date_picker = DatePicker(
        first_date=date(2000, 1, 1),
        last_date=date.today(),
        on_change=pilih_tanggal
    )

    page.overlay.append(date_picker)

    opsi_tgl_beli = ElevatedButton(
        "Pilih",
        icon=Icons.CALENDAR_MONTH,
        width=80,
        style=ButtonStyle(bgcolor=Colors.BLUE_GREY_700, color=Colors.WHITE),
        on_click=lambda e: page.open(date_picker)
    )

    inputan_lokasi = TextField(
        label="Lokasi Pabrik",
        multiline=True,
        min_lines=3,
        prefix_icon=Icons.FACTORY,
        width=360,
        border_color=Colors.BLUE_GREY_400
    )

    notif_kelola = Text("")

    # ================= INPUT SEARCH =================
    input_cari = TextField(
        hint_text="Cari Kode atau Nama Mesin...",
        prefix_icon=Icons.SEARCH,
        on_change=lambda e: proses_cari(e),
        width=350,
        border_radius=20
    )

    # ================= RESET FORM =================
    def bersihkan_form():
        nonlocal inputan_tipe_mesin

        inputan_kode_aset.value = ""
        inputan_nama_mesin.value = ""
        inputan_tgl_beli.value = None
        inputan_lokasi.value = ""
        selected_id["id"] = None

        # 🔥 RESET DROPDOWN (REBUILD AGAR BERSIH)
        dropdown_baru = buat_dropdown_tipe()
        idx_tipe = form_column.controls.index(inputan_tipe_mesin)
        form_column.controls[idx_tipe] = dropdown_baru
        inputan_tipe_mesin = dropdown_baru

        page.update()

    # ================= PROSES SEARCH =================
    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_mesin()
        page.update()

    # ================= SIMPAN / UPDATE =================
    def simpan_mesin(e):
        if not inputan_kode_aset.value or not inputan_nama_mesin.value or not inputan_tipe_mesin.value:
            notif_kelola.value = "❌ Data wajib diisi semua!"
            notif_kelola.color = Colors.RED
            page.update()
            return
        
        try:
            buka_koneksi = koneksi_database()
            perintahSQL = buka_koneksi.cursor()

            if selected_id["id"]:  # MODE UPDATE
                perintahSQL.execute(
                    """ UPDATE mesin SET kode_aset=%s, nama_mesin=%s, tipe_mesin=%s, 
                        tgl_beli=%s, lokasi_pabrik=%s WHERE id_mesin=%s """,
                    (
                        inputan_kode_aset.value,
                        inputan_nama_mesin.value,
                        inputan_tipe_mesin.value,
                        inputan_tgl_beli.value,
                        inputan_lokasi.value,
                        selected_id["id"],
                    ),
                )
                notif_kelola.value = "✅ Data Mesin berhasil diperbarui"
            else:  # MODE INSERT
                perintahSQL.execute(
                    """ INSERT INTO mesin (kode_aset, nama_mesin, tipe_mesin, 
                        tgl_beli, lokasi_pabrik) 
                        VALUES (%s, %s, %s, %s, %s) """,
                    (
                        inputan_kode_aset.value,
                        inputan_nama_mesin.value,
                        inputan_tipe_mesin.value,
                        inputan_tgl_beli.value,
                        inputan_lokasi.value,
                    ),
                )
                notif_kelola.value = "✅ Mesin baru berhasil ditambahkan"

            buka_koneksi.commit()
            perintahSQL.close()
            buka_koneksi.close()

            notif_kelola.color = Colors.GREEN_700
            bersihkan_form()
            muat_data_mesin()
            page.update()
        
        except Exception as err:
            notif_kelola.value = f"❌ Error: {err}"
            notif_kelola.color = Colors.RED
            page.update()

    # ================= KONFIRMASI HAPUS =================
    def konfirmasi_hapus(id_mesin):
        dialog = AlertDialog(
            modal=True,
            title=Text("Konfirmasi Hapus"),
            content=Text("Yakin ingin menghapus data mesin ini? Data log sensor terkait mungkin juga akan hilang."),
            actions=[
                TextButton("Batal", on_click=lambda e: page.close(dialog)),
                ElevatedButton(
                    "Hapus",
                    bgcolor=Colors.RED,
                    color=Colors.WHITE,
                    on_click=lambda e: hapus_mesin(dialog, id_mesin),
                ),
            ],
        )
        page.open(dialog)

    def hapus_mesin(dialog, id_mesin):
        try:
            buka_koneksi = koneksi_database()
            perintahSQL = buka_koneksi.cursor()
            perintahSQL.execute("DELETE FROM mesin WHERE id_mesin=%s", (id_mesin,))
            buka_koneksi.commit()
            perintahSQL.close()
            buka_koneksi.close()

            page.close(dialog)
            bersihkan_form()
            muat_data_mesin()
            page.update()
        except Exception as err:
            print(err)

    # ================= EDIT MESIN (POPULATE FORM) =================
    def edit_mesin(row):
        selected_id["id"] = row[0]
        inputan_kode_aset.value = row[1]
        inputan_nama_mesin.value = row[2]
        inputan_tipe_mesin.value = row[3]
        inputan_tgl_beli.value = str(row[4])
        inputan_lokasi.value = row[5]
        
        notif_kelola.value = "✏️ Mode Edit Aktif"
        notif_kelola.color = Colors.ORANGE
        page.update()

    # ================= TABEL DATA =================
    tabel_data_mesin = DataTable(
        border=border.all(1, Colors.GREY_200),
        border_radius=10,
        vertical_lines=border.BorderSide(1, Colors.GREY_200),
        heading_row_color=Colors.BLUE_GREY_50,
        columns=[
            DataColumn(Text("No.", weight="bold")),
            DataColumn(Text("Kode Aset", weight="bold")),
            DataColumn(Text("Nama Mesin", weight="bold")),
            DataColumn(Text("Tipe", weight="bold")),
            DataColumn(Text("Tgl Beli", weight="bold")),
            DataColumn(Text("Lokasi", weight="bold")),
            DataColumn(Text("Aksi", weight="bold")),
        ],
        rows=[],
    )

    info_halaman = Text()

    def muat_data_mesin():
        tabel_data_mesin.rows.clear()
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        keyword = f"%{keyword_cari['value']}%"

        # Hitung total data (Untuk Pagination)
        perintahSQL.execute(
            """ SELECT COUNT(*) FROM mesin 
                WHERE kode_aset LIKE %s OR nama_mesin LIKE %s """,
            (keyword, keyword)
        )
        total_data["value"] = perintahSQL.fetchone()[0]

        offset = (current_page["value"] - 1) * limit_per_page

        # Ambil Data
        perintahSQL.execute(
            """ SELECT 
                    id_mesin, kode_aset, nama_mesin, tipe_mesin, tgl_beli, lokasi_pabrik 
                FROM mesin
                WHERE kode_aset LIKE %s OR nama_mesin LIKE %s
                ORDER BY id_mesin DESC
                LIMIT %s OFFSET %s """,
            (keyword, keyword, limit_per_page, offset)
        )

        for index, row in enumerate(perintahSQL.fetchall()):
            no_urut = offset + index + 1
            tabel_data_mesin.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(no_urut)),
                        DataCell(Text(row[1], weight="bold", color=Colors.BLUE_GREY_800)),
                        DataCell(Text(row[2])),
                        DataCell(Container(
                            padding=5, 
                            border_radius=5,
                            bgcolor=Colors.BLUE_50 if row[3] == 'Listrik' else Colors.ORANGE_50,
                            content=Text(row[3], color=Colors.BLUE if row[3] == 'Listrik' else Colors.ORANGE_800)
                        )),
                        DataCell(Text(str(row[4]) if row[4] else "-")),
                        DataCell(Text(row[5])),
                        DataCell(
                            Row(
                                spacing=0,
                                controls=[
                                    IconButton(
                                        icon=Icons.EDIT,
                                        icon_color=Colors.BLUE,
                                        tooltip="Edit Mesin",
                                        on_click=lambda e, data=row: edit_mesin(data),
                                    ),
                                    IconButton(
                                        icon=Icons.DELETE,
                                        icon_color=Colors.RED,
                                        tooltip="Hapus Mesin",
                                        on_click=lambda e, id=row[0]: konfirmasi_hapus(id),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )
            
        total_halaman = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        info_halaman.value = f"Halaman {current_page['value']} dari {total_halaman}"

        perintahSQL.close()
        buka_koneksi.close()

    # ================= PAGING BUTTON =================
    def prev_page(e):
        if current_page["value"] > 1:
            current_page["value"] -= 1
            muat_data_mesin()
            page.update()

    def next_page(e):
        total_halaman = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        if current_page["value"] < total_halaman:
            current_page["value"] += 1
            muat_data_mesin()
            page.update()

    # Load data pertama kali
    muat_data_mesin()

    # ================= LAYOUT UTAMA =================
    form_column = Column(
        spacing=15,
        controls=[
            Container(
                padding=10, 
                bgcolor=Colors.BLUE_GREY_50, 
                border_radius=10,
                content=Row([Icon(Icons.ADD_BOX), Text("Input Data Aset", weight="bold")])
            ),
            inputan_kode_aset,
            inputan_nama_mesin,
            inputan_tipe_mesin,
            Row([inputan_tgl_beli, opsi_tgl_beli]),
            inputan_lokasi,
            Divider(),
            Row([
                ElevatedButton("Simpan", icon=Icons.SAVE, on_click=simpan_mesin, color=Colors.WHITE, bgcolor=Colors.BLUE_GREY_800, height=45),
                ElevatedButton("Reset", icon=Icons.REFRESH, on_click=lambda e: bersihkan_form(), color=Colors.BLACK, bgcolor=Colors.WHITE, height=45),
            ]),
            notif_kelola,
        ],
    )

    return Container(
        expand=True,
        padding=20,
        content=Row(
            spacing=20,
            vertical_alignment=CrossAxisAlignment.START,
            controls=[
                # Kiri: FORM
                Container(
                    width=400,
                    padding=25,
                    bgcolor="white",
                    border_radius=15,
                    shadow=BoxShadow(blur_radius=15, color="black12"),
                    content=form_column
                ),

                # Kanan: TABEL + SEARCH + PAGING
                Container(
                    expand=True,
                    padding=25,
                    bgcolor="white",
                    border_radius=15,
                    shadow=BoxShadow(blur_radius=15, color="black12"),
                    content=Column(
                        expand=True, # Mengisi tinggi yang tersedia
                        controls=[
                            Row(
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    Text("Daftar Aset Mesin", size=20, weight="bold", color=Colors.BLUE_GREY_900),
                                    input_cari,
                                ]
                            ),
                            Divider(),
                            
                            # 🔥 BAGIAN PERBAIKAN SCROLL HORIZONTAL
                            Container(
                                expand=True,
                                content=Column(
                                    scroll=ScrollMode.AUTO, # Scroll Vertikal
                                    controls=[
                                        Row(
                                            scroll=ScrollMode.ALWAYS, # Scroll Horizontal (Agar bisa geser kiri kanan)
                                            controls=[tabel_data_mesin]
                                        )
                                    ]
                                ),
                            ),
                            
                            Divider(),
                            Row(
                                alignment="spaceBetween",
                                controls=[
                                    ElevatedButton("◀ Sebelumnya", on_click=prev_page, style=ButtonStyle(color=Colors.BLUE_GREY_800, bgcolor=Colors.WHITE)),
                                    info_halaman,
                                    ElevatedButton("Berikutnya ▶", on_click=next_page, style=ButtonStyle(color=Colors.BLUE_GREY_800, bgcolor=Colors.WHITE)),
                                ],
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )