from flet import *

def tentang_view():
    return Container(
        alignment=alignment.top_left,
        content=Container(
            width=600,
            padding=35,
            bgcolor="white",
            border_radius=15,
            border=border.all(1, Colors.GREY_300),
            shadow=BoxShadow(
                blur_radius=15, 
                color=Colors.BLACK12, 
                offset=Offset(0, 5)
            ),
            content=Column(
                spacing=20,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    # ================= HEADER ICON =================
                    Container(
                        padding=20,
                        bgcolor=Colors.BLUE_50, # Background ikon lembut
                        border_radius=60,
                        content=Icon(Icons.PRECISION_MANUFACTURING, size=60, color=Colors.BLUE_GREY_700),
                    ),
                    
                    Column(
                        spacing=5,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        controls=[
                            Text(
                                "Sistem Maintenance Mesin",
                                size=22,
                                weight=FontWeight.BOLD,
                                color=Colors.BLUE_GREY_900
                            ),
                            Text(
                                "Versi 1.0.0 (Build 2025)",
                                size=12,
                                color=Colors.GREY_500
                            ),
                        ]
                    ),

                    Divider(thickness=1, color=Colors.GREY_200),

                    # ================= DESKRIPSI =================
                    Text(
                        "Sistem Informasi Manajemen Perawatan Mesin Industri "
                        "sebagai proyek UAS Mobile Application Development.",
                        text_align=TextAlign.CENTER,
                        size=15,
                        weight=FontWeight.W_500,
                        color=Colors.BLACK87
                    ),

                    Text(
                        "Dirancang untuk memudahkan teknisi dalam pendataan aset mesin, "
                        "monitoring log performa sensor (Suhu, RPM, Voltase), "
                        "serta manajemen pelaporan kerusakan dari operator lapangan.",
                        text_align=TextAlign.CENTER,
                        size=14,
                        color=Colors.GREY_600,
                    ),

                    Divider(thickness=1, color=Colors.GREY_200),

                    # ================= INFORMASI TEKNIS =================
                    Row(
                        alignment=MainAxisAlignment.CENTER,
                        spacing=40,
                        controls=[
                            _info_item(Icons.CODE, "Framework", "Flet (Python)"),
                            _info_item(Icons.STORAGE, "Database", "MariaDB / MySQL"),
                            _info_item(Icons.QUERY_STATS, "Fungsi", "Monitoring"),
                        ],
                    ),

                    Divider(thickness=1, color=Colors.GREY_200),

                    # ================= FOOTER =================
                    Text(
                        "© 2025 • Proyek UAS • Teknik Informatika",
                        size=12,
                        color=Colors.GREY_400,
                        italic=True
                    ),
                ],
            ),
        ),
    )


# ================= HELPER WIDGET =================
def _info_item(icon, title, value):
    return Column(
        spacing=5,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        controls=[
            Icon(icon, size=30, color=Colors.ORANGE_700), # Warna aksen oranye (Industrial safety color)
            Text(title, size=11, color=Colors.GREY_500),
            Text(value, size=13, weight=FontWeight.BOLD, color=Colors.BLUE_GREY_800),
        ],
    )