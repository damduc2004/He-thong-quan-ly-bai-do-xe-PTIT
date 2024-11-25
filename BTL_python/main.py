from setting import *
from mySql import *
from Preprocess import *
from camera_check import *
from PyQt6 import QtWidgets, QtCore, QtGui, uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt
from PyQt6.uic import loadUi

import sys
# setnumber
NUMBER_VEHICLES['car'] = number_vehicles('car')
NUMBER_VEHICLES['motorbike'] = number_vehicles('motorbike')
NUMBER_VEHICLES['bicycle'] = number_vehicles('bicycle')
lst_id = select_id()
lst_id = select_id()
id_car = max([int(id[2:]) for id in lst_id if id[0:2] == 'CA'], default=0)
id_motor = max([int(id[2:]) for id in lst_id if id[0:2] == 'MT'], default=0)
id_bicycle = max([int(id[2:]) for id in lst_id if id[0:2] == 'BC'], default=0)
# database
def checkPicture(id):
    conn = connectDB()
    cursor = conn.cursor()
    pc = "SELECT Picture FROM user WHERE Id = %s"

    status = checkStatus(id)
    if status == '0': return False
    # check picture
    cursor.execute(pc, (id,))
    picture = cursor.fetchone()  # Lấy dữ liệu từ cột 'Picture'

    if picture is not None and picture[0] is not None:  # Kiểm tra dữ liệu hợp lệ
        image_data = np.frombuffer(picture[0], dtype=np.uint8) #Chuyển đổi dữ liệu nhị phân thành mảng numpy
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)  # Giải mã thành ảnh

        if image is not None:
            cv2.imshow("Image", image)  # Hiển thị ảnh
            if cv2.waitKey(0) == ord('q'):  # Nhấn 'q' để thoát
                cv2.destroyAllWindows()  # Đóng cửa sổ chỉ khi nhấn 'q'
        else:
            QMessageBox.information('Error', 'Không thể hiển thị ảnh.')
    else:
        return False

    cursor.close()
    conn.close()
    return True

# creater id
def creater_id(kind):
    global id_car, id_motor, id_bicycle
    if kind == 'car':
        id_car += 1
        return 'CA' + '{:03d}'.format(id_car)
    elif kind == 'motorbike':
        id_motor += 1
        return 'MT' + '{:03d}'.format(id_motor)
    else:
        id_bicycle += 1
        return 'BC' + '{:03d}'.format(id_bicycle)

def get_vehicle_kind(id):
    if id[0:3] == 'CA':
        return 'car'
    elif id[0:2] == 'MT':
        return 'motorbike'
    else:
        return 'bicycle'

