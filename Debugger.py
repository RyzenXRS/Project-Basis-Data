import psycopg2
def connect():
    return psycopg2.connect(
        host="localhost",
        database="MaggottPY",
        user="postgres",
        password="321"
    )

def tambah_stok_maggot(id_user):
    conn = connect()
    cur = conn.cursor()

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

    id_stok = generate_id("SM", "stok_maggot", "id_stok_maggot")
    id_maggot = input("Pilih ID Maggot dari daftar di atas: ")

    cur.execute("SELECT 1 FROM maggot WHERE id_maggot = %s AND id_pembudidaya = %s", (id_maggot, id_user))
    if not cur.fetchone():
        print(f"ID Maggot {id_maggot} tidak ditemukan atau bukan milik Anda.")
        cur.close()
        conn.close()
        return

    jumlah = int(input("Jumlah (kg): "))
    status = input("Status (tersedia/habis): ")

    cur.execute("""
        INSERT INTO stok_maggot (id_stok_maggot, id_maggot, jumlah_kg, status)
        VALUES (%s, %s, %s, %s)
    """, (id_stok, id_maggot, jumlah, status))

    conn.commit()
    cur.close()
    conn.close()
    print("Stok maggot berhasil ditambahkan.")