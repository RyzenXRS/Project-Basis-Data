import psycopg2
from psycopg2.extras import RealDictCursor
import os
from tabulate import tabulate as tb

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def connect():
    return psycopg2.connect(
        host="localhost",
        database="MaggotPY",
        user="postgres",
        password="321"
    )

# ========== Gen ID otomatis ===========
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

# ========== Register ===========
def register_pembudidaya():
    conn = None
    cur = None
    try:
        clear_screen()
        nama = input("Masukkan nama : ").strip()
        email = input("Masukkan Email : ").strip()
        nomer_telepon = input("Masukkan Nomer Telepon : ").strip()
        password = input("Masukkan password : ").strip()
        deskripsi = input("Alamat : ").strip()
        if not all([nama, email, nomer_telepon, password, deskripsi]):
            print("Semua field harus diisi!")
            return

        role = "pembudidaya"
        id_user = generate_user_id(role)
        conn = connect()
        cur = conn.cursor()

        # Cek apakah email sudah terdaftar
        cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            print("Email sudah terdaftar. Gunakan email lain.")
            return

        # Eksekusi query insert
        cur.execute("""
            INSERT INTO users (id_user, nama_user, alamat, no_telp, email, password, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_user, nama, deskripsi, nomer_telepon, email, password, role))

        conn.commit()
        print(f"User {nama} berhasil didaftarkan dengan ID {id_user}")

    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
        print(f"Terjadi kesalahan pada database: {e}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error umum: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def register_supplier():
    conn = None
    cur = None
    try:
        clear_screen()
        nama = input("Masukkan nama : ").strip()
        email = input("Masukkan Email : ").strip()
        nomer_telepon = input("Masukkan Nomer Telepon : ").strip()
        password = input("Masukkan password : ").strip()
        deskripsi = input("Alamat : ").strip()

        # Validasi input tidak boleh kosong
        if not all([nama, email, nomer_telepon, password, deskripsi]):
            print("Semua field harus diisi!")
            return

        role = "supplier"
        id_user = generate_user_id(role)
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            print("Email sudah terdaftar. Gunakan email lain.")
            return

        cur.execute("""
            INSERT INTO users (id_user, nama_user, alamat, no_telp, email, password, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_user, nama, deskripsi, nomer_telepon, email, password, role))

        conn.commit()
        print(f"User {nama} berhasil didaftarkan dengan ID {id_user}")

    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
        print(f"Terjadi kesalahan pada database: {e}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error umum: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
def login_admin():
    conn = None
    cur = None
    try:
        email = input("Email : ").strip()
        password = input("Password : ").strip()
        if not email or not password:
            print("Email dan Password tidak boleh kosong.")
            return None
        conn = connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Eksekusi query
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()

        # Cek apakah user ditemukan
        if user and user['role'] == 'admin':
            print("Login berhasil")
            return user
        else:
            print("Email atau Password salah atau bukan akun admin.")
            return None

    except psycopg2.DatabaseError as e:
        print(f"Terjadi kesalahan pada database: {e}")
        return None

    except Exception as e:
        print(f"Error umum: {e}")
        return None

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def login_user():
    conn = None
    cur = None
    try:
        email = input("Email : ").strip()
        password = input("Password : ").strip()

        if not email or not password:
            print("Email dan Password tidak boleh kosong.")
            return None
        conn = connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Eksekusi query
        cur.execute("""
            SELECT * FROM users WHERE email = %s AND password = %s
        """, (email, password))
        user = cur.fetchone()

        if user:
            cur.execute("""
                UPDATE users SET last_activity = NOW() WHERE email = %s
            """, (email,))
            conn.commit()
            print(f"\nLogin berhasil! Selamat datang {user['nama_user']}, kamu login sebagai {user['role']}.\n")
            return user
        else:
            print("Email atau Password salah!")
            return None

    except psycopg2.DatabaseError as e:
        print(f"Terjadi kesalahan pada database: {e}")
        if conn:
            conn.rollback()
        return None

    except Exception as e:
        print(f"Error umum: {e}")
        return None

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
def profile(id_user):
    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    clear_screen()

    # Ambil data profil pengguna berdasarkan id_user
    cur.execute("SELECT nama_user, email, no_telp, alamat FROM users WHERE id_user = %s", (id_user,))
    user_data = cur.fetchone()

    if not user_data:
        print("Pengguna tidak ditemukan.")
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")
        return

    # Tampilkan profil pengguna dalam format tabulate
    print("\n=== Profil Pengguna ===\n")
    headers = ["Field", "Data"]
    table = [
        ["Nama", user_data['nama_user']],
        ["Email", user_data['email']],
        ["Nomor Telepon", user_data['no_telp']],
        ["Alamat", user_data['alamat']]
    ]
    print(tb(table, headers=headers, tablefmt="double_grid"))

    # Menu pilihan
    while True:
        print("\n[1] Edit Profil")
        print("[2] Kembali ke Menu Utama")
        pilihan = input("Masukkan pilihan: ").strip()
        match pilihan:
            case '1':
                edit_profile(id_user)
                break
            case '2':
                cur.close()
                conn.close()
                return
            case _:
                print("Pilihan tidak valid.")

def edit_profile(id_user):
    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Ambil data profil pengguna berdasarkan id_user
    cur.execute("SELECT nama_user, email, no_telp, alamat FROM users WHERE id_user = %s", (id_user,))
    user_data = cur.fetchone()

    if not user_data:
        print("Pengguna tidak ditemukan.")
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")
        return

    clear_screen()
    print("=== Edit Profil ===")
    print("Kosongkan kolom jika tidak ingin mengubahnya.\n")

    # Tampilkan data saat ini dengan tabulate
    headers = ["Field", "Data Saat Ini"]
    table = [
        ["Nama", user_data['nama_user']],
        ["Email", user_data['email']],
        ["Nomor Telepon", user_data['no_telp']],
        ["Alamat", user_data['alamat']]
    ]
    print(tb(table, headers=headers, tablefmt="grid"))
    print()  

    # Input baru untuk setiap field
    nama_baru = input(f"Nama (Saat ini: {user_data['nama_user']}): ").strip() or user_data['nama_user']
    email_baru = input(f"Email (Saat ini: {user_data['email']}): ").strip() or user_data['email']
    no_telp_baru = input(f"Nomor Telepon (Saat ini: {user_data['no_telp']}): ").strip() or user_data['no_telp']
    alamat_baru = input(f"Alamat (Saat ini: {user_data['alamat']}): ").strip() or user_data['alamat']

    # Perbarui data di database
    cur.execute("""
        UPDATE users 
        SET nama_user = %s, email = %s, no_telp = %s, alamat = %s 
        WHERE id_user = %s
    """, (nama_baru, email_baru, no_telp_baru, alamat_baru, id_user))
    conn.commit()

    print("\nProfil berhasil diperbarui!")
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu profil...")
    profile(id_user)  # Kembali ke halaman profil

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
        clear_screen()
    elif pilihan == '2':
        cur.execute("""
            SELECT id_user, nama_user, email, role, last_activity 
            FROM users WHERE role = 'supplier'
        """)
        clear_screen()
    elif pilihan == '3':
        cur.execute("""
            SELECT id_user, nama_user, email, role, last_activity 
            FROM users ORDER BY role
        """)
        clear_screen()

    hasil = cur.fetchall()
    if not hasil:
        print("Belum ada pengguna terdaftar.")
    else:
        headers = ["ID", "Nama", "Email", "Role", "Login Terakhir"]
        table_data = []
        current_role = ""
        for row in hasil:
            role = row[3]
            if role != current_role:
                if current_role:
                    print(tb(table_data, headers=headers, tablefmt="double_grid"))
                    table_data.clear()
                print(f"\n--- {role.capitalize()} ---")
                current_role = role
            last_login = row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else "Belum pernah login"
            table_data.append([row[0], row[1], row[2], row[3], last_login])
        if table_data:
            print(tb(table_data, headers=headers, tablefmt="double_grid"))

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
        headers = ["ID", "Jenis", "Harga/kg", "Supplier"]
        table_data = [[row[0], row[1], f"Rp{row[2]}", row[3]] for row in hasil]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
        
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
        headers = ["ID", "Jenis", "Harga/kg", "Pembudidaya"]
        table_data = [[row[0], row[1], f"Rp{row[2]}", row[3]] for row in hasil]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
    
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

# ======== Pemebudidaya Things ===========
def lihat_stok_sampah(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT ss.id_stok_sampah, so.jenis_sampah, ss.jumlah_kg, ss.status FROM stok_sampah_organik ss JOIN sampah_organik so ON ss.id_sampah_organik = so.id_sampah_organik WHERE so.id_supplier = %s", (id_user,))
    rows = cur.fetchall()
    
    print("\nStok Sampah Anda:")
    if not rows:
        print("Belum ada stok sampah.")
    else:
        headers = ["ID Stok", "Jenis", "Jumlah (kg)", "Status"]
        table_data = [[row[0], row[1], row[2], row[3]] for row in rows]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
        
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def lihat_stok_sampah_dibeli():
    conn = connect()
    cur = conn.cursor()

    clear_screen()
    print("=== Stok Sampah Organik Tersedia ===\n")

    cur.execute("""
        SELECT 
            ss.id_stok_sampah,
            so.jenis_sampah,
            ss.jumlah_kg,
            u.nama_user AS supplier,
            so.harga_per_kg
        FROM stok_sampah_organik ss
        JOIN sampah_organik so ON ss.id_sampah_organik = so.id_sampah_organik
        JOIN users u ON so.id_supplier = u.id_user
        WHERE ss.status = 'tersedia' AND ss.jumlah_kg > 0
    """)
    rows = cur.fetchall()

    if not rows:
        print("Belum ada stok sampah yang tersedia untuk dibeli.")
    else:
        headers = ["ID Stok", "Jenis Sampah", "Jumlah (kg)", "Supplier", "Harga/kg"]
        table_data = [[row[0], row[1], row[2], row[3], f"Rp{row[4]}"] for row in rows]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))

    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali...")
    
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

    print("\n--- Tambah Stok Sampah ---")
    while True:
        id_sampah = input("ID Sampah Organik: ").strip()
        if id_sampah:
            cur.execute("SELECT 1 FROM sampah_organik WHERE id_sampah_organik = %s AND id_supplier = %s", (id_sampah, id_user))
            if cur.fetchone():
                break
            else:
                print("ID Sampah tidak ditemukan atau bukan milik Anda.")
        else:
            print("ID Sampah tidak boleh kosong.")
    while True:
        jumlah_input = input("Jumlah (kg): ").strip()
        try:
            jumlah = int(jumlah_input)
            if jumlah > 0:
                break
            else:
                print("Jumlah harus lebih besar dari nol.")
        except ValueError:
            print("Input harus berupa angka.")
    while True:
        status = input("Status (tersedia/habis): ").strip().lower()
        if status in ['tersedia', 'habis']:
            break
        else:
            print("Status harus 'tersedia' atau 'habis'.")
    id_stok = generate_id("SSO", "stok_sampah_organik", "id_stok_sampah")

    try:
        cur.execute("""
            INSERT INTO stok_sampah_organik (id_stok_sampah, id_sampah_organik, jumlah_kg, status)
            VALUES (%s, %s, %s, %s)
        """, (id_stok, id_sampah, jumlah, status))
        conn.commit()
        print("Stok sampah berhasil ditambahkan.")
    except Exception as e:
        print(f"Gagal menambahkan stok: {e}")
    finally:
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
        headers = ["ID Stok", "Jenis", "Jumlah (kg)", "Status"]
        table_data = [[row[0], row[1], row[2], row[3]] for row in rows]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
        
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

