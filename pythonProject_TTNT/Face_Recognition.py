import cv2
import os
import unidecode

class Face_Recognition:
    def recognition(self):

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        recognizer.read("recognizer/trainning.yml")

        def getProfile(mssv):

            conn = self.connect()
            cur = conn.cursor()
            cur.execute("select mssv, name from sinhvien where mssv = " + str(mssv))

            profile = None

            for row in cur:
                profile = row
                # print(row)

            conn.close()
            return profile

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        fontface = cv2.FONT_HERSHEY_COMPLEX

        while (self.cap.isOpened()):
            ret, frame = self.cap.read()

            if ret == True:

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                    roi_gray = gray[y:y + h, x:x + w]

                    mssv, self.confidence = recognizer.predict(roi_gray)


                # print("ngoài",mssv)
                # print(self.confidence)
                if self.confidence < 40:

                    profile = getProfile(mssv)

                    # print(profile)

                    if (profile != None):
                        cv2.putText(frame, "Mssv: " + unidecode.unidecode(str(profile[0])), (x - 15, y + h + 30), fontface, 0.6, (255, 0, 0), 2)
                        cv2.putText(frame, "Name: " + unidecode.unidecode(str(profile[1])), (x - 40, y + h + 60), fontface, 0.6, (255, 0, 0), 2)

                    if self.number == 2:
                        self.diemdanh_sv(str(profile[0]), self.ca)
                        flag = 0
                        for i in range(len(self.mssv)):
                            if self.mssv[i][0] == profile[0]:
                                flag = 1

                        if flag == 1:
                            cv2.putText(frame, "Da diem danh", (x, y + h + 90),fontface, 0.6, (0, 0, 255), 2)
                        else:
                            cv2.putText(frame, "Lop khong co ban nay!", (x - 40, y + h + 90), fontface, 0.6, (0, 0, 255), 2)

                if self.confidence > 40:
                    cv2.putText(frame, "Unknown", (x, y + h + 30), fontface, 0.6, (255, 0, 0), 2)

                if self.confidence > 50:
                    if (self.logic == 1):

                        # Tạo folder lưu ảnh nếu chưa có
                        if not os.path.exists("image_db"):
                            os.makedirs("image_db")

                        self.value = self.value + 1
                        # lưu ảnh chụp vào folder trên
                        # cv2.imwrite("image_db/user." + self.lineEdit_class.text() + "/User." + self.lineEdit_mssv.text() + "." + str(self.value) + ".jpg", gray[y:y + h, x:x + w])

                        cv2.imwrite("image_db/User." + self.lineEdit_mssv.text() + "." + str(self.value) + ".jpg", gray[y:y + h, x:x + w])

                        self.logic = 0

                self.displayImage(frame, self.number)
                cv2.waitKey()
