from flet import *
import pymysql

# ================= KONEKSI DATABASE =================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_perawatan_mesin_uas"
    )

# ================= KOMPONEN KARTU KECIL =================
def sensor_card(value, label, icon, color):
    return Container(
        width=150,
        height=90,
        bgcolor="white",
        border_radius=12,
        padding=10,
        shadow=BoxShadow(blur_radius=10, color="black12"),
        content=Column(
            controls=[
                Icon(icon, color=color, size=24),
                Text(str(value), size=18, weight="bold", color=Colors.BLUE_GREY_800),
                Text(label, size=11, color="black54"),
            ],
            horizontal_alignment="center",
            spacing=5
        ),
    )

# ================= KOMPONEN STATISTIK UTAMA =================
def stat_card(title, value, color, icon_data):
    return Container(
        expand=True,
        padding=20,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Column(
                    spacing=5,
                    controls=[
                        Text(title, weight="bold", color=Colors.GREY_600),
                        Text(str(value), size=28, weight="bold", color=color),
                    ]
                ),
                Container(
                    padding=10,
                    # 🔥 PERBAIKAN DI SINI (Gunakan colors.with_opacity)
                    bgcolor=Colors.with_opacity(0.1, color),
                    border_radius=10,
                    content=Icon(icon_data, color=color, size=30)
                )
            ]
        ),
    )

# ================= VIEW DASHBOARD UTAMA =================
def dashboard_view():
    
    # --- VARIABEL PENAMPUNG DATA ---
    total_mesin = 0
    total_warning = 0
    total_critical = 0
    list_log_terakhir = []
    
    # --- AMBIL DATA DARI DATABASE ---
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Hitung Total Mesin
        cursor.execute("SELECT COUNT(*) FROM mesin")
        total_mesin = cursor.fetchone()[0]

        # 2. Hitung Status Warning
        cursor.execute("SELECT COUNT(*) FROM log_performa WHERE status_kondisi LIKE '%Warning%'")
        total_warning = cursor.fetchone()[0]

        # 3. Hitung Status Critical
        cursor.execute("SELECT COUNT(*) FROM log_performa WHERE status_kondisi LIKE '%Critical%' OR status_kondisi LIKE '%Overheat%'")
        total_critical = cursor.fetchone()[0]

        # 4. Ambil 5 Log Terakhir
        cursor.execute("""
            SELECT m.nama_mesin, l.suhu_mesin, l.voltase, l.status_kondisi, l.tanggal_entri 
            FROM log_performa l
            JOIN mesin m ON l.id_mesin = m.id_mesin
            ORDER BY l.tanggal_entri DESC LIMIT 5
        """)
        list_log_terakhir = cursor.fetchall()

        conn.close()

    except Exception as e:
        print(f"❌ Error Database Dashboard: {e}")
        return Text(f"Error memuat dashboard: {e}", color=Colors.RED)

    # --- MEMBUAT BARIS TABEL ---
    rows_tabel = []
    for log in list_log_terakhir:
        
        # Warna Badge Status
        bg_status = Colors.GREEN
        if "Warning" in log[3]: bg_status = Colors.ORANGE
        elif "Critical" in log[3] or "Overheat" in log[3]: bg_status = Colors.RED

        rows_tabel.append(
            DataRow(cells=[
                DataCell(Text(log[4].strftime("%H:%M") if log[4] else "-")), # Jam
                DataCell(Text(log[0], weight="bold")), # Nama Mesin
                DataCell(Text(f"{log[1]}°C")),         # Suhu
                DataCell(Text(f"{log[2]}V")),          # Volt
                DataCell(Container(
                    content=Text(log[3], color="white", size=10),
                    bgcolor=bg_status, padding=5, border_radius=5
                )),
            ])
        )

    # ================= SUSUNAN LAYOUT =================
    return Container(
        padding=10,
        expand=True,
        content=Column(
            scroll=ScrollMode.AUTO,
            spacing=20,
            controls=[
                Text("Dashboard Monitoring", size=24, weight="bold", color=Colors.BLUE_GREY_900),
                
                # --- SECTION 1: KARTU ATAS ---
                Row(
                    spacing=20,
                    controls=[
                        stat_card("Total Aset Mesin", total_mesin, Colors.BLUE, Icons.DOMAIN),
                        stat_card("Status Warning", total_warning, Colors.ORANGE, Icons.WARNING),
                        stat_card("Status Critical", total_critical, Colors.RED, Icons.DANGEROUS),
                    ],
                ),

                # --- SECTION 2: GRAFIK & TABEL ---
                Row(
                    spacing=20,
                    vertical_alignment=CrossAxisAlignment.START,
                    controls=[
                        # Grafik Pie (Demo)
                        Container(
                            expand=1,
                            padding=20,
                            bgcolor="white",
                            border_radius=12,
                            shadow=BoxShadow(blur_radius=12, color="black12"),
                            content=Column(
                                horizontal_alignment="center",
                                spacing=10,
                                controls=[
                                    Text("Komposisi Kondisi", weight="bold"),
                                    PieChart(
                                        sections=[
                                            PieChartSection(value=60, color=Colors.GREEN, radius=40),
                                            PieChartSection(value=30, color=Colors.ORANGE, radius=40),
                                            PieChartSection(value=10, color=Colors.RED, radius=40),
                                        ],
                                        height=150,
                                        sections_space=2,
                                    ),
                                    Row(
                                        alignment="center",
                                        controls=[
                                            Icon(Icons.CIRCLE, size=10, color=Colors.GREEN), Text(" Aman ", size=10),
                                            Icon(Icons.CIRCLE, size=10, color=Colors.ORANGE), Text(" Warning ", size=10),
                                            Icon(Icons.CIRCLE, size=10, color=Colors.RED), Text(" Rusak ", size=10),
                                        ]
                                    )
                                ]
                            )
                        ),

                        # Tabel Log Terakhir
                        Container(
                            expand=2,
                            padding=20,
                            bgcolor="white",
                            border_radius=12,
                            shadow=BoxShadow(blur_radius=12, color="black12"),
                            content=Column(
                                spacing=10,
                                controls=[
                                    Text("5 Aktivitas Sensor Terakhir", weight="bold", size=16),
                                    DataTable(
                                        columns=[
                                            DataColumn(Text("Jam")),
                                            DataColumn(Text("Mesin")),
                                            DataColumn(Text("Suhu")),
                                            DataColumn(Text("Volt")),
                                            DataColumn(Text("Status")),
                                        ],
                                        rows=rows_tabel
                                    )
                                ]
                            )
                        )
                    ]
                ),

                # --- SECTION 3: SENSOR RATA-RATA ---
                Container(
                    padding=20,
                    bgcolor="white",
                    border_radius=12,
                    shadow=BoxShadow(blur_radius=12, color="black12"),
                    content=Column(
                        controls=[
                            Text("Indikator Sensor Umum", weight="bold"),
                            Divider(),
                            Row(
                                scroll=ScrollMode.AUTO,
                                spacing=15,
                                controls=[
                                    sensor_card("60°C", "Avg Suhu", Icons.THERMOSTAT, Colors.RED),
                                    sensor_card("1200", "Avg RPM", Icons.SPEED, Colors.BLUE),
                                    sensor_card("220V", "Avg Volt", Icons.BOLT, Colors.AMBER),
                                    sensor_card("Stabil", "Vibrasi", Icons.VIBRATION, Colors.GREEN),
                                ]
                            )
                        ]
                    )
                )
            ],
        ),
    )