def beli_sampah_organik(id_user):
    conn = None
    cur = None

    try:
        # Koneksi database
        conn = connect()
        cur = conn.cursor()

        clear_screen()
        print("=== Daftar Sampah Organik Tersedia ===\n")

        # Ambil data stok yang tersedia
        cur.execute("""
            SELECT 
                ss.id_stok_sampah,
                so.jenis_sampah,
                ss.jumlah_kg,
                u.nama_user AS supplier,
                so.harga_per_kg,
                so.id_sampah_organik
            FROM stok_sampah_organik ss
            JOIN sampah_organik so ON ss.id_sampah_organik = so.id_sampah_organik
            JOIN users u ON so.id_supplier = u.id_user
            WHERE ss.status = 'tersedia' AND ss.jumlah_kg > 0
        """)
        hasil = cur.fetchall()

        if not hasil:
            print("Tidak ada stok tersedia saat ini.")
            input("\nTekan Enter untuk kembali...")
            return

        headers = ["ID Stok", "Jenis", "Jumlah (kg)", "Supplier", "Harga/kg"]
        table_data = [[row[0], row[1], row[2], row[3], f"Rp{row[4]}"] for row in hasil]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
        print("\nMasukkan ID Stok untuk membeli.")

        # Input ID Stok
        while True:
            id_stok = input("ID Stok (ketik 'batal' untuk batal): ").strip()
            if id_stok.lower() == 'batal':
                print("Pembelian dibatalkan.")
                return
            cur.execute("""
                SELECT 
                    ss.id_stok_sampah, 
                    ss.jumlah_kg, 
                    so.id_sampah_organik,
                    so.harga_per_kg
                FROM stok_sampah_organik ss
                JOIN sampah_organik so ON ss.id_sampah_organik = so.id_sampah_organik
                WHERE ss.id_stok_sampah = %s AND ss.status = 'tersedia'
            """, (id_stok,))
            stok = cur.fetchone()
            if stok:
                break
            else:
                print("ID Stok tidak ditemukan atau stok tidak tersedia.")

        id_stok_sampah, jumlah_tersedia, id_sampah, harga = stok

        # Input Jumlah
        while True:
            jumlah_input = input(f"Jumlah (kg) - Stok tersedia: {jumlah_tersedia} kg (ketik 'batal' untuk batal): ").strip()
            if jumlah_input.lower() == 'batal':
                print("Pembelian dibatalkan.")
                return
            try:
                jumlah = int(jumlah_input)
                if 0 < jumlah <= jumlah_tersedia:
                    break
                else:
                    print(f"Jumlah harus lebih besar dari 0 dan tidak melebihi {jumlah_tersedia} kg.")
            except ValueError:
                print("Input harus berupa angka.")

        deskripsi = input("Keterangan (opsional): ")

        id_transaksi = generate_id("TS", "transaksi_sampah_organik", "id_transaksi_sampah")

        # Eksekusi transaksi
        cur.execute("""
            INSERT INTO transaksi_sampah_organik (
                id_transaksi_sampah, id_pembeli, id_sampah_organik, jumlah_kg, deskripsi, status
            ) VALUES (%s, %s, %s, %s, %s, 'diproses')
        """, (id_transaksi, id_user, id_sampah, jumlah, deskripsi))

        # Kurangi stok
        sisa = jumlah_tersedia - jumlah
        if sisa > 0:
            cur.execute("UPDATE stok_sampah_organik SET jumlah_kg = %s WHERE id_stok_sampah = %s", (sisa, id_stok_sampah))
        else:
            cur.execute("DELETE FROM stok_sampah_organik WHERE id_stok_sampah = %s", (id_stok_sampah,))

        conn.commit()
        total_harga = harga * jumlah
        print(f"\nPembelian berhasil dicatat!")
        print(f"Total Harga: Rp{total_harga}")

    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
        print(f"Terjadi kesalahan pada database: {e}")
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error umum: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        input("\nTekan Enter untuk kembali...")

