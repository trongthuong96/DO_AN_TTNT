import sys
import os
import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox
import connect_db
import trainning_face
import Face_Recognition
from numpy import copy

class AppClone(QWidget, connect_db.connect_db):

    classcode = None
    def __init__(self, classcode):
        super().__init__()
        self.title = 'Điểm Danh'
        self.left = 300
        self.top = 30
        self.width = 640
        self.height = 600
        self.classcode = classcode
        print(classcode)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # Show widget
        self.show()

    def createTable(self):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(6)

        text = self.xuatfile(self.classcode) #self.lineEdit_class_2.text()
        self.tableWidget.setRowCount(len(text))

        for j in range(0, len(text)):
            for i in range(0, 6):
                self.tableWidget.setItem(j, i, QTableWidgetItem(text[j][i]))

class tehseencode(QDialog,trainning_face.trainning_face, Face_Recognition.Face_Recognition, connect_db.connect_db):
    cap = None
    flag = 0

    def __init__(self):
        super(tehseencode, self).__init__()
        loadUi("designer1.ui", self)

        self.w = None  # No external window yet.

        self.logic = 0
        self.value = 0
        self.number = 0
        self.confidence = None
        self.ca = None
        self.mssv = None
        self.action_train = None

        # sự kiện nút
        self.pushButton_start.clicked.connect(self.button_start)
        self.pushButton_start1.clicked.connect(self.button_start_1)
        self.pushButton_AddStudent.clicked.connect(self.CaptureClicked)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_stop_2.clicked.connect(self.stop)
        self.pushButton_file.clicked.connect(self.xuat)
        # self.lineEdit_class_2.text()

        # Làm mờ nút
        self.pushButton_AddStudent.setEnabled(False)
        self.pushButton_DeleteStudent.setEnabled(False)
        self.lineEdit_name.setEnabled(False)
        self.lineEdit_mssv.setEnabled(False)
        self.lineEdit_class.setEnabled(False)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_stop_2.setEnabled(False)

    @pyqtSlot()

    def xuat(self):
        # self.xuatfile(self.lineEdit_class_2.text())

        if self.w is None:
            self.w = AppClone(self.lineEdit_class_2.text())
            self.w.show()

        else:
            # self.w.close()  # Close window.
            self.w = None


            # Chức năng nút start của màn hình thêm xóa

    def button_start(self):

        #Hiện, Ẩn nút
        self.pushButton_stop.setEnabled(True)
        self.pushButton_AddStudent.setEnabled(True)
        self.pushButton_DeleteStudent.setEnabled(False)
        self.lineEdit_name.setEnabled(True)
        self.lineEdit_mssv.setEnabled(True)
        self.lineEdit_class.setEnabled(True)
        self.pushButton_start.setEnabled(False)
        self.pushButton_start1.setEnabled(False)
        self.number = 1
        if not os.path.isfile("recognizer/trainning.yml"):
            self.onClicked()
        else:
            self.recognition()

    # Chức năng nút start của màn hình điểm danh
    def button_start_1(self):

        # Hiện, Ẩn nút
        self.number = 2
        if not os.path.isfile("recognizer/trainning.yml"):
            self.onClicked()
        else:
            flag, self.mssv = self.upclassdiemdanh(self.lineEdit_class_2.text())
            self.ca = flag
            # print(self.mssv)

            # Thông báo khi không nhập, hoặc nhập sai mã lớp
            if self.mssv == None:
                msg = QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Vui lòng nhập đúng mã Lớp cần điểm danh.")
                x = msg.exec_()

            if flag != 0:
                self.pushButton_file.setEnabled(False)
                self.pushButton_stop_2.setEnabled(True)
                self.pushButton_start.setEnabled(False)
                self.pushButton_start1.setEnabled(False)
                self.label_class_2.setEnabled(False)
                self.lineEdit_class_2.setEnabled(False)
                self.recognition()

    # Liên kết đến file train để trainning ảnh thành dữ liệu hiểu
    def train(self):
        self.save_train()
        msg = QMessageBox()
        msg.setWindowTitle("Infomations")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Đã Thêm.")
        x = msg.exec_()

    # Mở camera khi chưa có file recognizer và có chức năng chụp ảnh
    def onClicked(self):
        
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        while (self.cap.isOpened()):
            ret, frame = self.cap.read()

            if ret == True:

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                fontface = cv2.FONT_HERSHEY_COMPLEX
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                    cv2.putText(frame, str("Unknow"), (x + 10, y + h + 30), fontface, 0.6, (255, 0, 0), 2)

                self.displayImage(frame, self.number)

                cv2.waitKey()
                if (self.logic == 1):

                    # Tạo folder lưu ảnh nếu chưa có
                    if not os.path.exists("image_db"):
                        os.makedirs("image_db")

                    '''
                    if not os.path.exists("image_db/user."+ self.lineEdit_class.text()):
                        os.makedirs("image_db/user."+ self.lineEdit_class.text())
                    self.value = self.value + 1
                    '''
                    self.value = self.value + 1
                    # lưu ảnh chụp vào folder trên
                    # cv2.imwrite("image_db/user." + self.lineEdit_class.text() + "/User." + self.lineEdit_mssv.text() + "." + str(self.value) + ".jpg", gray[y:y + h, x:x + w])

                    cv2.imwrite("image_db/User." + self.lineEdit_mssv.text() + "." + str(self.value) + ".jpg", gray[y:y + h, x:x + w])

                    self.logic = 0

            else:
                print('not found')
                self.cap.release()
                cv2.destroyAllWindows()

    ''' '''
    # HIển thị ảnh lên label
    def displayImage(self, img, window):
        img = copy(img)
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if (img.shape[2]) == 4:
                qformat = QImage.Format_RGBA888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()

        if window == 1:
            self.label_camera_1.setPixmap(QPixmap.fromImage(img))
            self.label_camera_1.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        if window == 2:
            self.label_camera_2.setPixmap(QPixmap.fromImage(img))
            self.label_camera_2.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

    # Chụp và lưu thông tin sinh viên vào csdl
    def CaptureClicked(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setIcon(QMessageBox.Warning)

        if not os.path.isfile("recognizer/trainning.yml"):
            self.confidence = 100

        if self.lineEdit_name.text() == "" or self.lineEdit_mssv.text() == "" or self.lineEdit_class.text() == "" or self.confidence < 42:
            msg.setText("Chưa có mssv, tên sv, lớp hoặc đã có mặt người này")
            x = msg.exec_()

        elif self.lineEdit_mssv.text().isdigit() == False:
            msg.setText("Vui lòng nhập số cho mssv.")
            x = msg.exec_()

        elif not os.path.isfile("recognizer/trainning.yml") or (os.path.isfile("recognizer/trainning.yml") and self.confidence > 45):
            if self.lineEdit_name.text() != "" and self.lineEdit_mssv.text() != "" and self.lineEdit_class.text() !="":

                data = self.check(self.lineEdit_mssv.text())

                if self.lineEdit_mssv.text() == data:
                    msg.setText("Đã có mã sinh viên này. Vui lòng nhập lại.")
                    x = msg.exec_()

                else:

                    self.lineEdit_name.setEnabled(False)
                    self.lineEdit_mssv.setEnabled(False)
                    self.lineEdit_class.setEnabled(False)
                    self.logic = 1

                    self.flag = self.flag + 1

                    if self.flag > 10:
                        self.flag = 0

                        self.upsinhvien(self.lineEdit_mssv.text(),self.lineEdit_name.text(),self.lineEdit_class.text())

                        self.lineEdit_name.setEnabled(True)
                        self.lineEdit_mssv.setEnabled(True)
                        self.lineEdit_class.setEnabled(True)
                        self.action_train = 1
                        msg.setWindowTitle("Infomations")
                        msg.setIcon(QMessageBox.Information)
                        msg.setText("Thêm thành công.")
                        x = msg.exec_()

    #kết thúc chương trình
    def closeEvent(self):
        if self.number == 1 or self.number == 2:
           self.cap.release()
           cv2.destroyAllWindows()
           sys.exit(app.exec_())
        else:
            sys.exit(app.exec_())

    # Chức năng nút stop
    def stop(self):

        self.pushButton_start.setEnabled(True)
        self.pushButton_start1.setEnabled(True)

        if self.number == 1:
            self.pushButton_AddStudent.setEnabled(False)
            self.pushButton_DeleteStudent.setEnabled(False)
            self.lineEdit_name.setEnabled(False)
            self.lineEdit_mssv.setEnabled(False)
            self.lineEdit_class.setEnabled(False)

        self.cap.release()
        cv2.destroyAllWindows()

        if self.number == 1:
            self.label_camera_1.clear()
            if self.action_train == 1:
                self.train()
            self.pushButton_stop.setEnabled(False)

        else:
            self.label_camera_2.clear()
            self.pushButton_stop_2.setEnabled(False)
            self.label_class_2.setEnabled(True)
            self.lineEdit_class_2.setEnabled(True)
            self.pushButton_file.setEnabled(True)


app = QApplication(sys.argv)
Window = tehseencode()
Window.show()
sys.exit(app.exec_())
