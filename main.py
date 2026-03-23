# ================= IMPORT MODULE =================
from flet import *
import traceback

# Import Halaman (Project Maintenance Mesin)
from hal_dashboard import dashboard_view
from hal_login import login_view
from hal_profil import profil_view
from hal_tentang import tentang_view
from hal_kelolamesin import kelola_mesin_view
from hal_kelolalogperforma import kelola_log_performa_view
from hal_kelolalaporanoperator import kelola_laporan_operator_view
from hal_rekapdata import rekap_data_view 

# ================= FUNGSI UTAMA APLIKASI =================
def main(page: Page):
    # ---------- Konfigurasi dasar window aplikasi ----------
    page.title = "Sistem Maintenance Mesin"
    page.bgcolor = "#e8ecf3"
    page.window.width = 1280
    page.window.height = 800
    page.window.maximized = True

    # ---------- Session login ----------
    session_user = {
        "username": None,
        "hak_akses": None
    }

    # ================= HALAMAN LOGIN =================
    def tampil_hallogin():
        page.clean()
        page.add(login_view(page, tampil_halpengguna))
        page.update()

    # ================= PROSES LOGOUT =================
    def proses_logout():
        session_user["username"] = None
        session_user["hak_akses"] = None
        tampil_hallogin()

    # ================= HALAMAN UTAMA SETELAH LOGIN =================
    def tampil_halpengguna(username, hak_akses):
        session_user["username"] = username
        session_user["hak_akses"] = hak_akses

        page.clean()
        content = Column(expand=True)

        # 🔹 DEFINISI MENU BERDASARKAN HAK AKSES 🔹
        
        # 1. Menu Dasar (Semua orang punya)
        list_menu = [
            NavigationRailDestination(icon=Icons.DASHBOARD, label="Dashboard"),
            NavigationRailDestination(icon=Icons.CONSTRUCTION, label="Data Mesin"),
            NavigationRailDestination(icon=Icons.TIMELINE, label="Log Performa"),
            NavigationRailDestination(icon=Icons.REPORT_PROBLEM, label="Laporan Operator"),
        ]

        # 2. Menu Khusus (Hanya Admin & Manager)
        # Teknisi TIDAK AKAN dapat menu ini
        if hak_akses in ["admin", "manager"]:
            list_menu.append(
                NavigationRailDestination(icon=Icons.SUMMARIZE, label="Rekap Data")
            )

        # 3. Menu Tambahan (Profil, Tentang, Logout - Semua punya)
        list_menu.extend([
            NavigationRailDestination(icon=Icons.PERSON, label="Profil User"),
            NavigationRailDestination(icon=Icons.INFO, label="Tentang App"),
            NavigationRailDestination(icon=Icons.LOGOUT, label="Logout"),
        ])

        # ================= NAVIGATION RAIL (MENU SAMPING) =================
        rail = NavigationRail(
            selected_index=0,
            label_type=NavigationRailLabelType.ALL,
            extended=True,
            expand=True, # Agar menu penuh ke bawah
            destinations=list_menu,
        )

        # ================= LOGIKA PINDAH HALAMAN (PAKAI LABEL) =================
        # Kita pakai Label (nama menu) karena urutan index bisa berubah beda user
        def change(e):
            # Ambil label menu yang sedang dipilih
            if rail.selected_index is not None and rail.selected_index < len(list_menu):
                selected_label = list_menu[rail.selected_index].label
            else:
                selected_label = "Dashboard" # Default jika error

            content.controls.clear()

            try:
                # --- DASHBOARD ---
                if selected_label == "Dashboard":
                    content.controls.append(
                        Column(
                            spacing=10,
                            expand=True,
                            controls=[
                                Text(
                                    f"👋 Selamat datang, {session_user['username']} "
                                    f"({session_user['hak_akses']})",
                                    size=18,
                                    weight="bold",
                                ),
                                dashboard_view(),
                            ],
                        )
                    )

                # --- DATA MESIN ---
                elif selected_label == "Data Mesin":
                    content.controls.append(
                        Column(
                            spacing=10,
                            expand=True,
                            controls=[
                                Text("🏭 Manajemen Data Mesin", size=18, weight="bold"),
                                kelola_mesin_view(page), 
                            ],
                        )
                    )

                # --- LOG PERFORMA ---
                elif selected_label == "Log Performa":
                    content.controls.append(
                        Column(
                            spacing=10,
                            expand=True,
                            controls=[
                                Text("📊 Log Performa & Sensor", size=18, weight="bold"),
                                kelola_log_performa_view(page),
                            ],
                        )
                    )

                # --- LAPORAN OPERATOR ---
                elif selected_label == "Laporan Operator":
                    content.controls.append(
                        Column(
                            spacing=10,
                            expand=True,
                            controls=[
                                Text("⚠️ Laporan Kerusakan Operator", size=18, weight="bold"),
                                kelola_laporan_operator_view(page),
                            ],
                        )
                    )

                # --- REKAP DATA (KHUSUS ADMIN/MANAGER) ---
                elif selected_label == "Rekap Data":
                    content.controls.append(
                        Column(
                            spacing=10,
                            expand=True,
                            controls=[
                                Text("🖨️ Rekapitulasi & Cetak Data", size=18, weight="bold"),
                                rekap_data_view(page),
                            ],
                        )
                    )

                # --- PROFIL ---
                elif selected_label == "Profil User":
                    content.controls.append(
                        profil_view(
                            page,
                            session_user["username"],
                            session_user["hak_akses"]
                        )
                    )

                # --- TENTANG ---
                elif selected_label == "Tentang App":
                    content.controls.append(tentang_view())

                # --- LOGOUT ---
                elif selected_label == "Logout":
                    content.controls.append(
                        Container(
                            alignment=alignment.center,
                            content=Container(
                                width=420,
                                padding=25,
                                bgcolor=Colors.WHITE,
                                border_radius=16,
                                shadow=BoxShadow(blur_radius=20, color=Colors.BLACK12),
                                content=Column(
                                    horizontal_alignment="center",
                                    spacing=20,
                                    controls=[
                                        Icon(Icons.LOGOUT, size=60, color=Colors.RED_400),
                                        Text("Konfirmasi Logout", size=22, weight="bold"),
                                        Text(
                                            "Apakah Anda yakin ingin keluar dari sistem?",
                                            text_align="center",
                                            color=Colors.GREY_700
                                        ),
                                        Row(
                                            alignment="spaceEvenly",
                                            controls=[
                                                OutlinedButton(
                                                    "Batal",
                                                    icon=Icons.CLOSE,
                                                    on_click=lambda e: (
                                                        setattr(rail, "selected_index", 0),
                                                        change(None)
                                                    ),
                                                ),
                                                ElevatedButton(
                                                    "Logout",
                                                    icon=Icons.LOGOUT,
                                                    bgcolor=Colors.RED,
                                                    color=Colors.WHITE,
                                                    on_click=lambda e: proses_logout(),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        )
                    )

            except Exception as err:
                content.controls.append(Text(f"Terjadi Kesalahan: {err}", color=Colors.RED))
                print(traceback.format_exc())

            page.update()

        rail.on_change = change

        # ================= LAYOUT GABUNGAN =================
        page.add(
            Row(
                expand=True,
                spacing=12,
                controls=[
                    # ---------- SIDEBAR ----------
                    Container(
                        width=260,
                        padding=12,
                        bgcolor=Colors.WHITE,
                        border_radius=12,
                        shadow=BoxShadow(blur_radius=12, color=Colors.BLACK12),
                        content=Column(
                            spacing=18,
                            controls=[
                                Column(
                                    horizontal_alignment="center",
                                    spacing=8,
                                    controls=[
                                        Container(
                                            width=80,
                                            height=80,
                                            border_radius=40,
                                            bgcolor=Colors.BLUE_100,
                                            alignment=alignment.center,
                                            content=Icon(Icons.ENGINEERING, size=46),
                                        ),
                                        Text(session_user["username"], weight="bold"),
                                        Container(
                                            padding=5,
                                            bgcolor=Colors.GREEN_100 if session_user["hak_akses"] == 'admin' else Colors.ORANGE_100,
                                            border_radius=5,
                                            content=Text(
                                                str(session_user["hak_akses"]).upper(),
                                                size=10,
                                                weight="bold",
                                                color=Colors.GREEN_800 if session_user["hak_akses"] == 'admin' else Colors.ORANGE_800
                                            ),
                                        ),
                                        Divider(),
                                    ],
                                ),
                                Container(
                                    height=page.height - 220,
                                    content=rail,
                                ),
                            ],
                        ),
                    ),

                    # ---------- AREA KONTEN ----------
                    Container(
                        expand=True,
                        padding=15,
                        content=content,
                    ),
                ],
            )
        )

        change(None)

    # ================= START APLIKASI =================
    tampil_hallogin()

# Menjalankan aplikasi Flet
app(main)