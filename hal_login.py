import pymysql
from flet import *
from datetime import datetime


# =========================================================
# 🔹 KONEKSI KE DATABASE
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_perawatan_mesin_uas" 
    )

def login_view(page: Page, on_login_success):
    
    # Input field
    inputan_username = TextField(
        label="Username", 
        width=300, 
        prefix_icon=Icons.PERSON_OUTLINE,
        border_color=Colors.BLUE_GREY_400
    )
    
    inputan_password = TextField(
        label="Password", 
        password=True, 
        width=300, 
        prefix_icon=Icons.LOCK_OUTLINE,
        can_reveal_password=True,
        border_color=Colors.BLUE_GREY_400
    )
    
    notif_login = Text("", size=12)

    # 🔘 Logika Proses Login
    def proses_login(e):
        try:
            # 1. Cek Koneksi
            buka_koneksi = koneksi_database()
            perintahSQL = buka_koneksi.cursor()
            
            # 2. Cek User
            perintahSQL.execute(
                "SELECT id_user, username, password, hak_akses FROM user WHERE username=%s AND password=%s",
                (inputan_username.value, inputan_password.value)
            )
            user = perintahSQL.fetchone()

            # 3. Validasi
            if user:
                v_id_user, v_username, v_password, v_hak_akses = user
                
                # Update akses terakhir
                perintahSQL.execute("UPDATE user SET akses_terakhir=%s WHERE id_user=%s", (datetime.now(), v_id_user))
                buka_koneksi.commit()
                perintahSQL.close()
                buka_koneksi.close()
                
                # ✅ LANGSUNG PINDAH HALAMAN (Tanpa Animasi/Delay)
                print("Login Berhasil! Memuat Dashboard...") # Cek di terminal bawah
                on_login_success(v_username, v_hak_akses)
            
            else:
                notif_login.value = "❌ Username atau password salah!"
                notif_login.color = Colors.RED
                page.update()
        
        except Exception as err:
            print(f"Error Login: {err}") # Cek di terminal bawah jika ada error
            notif_login.value = f"❌ Error: {err}"
            notif_login.color = Colors.RED
            page.update()

    # 🔘 UI Kartu Login
    login_card = Container(
        width=400,
        padding=40,
        bgcolor="white",
        border_radius=20,
        shadow=BoxShadow(blur_radius=30, color=Colors.BLACK26),
        border=border.all(1, Colors.GREY_200),
        content=Column(
            horizontal_alignment="center",
            spacing=20,
            controls=[
                Container(
                    padding=20,
                    bgcolor=Colors.BLUE_50,
                    border_radius=50,
                    content=Icon(Icons.FACTORY, size=50, color=Colors.BLUE_GREY_700),
                ),
                Column(
                    spacing=5,
                    horizontal_alignment="center",
                    controls=[
                        Text("System Login", size=24, weight="bold", color=Colors.BLUE_GREY_900),
                        Text("Maintenance Management", size=12, color=Colors.GREY_500),
                    ]
                ),
                Divider(height=10, color="transparent"),
                inputan_username,
                inputan_password,
                Divider(height=10, color="transparent"),
                ElevatedButton(
                    "Masuk System", 
                    width=300, 
                    height=50, 
                    icon=Icons.LOGIN,
                    style=ButtonStyle(
                        shape=RoundedRectangleBorder(radius=10),
                        bgcolor=Colors.BLUE_GREY_800,
                        color=Colors.WHITE,
                    ),
                    on_click=proses_login
                ),
                notif_login
            ],
        ),
    )

    return Container(
        expand=True,
        alignment=alignment.center,
        bgcolor="#e8ecf3",
        content=login_card,
    )