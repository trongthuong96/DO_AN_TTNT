import cv2
import numpy as np
import os
from PIL import Image

class trainning_face:

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    def save_train(self):

        # Duong dan den file anh
        path = "image_db/"

        faces, mssvs = self.getImageWithMSSV(path)

        if (mssvs == []) :
            pass

        else:
            self.recognizer.train(faces, np.array(mssvs))

            if not os.path.exists('recognizer'):
                os.makedirs('recognizer')

            self.recognizer.save('recognizer/trainning.yml')

    # ham lay duong dan tat ca anh
    def getImageWithMSSV(sefl,path):
        global MSSV, faceNp
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

        faces = []
        MSSVS = []

        # du lieu cho vao mang
        for imagePath in imagePaths:
            faceImg = Image.open(imagePath).convert('L')

            faceNp = np.array(faceImg, 'uint8')

            MSSV = int(imagePath.split('/')[1].split('.')[1])

            faces.append(faceNp)
            MSSVS.append(MSSV)

        return faces, MSSVS