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
        database="2025_db_mad_perawatan_mesin_uas"  # ✅ Sudah disesuaikan
    )

# =========================================================
# 🔹 HALAMAN PROFIL
# =========================================================
def profil_view(page: Page, username, hak_akses):

    input_username = TextField(
        label="Username Baru",
        prefix_icon=Icons.PERSON_OUTLINE,
        border_color=Colors.BLUE_GREY_400,
        width=320
    )

    input_password = TextField(
        label="Password Baru",
        prefix_icon=Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_color=Colors.BLUE_GREY_400,
        width=320
    )

    notif_profil = Text("", size=14)

    # ================= SIMPAN PERUBAHAN =================
    def simpan_perubahan(e):
        if not input_username.value and not input_password.value:
            notif_profil.value = "⚠️ Tidak ada perubahan yang diisi"
            notif_profil.color = Colors.RED
            page.update()
            return

        try:
            db = koneksi_database()
            cur = db.cursor()

            # Update Username jika diisi
            if input_username.value:
                cur.execute(
                    "UPDATE user SET username=%s WHERE username=%s",
                    (input_username.value, username)
                )
            
            # Update Password jika diisi
            if input_password.value:
                cur.execute(
                    "UPDATE user SET password=%s WHERE username=%s",
                    (input_password.value, input_username.value or username)
                )

            db.commit()
            cur.close()
            db.close()

            notif_profil.value = "✅ Data Akun berhasil diperbarui!"
            notif_profil.color = Colors.GREEN_700
            
            # Reset field setelah sukses
            input_username.value = ""
            input_password.value = ""
            page.update()

        except Exception as err:
            notif_profil.value = f"❌ Error: {err}"
            notif_profil.color = Colors.RED
            page.update()

    # ================= CARD PROFIL =================
    return Container(
        alignment=alignment.top_left,
        content=Container(
            width=450,
            padding=35,
            bgcolor="white",
            border_radius=15,
            border=border.all(1, Colors.GREY_300), # Tambah border tipis biar rapi
            shadow=BoxShadow(
                blur_radius=15, 
                color=Colors.BLACK12,
                offset=Offset(0, 5)
            ),
            content=Column(
                spacing=20,
                horizontal_alignment="center",
                controls=[
                    # Header Profil dengan nuansa Teknik
                    Container(
                        padding=15,
                        border_radius=50,
                        bgcolor=Colors.BLUE_50,
                        content=Icon(Icons.ENGINEERING, size=80, color=Colors.BLUE_GREY_700),
                    ),
                    
                    Column(
                        spacing=5,
                        horizontal_alignment="center",
                        controls=[
                            Text(f"{username}", size=22, weight="bold", color=Colors.BLUE_GREY_900),
                            Container(
                                padding=padding.symmetric(horizontal=10, vertical=5),
                                bgcolor=Colors.ORANGE_100 if hak_akses == 'admin' else Colors.GREEN_100,
                                border_radius=5,
                                content=Text(
                                    f"Role: {hak_akses.upper()}", 
                                    size=12, 
                                    weight="bold",
                                    color=Colors.ORANGE_800 if hak_akses == 'admin' else Colors.GREEN_800
                                )
                            )
                        ]
                    ),

                    Divider(height=30, thickness=1),

                    Text("Edit Keamanan Akun", size=14, color=Colors.GREY_500),

                    input_username,
                    input_password,

                    Container(height=10), # Spacer

                    ElevatedButton(
                        "Simpan Perubahan", 
                        icon=Icons.SAVE, 
                        width=320, 
                        height=50, 
                        style=ButtonStyle(
                            shape=RoundedRectangleBorder(radius=10),
                            bgcolor=Colors.BLUE_GREY_700, # Warna tombol lebih 'industrial'
                            color=Colors.WHITE,
                        ),
                        on_click=simpan_perubahan, 
                    ),

                    notif_profil
                ],
            ),
        ),
    )