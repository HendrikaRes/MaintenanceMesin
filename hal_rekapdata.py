from flet import *
import pymysql
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import datetime

# ================= KONEKSI DATABASE =================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_perawatan_mesin_uas" # ✅ Database Maintenance
    )

# ================= HALAMAN REKAP DATA & LAPORAN =================
def rekap_data_view(page: Page):

    # ---------- 1. Fungsi Ambil Data (JOIN Tabel) ----------
    def load_data(keyword_mesin=""):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Filter berdasarkan Nama Mesin
        param = f"%{keyword_mesin}%"
        
        # Query JOIN: Mengambil Nama Mesin dari tabel 'mesin' dan data sensor dari 'log_performa'
        cursor.execute("""
            SELECT 
                mesin.nama_mesin, 
                log_performa.suhu_mesin, 
                log_performa.rpm_motor, 
                log_performa.voltase,
                log_performa.status_kondisi, 
                log_performa.rekomendasi, 
                log_performa.durasi_maintenance, 
                log_performa.tanggal_entri
            FROM log_performa
            JOIN mesin ON log_performa.id_mesin = mesin.id_mesin
            WHERE mesin.nama_mesin LIKE %s
            ORDER BY log_performa.tanggal_entri DESC
        """, (param,))

        rows = cursor.fetchall()
        conn.close()
        return rows

    # ---------- 2. Fungsi Menampilkan Data ke Layar ----------
    def refresh_table():
        table.rows.clear()
        data = load_data(txt_search.value)

        for row in data:
            # Logika Warna Indikator Status
            status_color = Colors.GREEN
            if "Warning" in row[4]: status_color = Colors.ORANGE
            elif "Critical" in row[4] or "Overheat" in row[4]: status_color = Colors.RED

            # Format Tanggal agar rapi
            tgl_str = row[7].strftime("%d-%m %H:%M") if row[7] else "-"

            table.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(row[0], weight="bold", size=12)), # Nama Mesin
                        DataCell(Text(str(row[1]))),           # Suhu
                        DataCell(Text(str(row[2]))),           # RPM
                        DataCell(Text(str(row[3]))),           # Volt
                        DataCell(Container(
                            content=Text(row[4], size=11, color="white"),
                            bgcolor=status_color,
                            padding=5, border_radius=5
                        )),
                        DataCell(Text(row[5], size=12)),       # Rekomendasi
                        DataCell(Text(f"{row[6]} Jam" if row[6] else "-")),
                        DataCell(Text(tgl_str, size=11)),      # Tanggal
                    ]
                )
            )
        page.update()

    # ================= 3. Fungsi Cetak PDF =================
    def cetak_laporan(e):
        data = load_data(txt_search.value)

        if not data:
            page.snack_bar = SnackBar(Text("⚠️ Data kosong, tidak bisa dicetak"), bgcolor=Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        file_name = "laporan_maintenance_mesin.pdf"

        # Gunakan Landscape (Kertas Miring) karena kolomnya banyak
        pdf = SimpleDocTemplate(
            file_name,
            pagesize=landscape(A4),
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )

        styles = getSampleStyleSheet()
        elements = []

        # --- Kop Laporan ---
        elements.append(Paragraph("<para align='center'><font size=16><b>LAPORAN MAINTENANCE & PERFORMA MESIN</b></font></para>", styles["Normal"]))
        elements.append(Paragraph("<para align='center'><font size=12>Departemen Teknik & Pemeliharaan Aset</font></para>", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # --- Info Filter ---
        tanggal_cetak = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        filter_info = txt_search.value if txt_search.value else "Semua Mesin"

        info_text = f"<b>Tanggal Cetak:</b> {tanggal_cetak} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Filter Mesin:</b> {filter_info}"
        elements.append(Paragraph(info_text, styles["Normal"]))
        elements.append(Spacer(1, 10))

        # --- Header Tabel PDF ---
        table_data = [[
            "Nama Mesin", "Suhu", "RPM", "Volt",
            "Status Kondisi", "Rekomendasi / Tindakan", "Durasi", "Waktu Cek"
        ]]

        # --- Isi Tabel PDF ---
        for row in data:
            tgl = row[7].strftime("%d-%m-%Y %H:%M") if row[7] else "-"
            # Potong teks rekomendasi jika terlalu panjang agar tabel tidak hancur
            rekomendasi_cut = row[5][:25] + "..." if len(row[5]) > 25 else row[5]
            
            table_data.append([
                row[0],     # Nama
                f"{row[1]}°C", # Suhu
                row[2],     # RPM
                f"{row[3]}V", # Volt
                row[4],     # Status
                rekomendasi_cut, 
                f"{row[6]} Jam",
                tgl
            ])

        # Atur Lebar Kolom PDF (Total harus pas A4 Landscape)
        col_widths = [130, 50, 50, 50, 100, 180, 60, 110]
        
        table_pdf = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Style Tabel PDF (Warna Industrial)
        table_pdf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#37474f")), # Header Abu Gelap
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table_pdf)

        # --- Footer Halaman ---
        def footer(canvas, doc):
            canvas.setFont("Helvetica", 8)
            canvas.drawString(30, 20, f"Sistem Informasi Manajemen Aset | Halaman {doc.page}")

        pdf.build(elements, onFirstPage=footer, onLaterPages=footer)

        # Buka file otomatis (Khusus Windows)
        try:
            os.startfile(file_name)
            page.snack_bar = SnackBar(Text("✅ Laporan PDF berhasil dibuat!"), bgcolor=Colors.GREEN)
        except:
             page.snack_bar = SnackBar(Text("✅ PDF tersimpan, tapi gagal dibuka otomatis."), bgcolor=Colors.ORANGE)
        
        page.snack_bar.open = True
        page.update()

    # ================= 4. Komponen UI Flet =================
    txt_search = TextField(
        label="Filter Nama Mesin",
        width=300,
        prefix_icon=Icons.SEARCH,
        border_radius=10,
        on_submit=lambda e: refresh_table()
    )

    btn_refresh = IconButton(
        icon=Icons.REFRESH,
        tooltip="Refresh Data",
        icon_color=Colors.BLUE,
        on_click=lambda e: refresh_table()
    )

    btn_cetak = ElevatedButton(
        "Export Laporan PDF",
        icon=Icons.PICTURE_AS_PDF,
        style=ButtonStyle(
            bgcolor=Colors.RED_700,
            color=Colors.WHITE,
            shape=RoundedRectangleBorder(radius=10),
            padding=15
        ),
        on_click=cetak_laporan
    )

    table = DataTable(
        border=border.all(1, Colors.GREY_300),
        vertical_lines=border.BorderSide(1, Colors.GREY_200),
        heading_row_color=Colors.BLUE_GREY_50,
        expand=True,
        columns=[
            DataColumn(Text("Nama Mesin", weight="bold")),
            DataColumn(Text("Suhu", weight="bold")),
            DataColumn(Text("RPM", weight="bold")),
            DataColumn(Text("Volt", weight="bold")),
            DataColumn(Text("Status Kondisi", weight="bold")),
            DataColumn(Text("Rekomendasi", weight="bold")),
            DataColumn(Text("Durasi", weight="bold")),
            DataColumn(Text("Waktu", weight="bold")),
        ],
        rows=[]
    )

    # Load Data Awal saat halaman dibuka
    refresh_table()

    # ================= 5. Layout Halaman =================
    return Container(
        expand=True,
        content=Column(
            spacing=15,
            controls=[
                # --- Header Card ---
                Container(
                    padding=20,
                    bgcolor=Colors.WHITE,
                    border_radius=12,
                    shadow=BoxShadow(blur_radius=10, color=Colors.BLACK12),
                    content=Row(
                        alignment="spaceBetween",
                        controls=[
                            Row(
                                spacing=10, 
                                controls=[
                                    Icon(Icons.SUMMARIZE, size=32, color=Colors.BLUE_GREY_700),
                                    Column(
                                        spacing=0,
                                        controls=[
                                            Text("Rekap Data Maintenance", size=20, weight="bold", color=Colors.BLUE_GREY_900),
                                            Text("Monitoring riwayat performa seluruh aset mesin", size=12, color=Colors.GREY_500),
                                        ]
                                    )
                                ]
                            ),
                            btn_cetak,
                        ],
                    ),
                ),

                # --- Filter & Table Card ---
                Container(
                    expand=True,
                    padding=20,
                    bgcolor=Colors.WHITE,
                    border_radius=12,
                    shadow=BoxShadow(blur_radius=10, color=Colors.BLACK12),
                    content=Column(
                        controls=[
                            Row(
                                controls=[
                                    txt_search,
                                    btn_refresh
                                ]
                            ),
                            Divider(),
                            # Container Table dengan Scroll
                            Column(
                                expand=True,
                                scroll=ScrollMode.AUTO,
                                controls=[table]
                            )
                        ]
                    ),
                ),
            ],
        ),
    )