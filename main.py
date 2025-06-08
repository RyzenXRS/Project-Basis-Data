import psycopg2
from psycopg2.extras import RealDictCursor
import os 

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def connect():
    return psycopg2.connect(
        host="localhost",
        database="MaggottPY",
        user="postgres",
        password="321"
    )

def generate_id(prefix, table, id_column):
    conn = connect()
    cur = conn.cursor()
    query = f"SELECT {id_column} FROM {table} WHERE {id_column} LIKE %s ORDER BY {id_column} DESC LIMIT 1"
    cur.execute(query, (f"{prefix}%",))
    last_id = cur.fetchone()
    if last_id:
        last_num = int(last_id[0].replace(prefix, ""))
        new_id = f"{prefix}{last_num + 1:03d}"
    else:
        new_id = f"{prefix}001"
    cur.close()
    conn.close()
    return new_id


def generate_user_id(role):
    conn = connect()
    cur = conn.cursor()

    prefix = {
        'admin': 'AD',
        'pembudidaya': 'PD',
        'supplier': 'SP'
    }.get(role, 'XX')

    cur.execute("""
        SELECT id_user FROM users
        WHERE id_user LIKE %s
        ORDER BY id_user DESC
        LIMIT 1
    """, (f"{prefix}%",))
    
    last_id = cur.fetchone()

    if last_id:
        last_num = int(last_id[0][2:])
        new_id = f"{prefix}{last_num + 1:03d}"
    else:
        new_id = f"{prefix}001"

    cur.close()
    conn.close()
    return new_id


