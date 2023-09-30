import sys
import requests
import time
import http.client
import hashlib
import urllib
import random
import json
import openai
import cv2
import pytesseract
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qt_material import apply_stylesheet

import translator
import preprocess
import ToRoman

class PhotoLabel(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n 拖入图片 \n\n')
        self.setStyleSheet('''
        QLabel {
            border: 4px dashed #aaa;
        }''')

    def setPixmap(self, *args, **kwargs):
        super().setPixmap(*args, **kwargs)
        self.setStyleSheet('''
        QLabel {
            border: none;
        }''')


class Template(QWidget):

    def __init__(self):
        super().__init__()
        self.photo = PhotoLabel()
        btn = QPushButton('Browse')
        btn.clicked.connect(self.open_image)

        self.lineEdit_result = QLineEdit()
        self.lineEdit_result.setText("")
        self.lineEdit_result.setStyleSheet("color: rgb(255,255,255)")

        self.jpn = QLineEdit()
        self.jpn.setStyleSheet("color: rgb(255,255,255)")

        self.roman = QLineEdit()
        self.roman.setStyleSheet("color: rgb(255,255,255)")

        read_local_vert = QPushButton('本地竖版')
        read_local_vert.clicked.connect(self.read_local_vert)

        read_local_horizontal = QPushButton('本地横版')
        read_local_horizontal.clicked.connect(self.read_local_horizontal)

        read_copy_horizontal = QPushButton('粘贴横版')
        read_copy_horizontal.clicked.connect(self.read_copy_horizontal)

        read_copy_vert = QPushButton('粘贴竖版')
        read_copy_vert.clicked.connect(self.read_copy_vert)

        youdao = QPushButton('youdao')
        youdao.clicked.connect(self.YOUDAOtranslate)
        baidu = QPushButton('baidu')
        baidu.clicked.connect(self.BAIDUtranslate)
        gpt = QPushButton('gpt')
        gpt.clicked.connect(self.GPTtranslate)

        grid = QGridLayout(self)
        grid.addWidget(self.lineEdit_result, 6, 0, 1, 4)
        grid.addWidget(self.roman, 7, 0, 1, 4)
        grid.addWidget(youdao, 5, 0, 1, 1)
        grid.addWidget(baidu, 5, 1, 1, 1)
        grid.addWidget(gpt, 5, 2, 1, 1)

        grid.addWidget(self.jpn, 4, 0, 1, 4)

        grid.addWidget(read_local_vert, 2, 0, 2, 1)

        grid.addWidget(read_local_horizontal, 1, 0, 2, 1)

        grid.addWidget(read_copy_horizontal, 1, 3, 2, 1)

        grid.addWidget(read_copy_vert, 2, 3, 2, 1)

        grid.addWidget(btn, 0, 1, 1, 2, Qt.AlignHCenter)

        grid.addWidget(self.photo, 1, 1, 3, 2)

        self.setAcceptDrops(True)
        self.resize(300, 300)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            filename = event.mimeData().urls()[0].toLocalFile()
            event.accept()
            self.open_image(filename)
        else:
            event.ignore()

    def open_image(self, filename=None):
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
            if not filename:
                return
        self.photo.setPixmap(QPixmap(filename))
        QPixmap(filename).save("input.png")

    def read_copy_vert(self):
        self.readcopy()
        self.read_local_vert()

    def read_copy_horizontal(self):
        self.readcopy()
        self.read_local_horizontal()

    def readcopy(self):
        from PIL import Image, ImageGrab
        import cv2
        # 保存剪切板内图片
        im = ImageGrab.grabclipboard()

        if isinstance(im, Image.Image):
            print("Image: size : %s, mode: %s" % (im.size, im.mode))
            im.save("input.png")
        elif im:
            for filename in im:
                print("filename:%s" % filename)
                im = Image.open(filename)
        else:
            print("clipboard is empty")
        self.photo.setPixmap(QPixmap("input.png"))

    def read_local_horizontal(self):
        print("read_r")
        image = cv2.imread('input.png')

        # 文字识别
        denoised = preprocess.Preprocess().process(image=image)
        text = pytesseract.image_to_string(denoised, lang='jpn')
        text = text.replace(" ", "").replace("\n", "")
        self.jpn.setText(text)
        # 输出识别结果

    def read_local_vert(self):

        image = cv2.imread('input.png')
        print("read_image")
        # 文字识别
        denoised = preprocess.Preprocess().process(image=image)
        text = pytesseract.image_to_string(denoised, lang='jpn_vert')
        text = text.replace(" ", "").replace("\n", "")
        self.jpn.setText(text)

    def YOUDAOtranslate(self):
        romans = ToRoman.ToRoman().Roman(text=self.jpn.text())
        translateResult = translator.YouDaoTranslator().YOUDAOtranslate(text=self.jpn.text())
        self.lineEdit_result.repaint()
        self.lineEdit_result.setText(translateResult)
        self.roman.repaint()
        self.roman.setText(romans)
    def BAIDUtranslate(self):
        romans = ToRoman.ToRoman().Roman(text=self.jpn.text())
        translateResult = translator.BaiDuTranslator().BAIDUtranslate(text=self.jpn.text())
        self.lineEdit_result.repaint()
        self.lineEdit_result.setText(translateResult)

        self.roman.repaint()
        self.roman.setText(romans)
    def GPTtranslate(self):
        romans = ToRoman.ToRoman().Roman(text=self.jpn.text())
        translateResult = translator.GptTranslator().GPTtranslate(text=self.jpn.text())
        self.lineEdit_result.repaint()
        self.lineEdit_result.setText(translateResult)

        self.roman.repaint()
        self.roman.setText(romans)

if __name__ == '__main__':
    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    # setup stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')
    # app = QApplication(sys.argv)
    gui = Template()
    gui.show()
    sys.exit(app.exec_())