class Main_w(QMainWindow):
    def __init__(self):
        super(Main_w, self).__init__()
        uic.loadUi("form_main.ui", self)
        self.listView = self.findChild(QListView, 'listView')
        self.show_garage()
        self.them_xe.clicked.connect(self.them)
        self.kiem_tra.clicked.connect(self.kiemtra)
        self.thu_nhap.clicked.connect(self.thuNhap)
        self.exit.clicked.connect(self.quit)

    def show_garage(self):
        conn = connectDB()
        cursor = conn.cursor()
        sql = "SELECT * FROM vehicles"
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.number_car.setText(f"{rows[0][1]} : {rows[0][2]}")
        self.number_moto.setText(f"{rows[1][1]} : {rows[1][2]}")
        self.number_bicycle.setText(f"{rows[2][1]} : {rows[2][2]}")
        cursor.close()
        conn.close()

    def thuNhap(self):
        conn = connectDB()
        cursor = conn.cursor()
        sql = "SELECT Price FROM user"
        cursor.execute(sql)
        income = sum([row[0] for row in cursor.fetchall()])
        self.listWidget.addItem(f'/// THU NHAP: {str(income)} VND')
        cursor.close()
        conn.close()

    def them(self):
        widget.setCurrentIndex(1)
    def kiemtra(self):
        widget.setCurrentIndex(2)

    def quit(self):
        if QMessageBox.question(self, 'Quit', 'Bạn có muốn rời khỏi hệ thống', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            sys.exit()

class Them_w(QMainWindow):
    def __init__(self):
        super(Them_w, self).__init__()
        uic.loadUi("form_them.ui", self)
        # Kết nối signal của QRadioButton với hàm xử lý
        self.choice_car.toggled.connect(lambda checked: self.stateChangeRadio(self.choice_car))
        self.choice_moto.toggled.connect(lambda checked: self.stateChangeRadio(self.choice_moto))
        self.choice_bicycle.toggled.connect(lambda checked: self.stateChangeRadio(self.choice_bicycle))
        # Kết nối nút "Bắt đầu" với hàm start_camera
        self.start.clicked.connect(self.start_camera)
        self.stop.clicked.connect(self.stop_camera)
        # Ket noi nut "Them" voi ham insert
        self.insert.clicked.connect(self.Insert)
        # Kết nối nút "Thoát" với hàm quit
        self.thoat.clicked.connect(self.quit)
        self.cap, self.timer = None, QTimer()
        self.timer.timeout.connect(self.update_frame)
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.result_label.setText("Error: Unable to access camera")
            return
        self.timer.start(30)
    
    def stop_camera(self):
        if self.cap:
            ret, frame = self.cap.read()
            cv2.imwrite("number_plate.jpg", frame)
            self.cap.release()
            cv2.destroyAllWindows()
        self.timer.stop()
        self.video_label.clear()
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            plate, img= process_frame(frame)
            self.result_label.setText(f"Detected: {plate}" if plate else "No Plate Detected")
            self.nplate = plate
            self.select_nb.setText(self.nplate)
            rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.video_label.setPixmap(QPixmap.fromImage(QImage(rgb_frame.data, *rgb_frame.shape[1::-1],
                                                                rgb_frame.shape[2] * rgb_frame.shape[1],
                                                                QImage.Format.Format_RGB888)))
    def stateChangeRadio(self, button):
        if button.isChecked():
            self.kind = button.text().lower()
            self.id = creater_id(self.kind)
    
    def reset_radio_buttons(self):
        self.choice_car.setAutoExclusive(False)
        self.choice_car.setChecked(False)
        self.choice_car.setAutoExclusive(True)

        self.choice_moto.setAutoExclusive(False)
        self.choice_moto.setChecked(False)
        self.choice_moto.setAutoExclusive(True)

        self.choice_bicycle.setAutoExclusive(False)
        self.choice_bicycle.setChecked(False)
        self.choice_bicycle.setAutoExclusive(True)
    
    def Insert(self):
        insertDB(self.id, self.nplate)
        NUMBER_VEHICLES[self.kind] +=1
        udpdatenumber(NUMBER_VEHICLES[self.kind], self.kind)
        QMessageBox.information(self, 'Success', 'Xe đã được thêm vào bãi gửi.')
        Main_f.show_garage()
        Main_f.listWidget.addItem(f"/// {self.id} : {self.nplate} : XE VÀO BÃI GỬI")
        self.reset_radio_buttons()
    def quit(self):
        widget.setCurrentIndex(0)  # Giả định rằng widget là một QStackedWidget được định nghĩa bên ngoài.


class KiemTra_w(QMainWindow):
    def __init__(self):
        super(KiemTra_w, self).__init__()
        uic.loadUi("form_kiemtra.ui", self)
        # Kết nối nút "Camera" với hàm Camera
        self.start.clicked.connect(self.start_camera)
        self.stop.clicked.connect(self.stop_camera)
        # Kết nối nút "Thoát" với hàm quit
        self.thoat_check.clicked.connect(self.Quit)
        # Kết nối nút hoặc sự kiện lấy giá trị ID từ QTextEdit
        self.check_id.clicked.connect(self.Check_id)
        # Kết nối nút hoặc sự kiện lấy giá trị biển số từ QTextEdit
        self.check_plate.clicked.connect(self.Check_plate)
        self.cap, self.timer = None, QTimer()
        self.timer.timeout.connect(self.update_frame)
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.result_label.setText("Error: Unable to access camera")
            return
        self.timer.start(30)
    
    def stop_camera(self):
        if self.cap:
            ret, frame = self.cap.read()
            cv2.imwrite("number_plate.jpg", frame)
            self.cap.release()
            cv2.destroyAllWindows()
        self.timer.stop()
        self.video_label.clear()
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            plate, img= process_frame(frame)
            self.result_label.setText(f"Detected: {plate}" if plate else "No Plate Detected")
            self.nplate = plate
            self.text_np.setText(self.nplate)
            rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.video_label.setPixmap(QPixmap.fromImage(QImage(rgb_frame.data, *rgb_frame.shape[1::-1],
                                                                rgb_frame.shape[2] * rgb_frame.shape[1],
                                                                QImage.Format.Format_RGB888)))

    def Check_id(self):
        # Lấy nội dung từ QTextEdit và chuyển thành chữ hoa
        self.id = self.text_id.toPlainText().upper()

        # Kiểm tra ID
        if self.id in select_id():
            if checkPicture(self.id):
                # Cập nhật cơ sở dữ liệu và thông tin
                udpdateDB(self.id)
                NUMBER_VEHICLES[get_vehicle_kind(self.id)] -= 1
                udpdatenumber(NUMBER_VEHICLES[get_vehicle_kind(self.id)], get_vehicle_kind(self.id))

                # Hiển thị thông tin xe
                message = f"""{self.id} : XE RA KHOI BAI GUI
Biển số: {select_number_plate(self.id)}                     
Giờ vào: {select_datein(self.id)}                       
Giờ ra:  {select_dateout(self.id)} 
Giá: {select_price(self.id)} VND                     
"""
                QMessageBox.information(self, 'Success', message)
                Main_f.show_garage()
                Main_f.listWidget.addItem(f"""///
{message}///""")
            else:
                QMessageBox.information(self, 'Error', 'Xe không có trong bãi gửi.')
        else:
            QMessageBox.information(self, 'Error', 'Xe không có trong bãi gửi.')
    
    def Check_plate(self):
        self.nplate = self.text_np.text().upper()
        if check_number_plate(self.nplate) and checkStatus(select_id_plate(self.nplate)) == '1':
            id = select_id_plate(self.nplate)
            udpdateDB(self.id)
            NUMBER_VEHICLES[get_vehicle_kind(self.id)] -= 1
            udpdatenumber(NUMBER_VEHICLES[get_vehicle_kind(self.id)], get_vehicle_kind(self.id))
             # Hiển thị thông tin xe
            message = f"""{id} : XE RA KHOI BAI GUI
Biển số: {select_number_plate(id)}                     
Giờ vào: {select_datein(id)}                       
Giờ ra:  {select_dateout(id)}                      
Giá: {select_price(id)} VND                     
"""
            QMessageBox.information(self, 'Success', message)
            Main_f.show_garage()
            Main_f.listWidget.addItem(f"""///
{message}///""")
        else:   
            QMessageBox.information(self, 'Error', 'Xe không có trong bãi gửi.')

    def Quit(self):
        widget.setCurrentIndex(0)  # Chuyển về màn hình chính

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()

Main_f = Main_w()
Them_f = Them_w()
KiemTra_f = KiemTra_w()
Main_f.setWindowTitle("Main")
Them_f.setWindowTitle("Them")
KiemTra_f.setWindowTitle("KiemTra")
widget.addWidget(Main_f)
widget.addWidget(Them_f)
widget.addWidget(KiemTra_f)
widget.show()
app.exec()