def register_pembudidaya():
    conn = connect()
    cur = conn.cursor()
    nama = input("Masukkan nama : ")
    email = input("Masukkan Email : ")
    nomer_telepon = input("Masukkan Nomer Telepon : ")
    password = input("Masukkan password : ")
    deskripsi = input("Alamat : ")
    role = "pembudidaya"
    id_user = generate_user_id(role)

    cur.execute("""
        INSERT INTO users (id_user, nama_user, alamat, no_telp, email, password, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (id_user, nama, deskripsi, nomer_telepon, email, password, role))

    conn.commit()
    cur.close()
    conn.close()
    print(f"User {nama} berhasil didaftarkan dengan ID {id_user}")
    return


def register_supplier():
    conn = connect()
    cur = conn.cursor()
    nama = input("Masukkan nama : ")
    email = input("Masukkan Email : ")
    nomer_telepon = input("Masukkan Nomer Telepon : ")
    password = input("Masukkan password : ")
    deskripsi = input("Alamat : ")
    role = "supplier"
    id_user = generate_user_id(role)

    cur.execute("""
        INSERT INTO users (id_user, nama_user, alamat, no_telp, email, password, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (id_user, nama, deskripsi, nomer_telepon, email, password, role))

    conn.commit()
    cur.close()
    conn.close()
    print(f"User {nama} berhasil didaftarkan dengan ID {id_user}")
    return

def login_admin():
    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    email = input("Email : ")
    password = input("Password : ")
    cur.execute("""SELECT * FROM users WHERE email = %s AND password = %s""", (email,password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        print("Login berhasil")
        return user
    else: 
        print("Email atau Password salah !")

def login_user():
    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    email = input("Email : ")
    password = input("Password : ")

    cur.execute("""
        SELECT * FROM users WHERE email = %s AND password = %s
    """, (email, password))
    user = cur.fetchone()

    if user:
        cur.execute("""UPDATE users SET last_activity = NOW() WHERE email = %s""", (email,))
        conn.commit()
        print(f"\nLogin berhasil! Selamat datang {user['nama_user']}, kamu login sebagai {user['role']}.\n")
        cur.close()
        conn.close()
        return user
    else:
        print("Email atau Password salah!")
        cur.close()
        conn.close()
        return None


# ======== Admin Things ===========
def pengguna_online():
    conn = connect()
    cur = conn.cursor()

    clear_screen()
    print("=== Cek Pengguna ===")
    print("[1] Pembudidaya")
    print("[2] Supplier")
    print("[3] Semua User")
    pilihan = input("Pilih kategori [1/2/3]: ")

    if pilihan not in ['1', '2', '3']:
        print("Pilihan tidak valid.")
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")
        return

    print("\nDaftar User : ")

    if pilihan == '1':
        cur.execute("""
            SELECT id_user, nama_user, email, role, last_activity 
            FROM users WHERE role = 'pembudidaya'
        """)
    elif pilihan == '2':
        cur.execute("""
            SELECT id_user, nama_user, email, role, last_activity 
            FROM users WHERE role = 'supplier'
        """)
    elif pilihan == '3':
        cur.execute("""
            SELECT id_user, nama_user, email, role, last_activity 
            FROM users ORDER BY role
        """)

    hasil = cur.fetchall()

    if not hasil:
        print("Belum ada pengguna terdaftar.")
    else:
        roles = ""
        for row in hasil:
            role = row[3]
            if role != roles:
                print(f"--- {role.capitalize()} ---")
                roles = role

            last_login = row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "Belum pernah login"
            print(f"ID: {row[0]}, Nama: {row[1]}, Email: {row[2]}, Login Terakhir: {last_login}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def lihat_sampah():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT s.id_sampah_organik, s.jenis_sampah, s.harga_per_kg, u.nama_user FROM sampah_organik s JOIN users u ON s.id_supplier = u.id_user")
    hasil = cur.fetchall()

    print("\nDaftar Sampah Organik:")
    if not hasil:
        print("Belum ada sampah organik tersedia.")
    else:
        for row in hasil:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Harga/kg: {row[2]}, Supplier: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")
        
def lihat_produk_maggot():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT m.id_maggot, m.jenis_maggot, m.harga_per_kg, u.nama_user FROM maggot m JOIN users u ON m.id_pembudidaya = u.id_user")
    hasil = cur.fetchall()

    print("\nDaftar Produk Maggot:")
    if not hasil:
        print("Belum ada produk maggot tersedia.")
    else:
        for row in hasil:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Harga/kg: {row[2]}, Pembudidaya: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

# ======== Pemebudidaya Things ===========
def tambah_stok_maggot(id_user):
    conn = connect()
    cur = conn.cursor()

    while True:
        cur.execute("SELECT id_maggot, jenis_maggot FROM maggot WHERE id_pembudidaya = %s", (id_user,))
        maggot_list = cur.fetchall()
        if not maggot_list:
            print("Anda belum memiliki produk maggot. Silakan tambahkan produk maggot terlebih dahulu.")
            cur.close()
            conn.close()
            return

        print("\nDaftar Maggot Anda:")
        for row in maggot_list:
            print(f"- ID: {row[0]}, Jenis: {row[1]}")

        id_maggot = input("Pilih ID Maggot dari daftar di atas (atau ketik 'batal' untuk kembali): ").strip()
        if id_maggot.lower() == 'batal':
            print("Tambah produk dibatalkan.")
            break

        cur.execute("SELECT 1 FROM maggot WHERE id_maggot = %s AND id_pembudidaya = %s", (id_maggot, id_user))
        if not cur.fetchone():
            print(f"ID Maggot {id_maggot} tidak ditemukan atau bukan milik Anda. Coba lagi.")
            continue
        
        while True:
            try:
                jumlah = int(input("Jumlah (kg): "))
                if jumlah <= 0:
                    print("Jumlah harus lebih besar dari nol.")
                    continue
                break
            except ValueError:
                print("Input harus berupa angka.")

        while True:
            status = input("Status (tersedia/habis): ").lower()
            if status in ['tersedia', 'habis']:
                break
            print("Status harus 'tersedia' atau 'habis'.")

        id_stok = generate_id("SM", "stok_maggot", "id_stok_maggot")
        cur.execute("""
            INSERT INTO stok_maggot (id_stok_maggot, id_maggot, jumlah_kg, status)
            VALUES (%s, %s, %s, %s)
        """, (id_stok, id_maggot, jumlah, status))
        conn.commit()
        print("Stok maggot berhasil ditambahkan.")
        break 

    cur.close()
    conn.close()


def lihat_stok_maggot(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT sm.id_stok_maggot, m.jenis_maggot, sm.jumlah_kg, sm.status FROM stok_maggot sm JOIN maggot m ON sm.id_maggot = m.id_maggot WHERE m.id_pembudidaya = %s", (id_user,))
    rows = cur.fetchall()
    
    clear_screen()
    print("\nStok Maggot Anda:")
    if not rows:
        print("Belum ada stok maggot.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Status: {row[3]}")
    
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def tambah_stok_sampah(id_user):
    conn = connect()
    cur = conn.cursor()
    id_stok = generate_id("SSO", "stok_sampah_organik", "id_stok_sampah")
    id_sampah = input("ID Sampah Organik: ")
    jumlah = int(input("Jumlah (kg): "))
    status = input("Status (tersedia/habis): ")
    cur.execute("INSERT INTO stok_sampah_organik (id_stok_sampah, id_sampah_organik, jumlah_kg, status) VALUES (%s, %s, %s, %s)", (id_stok, id_sampah, jumlah, status))
    conn.commit()
    cur.close()
    conn.close()
    print("Stok sampah ditambahkan.")

def lihat_stok_sampah(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT ss.id_stok_sampah, so.jenis_sampah, ss.jumlah_kg, ss.status FROM stok_sampah_organik ss JOIN sampah_organik so ON ss.id_sampah_organik = so.id_sampah_organik WHERE so.id_supplier = %s", (id_user,))
    rows = cur.fetchall()

    print("\nStok Sampah Anda:")
    if not rows:
        print("Belum ada stok sampah.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Status: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def beli_sampah_organik(id_user):
    conn = connect()
    cur = conn.cursor()
    id_transaksi = generate_id("TS", "transaksi_sampah_organik", "id_transaksi_sampah")
    id_sampah = input("ID Sampah: ")
    jumlah = int(input("Jumlah (kg): "))
    deskripsi = input("Keterangan: ")
    cur.execute("INSERT INTO transaksi_sampah_organik (id_transaksi_sampah, id_pembeli, id_sampah_organik, jumlah_kg, deskripsi, status) VALUES (%s, %s, %s, %s, %s, 'diproses')", (id_transaksi, id_user, id_sampah, jumlah, deskripsi))
    conn.commit()
    cur.close()
    conn.close()
    print("Pembelian sampah tercatat.")

def jual_maggot(id_user):
    conn = connect()
    cur = conn.cursor()
    id_transaksi = generate_id("TM", "transaksi_maggot", "id_transaksi_maggot")
    id_maggot = input("ID Maggot: ")
    jumlah = int(input("Jumlah (kg): "))
    pembeli = input("ID Pembeli: ")
    deskripsi = input("Keterangan: ")
    cur.execute("INSERT INTO transaksi_maggot (id_transaksi_maggot, id_pembeli, id_maggot, jumlah_kg, deskripsi, status) VALUES (%s, %s, %s, %s, %s, 'diproses')", (id_transaksi, pembeli, id_maggot, jumlah, deskripsi))
    conn.commit()
    cur.close()
    conn.close()
    print("Penjualan maggot tercatat.")

def catat_harian(id_user):
    conn = connect()
    cur = conn.cursor()
    id_transaksi = generate_id("TS", "transaksi_sampah_organik", "id_transaksi_sampah")
    deskripsi = input("Deskripsi kegiatan: ")
    cur.execute("INSERT INTO transaksi_sampah_organik (id_transaksi_sampah, id_pembeli, id_sampah_organik, jumlah_kg, deskripsi, status) VALUES (%s, %s, NULL, 0, %s, 'harian')", (id_transaksi, id_user, deskripsi))
    conn.commit()
    cur.close()
    conn.close()
    print("Catatan harian berhasil disimpan.")

def riwayat_transaksi_pembelian(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT t.id_transaksi_sampah, so.jenis_sampah, t.jumlah_kg, t.deskripsi FROM transaksi_sampah_organik t JOIN sampah_organik so ON t.id_sampah_organik = so.id_sampah_organik WHERE t.id_pembeli = %s AND t.status = 'diproses'", (id_user,))
    rows = cur.fetchall()

    print("\nRiwayat Pembelian Sampah:")
    if not rows:
        print("Belum ada riwayat pembelian.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Catatan: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def riwayat_transaksi_penjualan(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT t.id_transaksi_maggot, m.jenis_maggot, t.jumlah_kg, t.deskripsi FROM transaksi_maggot t JOIN maggot m ON t.id_maggot = m.id_maggot WHERE m.id_pembudidaya = %s AND t.status = 'diproses'", (id_user,))
    rows = cur.fetchall()

    print("\nRiwayat Penjualan Maggot:")
    if not rows:
        print("Belum ada riwayat penjualan.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Catatan: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

# ======== Supplier Things ===========
def tambah_stok(id_user):
    conn = connect()
    cur = conn.cursor()
    id_stok = generate_id("SSO", "stok_sampah_organik", "id_stok_sampah")
    id_sampah = input("ID Sampah Organik: ")
    jumlah = int(input("Jumlah (kg): "))
    status = input("Status (tersedia/habis): ")
    cur.execute("INSERT INTO stok_sampah_organik (id_stok_sampah, id_sampah_organik, jumlah_kg, status) VALUES (%s, %s, %s, %s)", (id_stok, id_sampah, jumlah, status))
    conn.commit()
    cur.close()
    conn.close()
    print("Stok sampah ditambahkan.")

def lihat_stok(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT ss.id_stok_sampah, so.jenis_sampah, ss.jumlah_kg, ss.status FROM stok_sampah_organik ss JOIN sampah_organik so ON ss.id_sampah_organik = so.id_sampah_organik WHERE so.id_supplier = %s", (id_user,))
    rows = cur.fetchall()
    print("Stok Sampah Anda:")
    for row in rows:
        print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Status: {row[3]}")
    cur.close()
    conn.close()

def terima_pesanan(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT ts.id_transaksi_sampah, u.nama_user, so.jenis_sampah, ts.jumlah_kg, ts.status FROM transaksi_sampah_organik ts JOIN sampah_organik so ON ts.id_sampah_organik = so.id_sampah_organik JOIN users u ON ts.id_pembeli = u.id_user WHERE so.id_supplier = %s AND ts.status = 'diproses'", (id_user,))
    rows = cur.fetchall()

    print("\nPesanan Masuk:")
    if not rows:
        print("Tidak ada pesanan masuk.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Pembeli: {row[1]}, Jenis: {row[2]}, Jumlah: {row[3]}kg, Status: {row[4]}")

    id_pilih = input("Masukkan ID transaksi yang ingin diterima (atau tekan Enter untuk batal): ")
    if id_pilih.strip():
        cur.execute("UPDATE transaksi_sampah_organik SET status = 'dikirim' WHERE id_transaksi_sampah = %s", (id_pilih,))
        conn.commit()
        print("Transaksi diperbarui menjadi dikirim.")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def beli_maggot(id_user):
        conn = connect()
        cur = conn.cursor()
        id_transaksi = generate_id("TM", "transaksi_maggot", "id_transaksi_maggot")
        id_maggot = input("ID Maggot: ")
        jumlah = int(input("Jumlah (kg): "))
        deskripsi = input("Keterangan: ")
        cur.execute("INSERT INTO transaksi_maggot (id_transaksi_maggot, id_pembeli, id_maggot, jumlah_kg, deskripsi, status) VALUES (%s, %s, %s, %s, %s, 'diproses')", (id_transaksi, id_user, id_maggot, jumlah, deskripsi))
        conn.commit()
        cur.close()
        conn.close()
        print("Pembelian maggot berhasil dicatat.")

def catat_harian(id_user):
    conn = connect()
    cur = conn.cursor()
    id_transaksi = generate_id("TS", "transaksi_sampah_organik", "id_transaksi_sampah")
    deskripsi = input("Deskripsi kegiatan: ")
    cur.execute("INSERT INTO transaksi_sampah_organik (id_transaksi_sampah, id_pembeli, id_sampah_organik, jumlah_kg, deskripsi, status) VALUES (%s, %s, NULL, 0, %s, 'harian')", (id_transaksi, id_user, deskripsi))
    conn.commit()
    cur.close()
    conn.close()
    print("Catatan harian supplier disimpan.")

def riwayat_penjualan(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT ts.id_transaksi_sampah, so.jenis_sampah, ts.jumlah_kg, ts.deskripsi FROM transaksi_sampah_organik ts JOIN sampah_organik so ON ts.id_sampah_organik = so.id_sampah_organik WHERE so.id_supplier = %s AND ts.status = 'diproses'", (id_user,))
    rows = cur.fetchall()

    print("\nRiwayat Penjualan Sampah:")
    if not rows:
        print("Belum ada riwayat penjualan.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Catatan: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def riwayat_pembelian(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT tm.id_transaksi_maggot, m.jenis_maggot, tm.jumlah_kg, tm.deskripsi FROM transaksi_maggot tm JOIN maggot m ON tm.id_maggot = m.id_maggot WHERE tm.id_pembeli = %s", (id_user,))
    rows = cur.fetchall()

    print("\nRiwayat Pembelian Maggot:")
    if not rows:
        print("Belum ada riwayat pembelian.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Jenis: {row[1]}, Jumlah: {row[2]}kg, Catatan: {row[3]}")

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

# ======== Menu Menu ===========
def menu_admin(admin):
    clear_screen()
    print(f"Halo {admin['nama_user']}, Kamu login sebagai Admin!")
    while True:
        clear_screen()
        print("""
Menu Admin:
[1] Lihat Pengguna Online
[2] Daftar Sampah
[3] Daftar Produk Maggot
[4] Logout
    """)
        pilihan = input("Masukkan pilihan: ")

        match pilihan:
            case '1':
                pengguna_online()
            case '2':
                lihat_sampah()
            case '3':
                lihat_produk_maggot()
            case '4':
                main()
                return
            case _:
                print("Pilihan tidak valid.")

def menu_pembudidaya(id_user):
    while True:
        clear_screen()
        print("""
Menu Pembudidaya:
[1] Tambah Stok Maggot
[2] Lihat Stok Maggot
[3] Tambah Stok Sampah
[4] Lihat Stok Sampah
[5] Beli Sampah Organik
[6] Jual Maggot
[7] Catatan Harian
[8] Riwayat Pembelian Sampah
[9] Riwayat Penjualan Maggot
[0] Logout
            """)
        pilihan = input("Masukkan pilihan: ")
        match pilihan:
            case '1':
                tambah_stok_maggot(id_user)
            case '2':
                lihat_stok_maggot(id_user)
            case '3':
                tambah_stok_sampah(id_user)
            case '4':
                lihat_stok_sampah(id_user)
            case '5':
                beli_sampah_organik(id_user)
            case '6':
                jual_maggot(id_user)
            case '7':
                catat_harian(id_user)
            case '8':
                riwayat_transaksi_pembelian(id_user)
            case '9':
                riwayat_transaksi_penjualan(id_user)
            case '0':
                main()
                return
            case _:
                print("Pilihan tidak valid.")

def menu_supplier(id_user):
        while True:
            clear_screen()
            print("""
Menu Supplier:
[1] Tambah Stok Sampah
[2] Lihat Stok Sampah
[3] Terima Pesanan Sampah
[4] Beli Maggot   
[5] Catat Harian
[6] Riwayat Penjualan Sampah
[7] Riwayat Pembelian Maggot
[0] Logout
            """)
            pilihan = input("Masukkan pilihan: ")

            match pilihan:
                case '1':
                    tambah_stok(id_user)
                case '2':
                    lihat_stok(id_user)
                case '3':
                    terima_pesanan(id_user)
                case '4':
                    beli_maggot(id_user)
                case '5':
                    catat_harian(id_user)
                case '6':
                    riwayat_penjualan(id_user)
                case '7':
                    riwayat_pembelian(id_user)
                case '0':
                    main()
                    return
                case _:
                    print("Pilihan tidak valid.")

#========================= UPDATE ATAS !!============================
def main():
    clear_screen()
    conn = connect()
    cur = conn.cursor()
    while True:
        print(
            """
╔══════════════════╗
║  Selamat Datang  ║
║┌────────────────┐║
║│  1. Login      │║
║│  2. Register   │║
║│  3. Keluar     │║    
║├────────────────┤║
║│   Home  Page   │║
║└────────────────┘║
╚══════════════════╝
            """)
        pilihan = input("Masukkan pilihan [1,2,3] : ")
        match pilihan:
            case '1':
                clear_screen()
                print("Login sebagai :")
                print("[1] User (Pembudidaya / Supplier)")
                print("[2] Admin")
                pilih = int(input("Masukkan pilihan login : "))

                if pilih == 1:
                    user = login_user()
                    if user:
                        if user['role'] == 'pembudidaya':
                            menu_pembudidaya(id_user=user['id_user'])
                        elif user['role'] == 'supplier':
                            menu_supplier(id_user=user['id_user'])
                elif pilih == 2:
                    admin = login_admin()
                    if admin:
                        menu_admin(admin)
                else:
                    print("Tidak ada pilihan")
                return
            case '2':
                print("Register sebagai  ")
                print("[1] Pembudidaya")
                print("[2] Supplier")
                pilihan = int(input("Pilih Register : "))

                if pilihan == 1:
                    register_pembudidaya()
                elif pilihan == 2:
                    register_supplier()
                else:
                    print("Tidak ada pilihan")
            case '3':
                print("Kamu memilih keluar.")
                break
            case _:
                print("Pilihan tidak ada")

main()



