from setting import *

def connectDB():
    conn = mysql.connector.connect(
        user='root', 
        password='', 
        host='localhost', 
        database='garagedb'
    )
    return conn

def insertDB(id, number_plate):
    conn = connectDB()
    curror = conn.cursor()
    image_data = convert_to_binary_data('number_plate.jpg') 
    sql = """INSERT INTO user (Id, Picture, Number_plate, Date_in, Status) VALUES (%s, %s, %s, %s, %s)"""
    now = datetime.datetime.now()
    date_in = now.strftime("%Y/%m/%d %H:%M:%S")
    data_tuple = (id, image_data, number_plate, date_in, '1')
    curror.execute(sql, data_tuple)
    conn.commit()
    curror.close()
    conn.close()
    print("VAO BAI GUI XE")
    print("Ngay gio vao : " + date_in)

def udpdateDB(id):
    """Cập nhật trạng thái và thời gian ra khỏi bãi xe."""
    conn = connectDB()  # Kết nối đến cơ sở dữ liệu
    cursor = conn.cursor()
    # Chỉnh sửa tên cột ở đây nếu cần thiết
    sql = "UPDATE user SET Status = %s, Date_out = %s, Price = %s WHERE Id = %s"
    now = datetime.datetime.now()
    date_out = now.strftime("%Y/%m/%d %H:%M:%S")
    kind = get_vehicle_kind(id)
    price = PRICES[kind]
    if kind == 'car':
        date_in = select_datein(id)
        duration = now - date_in
        price = duration.total_seconds() / 3600 * price  # Calculate price based on hours
    cursor.execute(sql, ('0', date_out, price, id))  # Thực hiện câu lệnh SQL
    # Kiểm tra xem có bản ghi nào được cập nhật không
    if cursor.rowcount > 0:
        conn.commit()  # Lưu thay đổi vào cơ sở dữ liệu
        print("RA KHOI BAI XE")
        print("Ngay gio ra : " + date_out)
    else:
        print(f"Không tìm thấy bản ghi với ID: {id}. Không có bản ghi nào được cập nhật.")

    cursor.close()
    conn.close()
    

def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:  # Mở file ảnh ở chế độ 'rb' (read binary)
        binary_data = file.read()  # Đọc dữ liệu nhị phân từ ảnh
    return binary_data

def get_vehicle_kind(id):
    if id[0:3] == 'CA':
        return 'car'
    elif id[0:2] == 'MT':
        return 'motorbike'
    else:
        return 'bicycle'

def check_number_plate(number_plate):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Number_plate FROM user"
    cursor.execute(sql)
    rows = cursor.fetchall()
    if number_plate in [row[0] for row in rows]:
        return True
    cursor.close()
    conn.close()
    return False

def checkStatus(id):
    conn = connectDB()
    cursor = conn.cursor()
    st = "SELECT Status FROM user WHERE Id = %s"
    cursor.execute(st, (id,))
    status = cursor.fetchone()
    cursor.close()
    conn.close()
    return status[0]

def udpdatenumber(number, kind):
    conn = connectDB()
    curror = conn.cursor()
    sql = "UPDATE vehicles SET number = %s WHERE vehicle = %s"
    curror.execute(sql, (number, kind))
    conn.commit()
    curror.close()
    conn.close()

def number_vehicles(kind):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT number FROM vehicles WHERE vehicle = %s"
    cursor.execute(sql, (kind,))
    number = cursor.fetchone()
    return number[0]

def select_id():
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Id FROM user"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]

def select_id_plate(number_plate):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Id FROM user WHERE Number_plate = %s"
    cursor.execute(sql, (number_plate,))
    id = cursor.fetchone()
    return id[0]

def select_datein(id):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Date_in FROM user WHERE Id = %s"
    cursor.execute(sql, (id,))
    date_in = cursor.fetchone()
    return date_in[0]

def select_dateout(id):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Date_out FROM user WHERE Id = %s"
    cursor.execute(sql, (id,))
    date_out = cursor.fetchone()
    return date_out[0]

def select_number_plate(id):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Number_plate FROM user WHERE Id = %s"
    cursor.execute(sql, (id,))
    number_plate = cursor.fetchone()
    return number_plate[0]

def select_price(id):
    conn = connectDB()
    cursor = conn.cursor()
    sql = "SELECT Price FROM user WHERE Id = %s"
    cursor.execute(sql, (id,))
    price = cursor.fetchone()
    return price[0]