def jual_maggot(id_user):
    conn = connect()
    cur = conn.cursor()

    print("\n--- Jual Maggot ---")
    while True:
        id_maggot = input("ID Maggot: ").strip()
        if not id_maggot:
            print("ID Maggot tidak boleh kosong.")
            continue

        cur.execute("SELECT 1 FROM maggot WHERE id_maggot = %s AND id_pembudidaya = %s", (id_maggot, id_user))
        if cur.fetchone():
            break
        else:
            print("ID Maggot tidak ditemukan atau bukan milik Anda.")
    while True:
        id_pembeli = input("ID Pembeli: ").strip()
        if not id_pembeli:
            print("ID Pembeli tidak boleh kosong.")
            continue

        cur.execute("SELECT 1 FROM users WHERE id_user = %s AND role IN ('supplier', 'pembudidaya')", (id_pembeli,))
        if cur.fetchone():
            break
        else:
            print("Pembeli tidak ditemukan.")
    while True:
        jumlah_input = input("Jumlah (kg): ").strip()
        try:
            jumlah = int(jumlah_input)
            if jumlah <= 0:
                print("Jumlah harus lebih besar dari nol.")
                continue
            break
        except ValueError:
            print("Input harus berupa angka.")

    deskripsi = input("Keterangan (opsional): ").strip()

    # Cek stok tersedia
    cur.execute("SELECT jumlah_kg, id_stok_maggot FROM stok_maggot WHERE id_maggot = %s AND status = 'tersedia'", (id_maggot,))
    stok_row = cur.fetchone()

    if stok_row:
        stok_tersedia, id_stok = stok_row
        if stok_tersedia < jumlah:
            print(f"Stok tidak mencukupi. Hanya tersisa {stok_tersedia} kg.")
            cur.close()
            conn.close()
            input("\nTekan Enter untuk kembali...")
            return
    else:
        print("Tidak ada stok tersedia untuk maggot ini.")
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")
        return

    id_transaksi = generate_id("TM", "transaksi_maggot", "id_transaksi_maggot")
    try:
        # Simpan transaksi
        cur.execute("""
            INSERT INTO transaksi_maggot (
                id_transaksi_maggot, id_pembeli, id_maggot, jumlah_kg, deskripsi, status
            ) VALUES (%s, %s, %s, %s, %s, 'diproses')
        """, (id_transaksi, id_pembeli, id_maggot, jumlah, deskripsi))

        # Kurangi stok
        sisa_stok = stok_tersedia - jumlah
        if sisa_stok > 0:
            cur.execute("UPDATE stok_maggot SET jumlah_kg = %s WHERE id_stok_maggot = %s", (sisa_stok, id_stok))
        else:
            cur.execute("DELETE FROM stok_maggot WHERE id_stok_maggot = %s", (id_stok,))

        conn.commit()
        print("Penjualan maggot berhasil dicatat dan stok diperbarui.")
    except Exception as e:
        print(f"Gagal mencatat penjualan: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


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
        headers = ["ID Transaksi", "Jenis", "Jumlah (kg)", "Catatan"]
        table_data = [[row[0], row[1], row[2], row[3]] for row in rows]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
        
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali ke menu...")

# ======== Supplier Things ===========
def tambah_stok(id_user):
    conn = None
    cur = None

    try:
        conn = connect()
        cur = conn.cursor()
        print("\n--- Tambah Stok Sampah Organik ---")

        # Input ID Sampah
        while True:
            id_sampah = input("ID Sampah Organik: ").strip()
            if not id_sampah:
                print("ID Sampah tidak boleh kosong.")
                continue

            cur.execute("SELECT 1 FROM sampah_organik WHERE id_sampah_organik = %s AND id_supplier = %s", (id_sampah, id_user))
            if cur.fetchone():
                break
            else:
                print("ID Sampah tidak ditemukan atau bukan milik Anda.")

        while True:
            jumlah_input = input("Jumlah (kg): ").strip()
            if not jumlah_input:
                print("Jumlah tidak boleh kosong.")
                continue
            try:
                jumlah = int(jumlah_input)
                if jumlah <= 0:
                    print("Jumlah harus lebih besar dari nol.")
                else:
                    break
            except ValueError:
                print("Input harus berupa angka.")

        while True:
            status = input("Status (tersedia/habis): ").strip().lower()
            if status in ['tersedia', 'habis']:
                break
            else:
                print("Status harus 'tersedia' atau 'habis'.")
        id_stok = generate_id("SSO", "stok_sampah_organik", "id_stok_sampah")

        # Eksekusi INSERT
        cur.execute("""
            INSERT INTO stok_sampah_organik 
            (id_stok_sampah, id_sampah_organik, jumlah_kg, status)
            VALUES (%s, %s, %s, %s)
        """, (id_stok, id_sampah, jumlah, status))

        conn.commit()
        print("Stok sampah berhasil ditambahkan.")

    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
        print(f"Terjadi kesalahan pada database: {e}")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error umum: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        input("\nTekan Enter untuk kembali...")


def terima_pesanan(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT ts.id_transaksi_sampah, u.nama_user, so.jenis_sampah, ts.jumlah_kg, ts.status FROM transaksi_sampah_organik ts JOIN sampah_organik so ON ts.id_sampah_organik = so.id_sampah_organik JOIN users u ON ts.id_pembeli = u.id_user WHERE so.id_supplier = %s AND ts.status = 'diproses'", (id_user,))
    rows = cur.fetchall()
    
    if not rows:
        print("Tidak ada pesanan masuk.")
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")
        return

    print("\nPesanan Masuk:")
    for row in rows:
        print(f"ID: {row[0]}, Pembeli: {row[1]}, Jenis: {row[2]}, Jumlah: {row[3]}kg, Status: {row[4]}")

    while True:
        id_pilih = input("Masukkan ID transaksi yang ingin diterima: ").strip()
        if id_pilih:
            break
        print("ID transaksi tidak boleh kosong.")

    cur.execute("UPDATE transaksi_sampah_organik SET status = 'dikirim' WHERE id_transaksi_sampah = %s", (id_pilih,))
    conn.commit()
    print("Transaksi diperbarui menjadi dikirim.")
    cur.close()
    conn.close()
    input("\nTekan Enter untuk kembali...")

def beli_maggot(id_user):
    conn = connect()
    cur = conn.cursor()
    clear_screen()
    print("\n--- Daftar Produk Maggot Tersedia ---")

    # Query Ambil data maggot dengan stok tersedia + harganya
    cur.execute("""
        SELECT m.id_maggot, m.jenis_maggot, m.harga_per_kg, sm.jumlah_kg 
        FROM maggot m
        JOIN stok_maggot sm ON m.id_maggot = sm.id_maggot
        WHERE sm.status = 'tersedia'
          AND sm.jumlah_kg > 0
    """)
    hasil = cur.fetchall()

    if not hasil:
        print("Tidak ada maggot tersedia untuk dibeli.")
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali...")
        return

    headers = ["ID Maggot", "Jenis Maggot", "Harga/kg", "Stok (kg)"]
    table_data = [[row[0], row[1], f"Rp{row[2]}", row[3]] for row in hasil]
    print(tb(table_data, headers=headers, tablefmt="double_grid"))


    while True:
        id_maggot = input("\nMasukkan ID Maggot yang ingin dibeli: ").strip()
        cur.execute("""
            SELECT m.id_maggot, m.jenis_maggot, m.harga_per_kg, sm.jumlah_kg 
            FROM maggot m
            JOIN stok_maggot sm ON m.id_maggot = sm.id_maggot
            WHERE m.id_maggot = %s AND sm.status = 'tersedia' AND sm.jumlah_kg > 0
        """, (id_maggot,))
        maggot = cur.fetchone()
        if maggot:
            break
        else:
            print("ID Maggot tidak ditemukan atau stok habis. Silakan coba lagi.")
            
    while True:
        try:
            jumlah = int(input(f"Jumlah (kg) - Stok tersedia: {maggot[3]} kg: "))
            if 0 < jumlah <= maggot[3]:
                break
            else:
                print(f"Jumlah harus lebih besar dari 0 dan tidak melebihi {maggot[3]} kg.")
        except ValueError:
            print("Input harus berupa angka.")

    deskripsi = input("Keterangan (opsional): ")
    id_transaksi = generate_id("TM", "transaksi_maggot", "id_transaksi_maggot")
    try:
        cur.execute("""
            INSERT INTO transaksi_maggot (
                id_transaksi_maggot, id_pembeli, id_maggot, jumlah_kg, deskripsi, status
            ) VALUES (%s, %s, %s, %s, %s, 'diproses')
        """, (id_transaksi, id_user, id_maggot, jumlah, deskripsi))
        conn.commit()
        total_harga = maggot[2] * jumlah
        print(f"\nPembelian berhasil dicatat!")
        print(f"Total harga: Rp{total_harga}")
    except Exception as e:
        conn.rollback()
        print(f"Gagal mencatat pembelian: {e}")
    finally:
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali ke menu...")

def riwayat_penjualan(id_user):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT ts.id_transaksi_sampah, so.jenis_sampah, ts.jumlah_kg, ts.deskripsi 
        FROM transaksi_sampah_organik ts
        JOIN sampah_organik so ON ts.id_sampah_organik = so.id_sampah_organik 
        WHERE so.id_supplier = %s AND ts.status = 'diproses'
    """, (id_user,))
    
    rows = cur.fetchall()
    clear_screen()
    print("\nRiwayat Penjualan Sampah:")
    
    if not rows:
        print("Belum ada riwayat penjualan.")
    else:
        headers = ["ID Transaksi", "Jenis Sampah", "Jumlah (kg)", "Catatan"]
        table_data = [[row[0], row[1], f"{row[2]} kg", row[3]] for row in rows]
        print(tb(table_data, headers=headers, tablefmt="double_grid"))
    
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
[4] Profil 
[5] Logout
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
                profile(admin['id_user'])
            case '5':
                main()
                return
            case _:
                print("Pilihan tidak valid.")

def menu_pembudidaya(id_user):
    while True:
        clear_screen()
        print("""
[1] Menu Maggot
[2] Menu Sampah Organik
[3] Riwayat Penjualan Maggot
[4] Riwayat Pembelian Sampah
[5] Profile
[0] Logout
    """)
        pilihan = input("Masukkan pilihan: ")
        match pilihan:
            case '1':
                while True:
                    clear_screen()
                    print("""
Menu Maggot:
[1] Tambah Stok Maggot
[2] Lihat Stok Maggot
[3] Jual Maggot
[0] Kembali ke Menu Utama
                    """)
                    pilihan_maggot = input("Masukkan pilihan: ")

                    match pilihan_maggot:
                        case '1':
                            tambah_stok_maggot(id_user)
                        case '2':
                            lihat_stok_maggot(id_user)
                        case '3':
                            jual_maggot(id_user)
                        case '0':
                            break
                        case _:
                            print("Pilihan tidak valid.")
            case '2':
                while True:
                    clear_screen()
                    print("""
Menu Sampah Organik:
[1] Lihat Stok Sampah
[2] Beli Sampah Organik
[0] Kembali ke Menu Utama
                    """)
                    pilihan_sampah = input("Masukkan pilihan: ")

                    match pilihan_sampah:
                        case '1':
                            lihat_stok_sampah_dibeli()
                        case '2':
                            beli_sampah_organik(id_user)
                        case '0':
                            break
                        case _:
                            print("Pilihan tidak valid.")
            case '3':
                riwayat_transaksi_pembelian(id_user)
            case '4':
                riwayat_transaksi_pembelian(id_user)
            case '5':
                profile(id_user)
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
[1] Menu Maggot
[2] Menu Sampah Organik
[3] Riwayat Penjualan Sampah
[4] Riwayat Pembelian Maggot
[0] Logout
        """)
            pilihan = input("Masukkan pilihan: ")
            match pilihan:
                case '1':
                    while True:
                        clear_screen()
                        print("""
Menu Maggot:
[1] Beli Maggot
[2] Riwayat Pembelian Maggot
[0] Kembali ke Menu Utama
                        """)
                        pilihan_maggot = input("Masukkan pilihan: ")

                        match pilihan_maggot:
                            case '1':
                                beli_maggot(id_user)
                            case '2':
                                riwayat_pembelian(id_user)
                            case '0':
                                break
                            case _:
                                print("Pilihan tidak valid.")
                case '2':
                    while True:
                        clear_screen()
                        print("""
Menu Sampah Organik:
[1] Tambah Stok Sampah
[2] Lihat Stok Sampah
[3] Terima Pesanan Sampah
[0] Kembali ke Menu Utama
                        """)
                        pilihan_sampah = input("Masukkan pilihan: ")

                        match pilihan_sampah:
                            case '1':
                                tambah_stok(id_user)
                            case '2':
                                lihat_stok_sampah(id_user)
                            case '3':
                                terima_pesanan(id_user)
                            case '0':
                                break
                            case _:
                                print("Pilihan tidak valid.")
                case '3':
                    riwayat_penjualan(id_user)
                case '4':
                    riwayat_pembelian(id_user)
                case '0':
                    main()
                    return
                case _:
                    print("Pilihan tidak valid.")

#========================= UPDATE ATAS !!============================
def main():
    clear_screen()
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
        pilihan = input("Masukkan pilihan [1,2,3] : ").strip()
        match pilihan:
            case '1':
                clear_screen()
                print("Login sebagai :")
                print("[1] User (Pembudidaya / Supplier)")
                print("[2] Admin")
                pilih = input("Masukkan pilihan login : ").strip()
                if pilih == "1":
                    clear_screen()
                    user = login_user()
                    if user:
                        if user['role'] == 'pembudidaya':
                            menu_pembudidaya(user['id_user'])
                        elif user['role'] == 'supplier':
                            menu_supplier(user['id_user'])
                elif pilih == "2":
                    clear_screen()
                    admin = login_admin()
                    if admin:
                        menu_admin(admin)
                else:
                    print("Tidak ada pilihan")
            case '2':
                print("Register sebagai  ")
                print("[1] Pembudidaya")
                print("[2] Supplier")
                reg_pilihan = input("Pilih Register : ").strip()
                if reg_pilihan == '1':
                    register_pembudidaya()
                elif reg_pilihan == '2':
                    register_supplier()
                else:
                    print("Tidak ada pilihan")
            case '3':
                print("Kamu memilih keluar.")
                break
            case _:
                print("Pilihan tidak ada")
        input("\nTekan Enter untuk kembali...")

main()