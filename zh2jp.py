import sys

import requests
import time

import http.client
import hashlib
import urllib
import random
import json

import cv2

import pytesseract
import openai
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qt_material import apply_stylesheet

openai.api_base = ""  #openai
openai.api_key = ""#密钥

appid = ''  # 填写你的百度appid
secretKey = ''  # 填写你的密钥


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

        read = QPushButton('本地竖版')
        read.clicked.connect(self.read_image)

        r = QPushButton('本地横版')
        r.clicked.connect(self.read_r)

        copyn = QPushButton('粘贴横版')
        copyn.clicked.connect(self.normal)

        copyv = QPushButton('粘贴竖版')
        copyv.clicked.connect(self.vert)

        youdao = QPushButton('youdao')
        youdao.clicked.connect(self.YOUDAOtranslate)
        baidu = QPushButton('baidu')
        baidu.clicked.connect(self.BAIDUtranslate)
        gpt = QPushButton('gpt')
        gpt.clicked.connect(self.GPTtranslate)


        grid = QGridLayout(self)
        grid.addWidget(self.lineEdit_result, 6, 0, 1, 4)
        # grid.addWidget(self.lineEdit_result, 2, 0)
        grid.addWidget(youdao, 5, 0, 1, 1)
        grid.addWidget(baidu, 5, 1, 1, 1)
        grid.addWidget(gpt, 5, 2, 1, 1)

        grid.addWidget(self.jpn, 4, 0, 1, 4 )
        # grid.addWidget(self.jpn, 7, 0)

        grid.addWidget(read, 2 ,0, 2, 1)
        # grid.addWidget(read, 5, 0)

        grid.addWidget(r, 1, 0, 2, 1)
        # grid.addWidget(r, 6, 0)

        grid.addWidget(copyn, 1, 3, 2, 1)
        # grid.addWidget(copyn, 4, 0)

        grid.addWidget(copyv, 2, 3, 2, 1)
        # grid.addWidget(copyv, 3, 0)

        # grid.addWidget(btn, 0, 0, Qt.AlignHCenter)
        grid.addWidget(btn, 0, 1, 1, 2, Qt.AlignHCenter)

        # grid.addWidget(self.photo, 1, 0)
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

    def vert(self):
        self.readcopy()
        self.read_image()

    def normal(self):
        self.readcopy()
        self.read_r()

    def scale(self, image):
        print("scale")
        size = 600
        # 获取原始图像宽高。
        height, width = image.shape[0], image.shape[1]
        # 等比例缩放尺度。
        scale = height / size
        # 获得相应等比例的图像宽度。
        width_size = int(width / scale)
        print(width, height)
        # resize
        if (width <= 100 or height < 150):
            image_resize = cv2.resize(image, (width_size, size))
        else:
            image_resize = image

        return image_resize

    def preprocess(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        return denoised

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

    def read_r(self):
        print("read_r")
        image = cv2.imread('input.png')
        image = self.scale(self, image)
        # 文字识别
        denoised = self.preprocess(self, image)
        text = pytesseract.image_to_string(denoised, lang='jpn')
        text = text.replace(" ", "").replace("\n", "")
        self.jpn.setText(text)
        # 输出识别结果
        # self.YOUDAOtranslate(text)

    def read_image(self):

        image = cv2.imread('input.png')
        print("read_image")
        image = self.scale(image)
        # 文字识别
        denoised = self.preprocess(image)
        text = pytesseract.image_to_string(denoised, lang='jpn_vert')
        text = text.replace(" ", "").replace("\n", "")
        self.jpn.setText(text)
        # 输出识别结果
        # self.GPTtranslate(text.replace(" ", "").replace("\n", ""))

    def YOUDAOtranslate(self):
        text = self.jpn.text()
        print("youdao")
        sett = True
        # m3u8 AES加密
        while sett == True:
            word = text
            print(text)
            # word = input('请输入你想要翻译的内容(输入0即可退出): ')
            # f = open('有道.js', encoding='utf-8')
            # js_code = f.read()
            # compile_code = execjs.compile(js_code)
            # json_data = compile_code.call('youdao', word)
            string = "fanyideskweb" + word + str(int(time.time() * 10000)) + "Ygy_4c=r#e#4EX^NUGUc5"
            sign = hashlib.md5(string.encode('utf-8')).hexdigest()
            # print(json_data)
            url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'  # 确定请求网址
            # headers 请求头 伪装python代码, 如果你不伪装, 就被识别出来是爬虫程序, 从而得不到数据内容
            headers = {
                'Cookie': 'OUTFOX_SEARCH_USER_ID=1092484940@10.169.0.82; OUTFOX_SEARCH_USER_ID_NCOO=1350964471.5510483; JSESSIONID=aaa_jaG1Fa7rPdutNrm_x; ___rl__test__cookies=1647328160933',
                'Host': 'fanyi.youdao.com',
                'Origin': 'https://fanyi.youdao.com',
                'Referer': 'https://fanyi.youdao.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            }
            # 表单数据, post请求都是需要提交一个from data 表单数据
            data = {
                'i': word,
                'from': 'AUTO',
                'to': 'AUTO',
                'smartresult': 'dict',
                'client': 'fanyideskweb',
                'salt': int(time.time() * 10000),
                'sign': sign,
                'lts': int(time.time() * 1000),
                'bv': 'c2777327e4e29b7c4728f13e47bde9a5',
                'doctype': 'json',
                'version': '2.1',
                'keyfrom': 'fanyi.web',
                'action': 'FY_BY_REALTlME',
            }
            response = requests.post(url=url, data=data, headers=headers)  # <Response [200]> 200 状态码请求成功 响应对象
            # response.json() 返回json字典数据 键值对取值

            # print(response.json()['translateResult'])
            # translateResult = response.json()['translateResult'][0][0]['tgt']
            # lenth=len(response.json()['translateResult'])
            # # pprint.pprint(response.json())
            # print('翻译的结果: ', translateResult)
            print("翻译的结果")
            # print(response.json()['translateResult'])
            translateResult = ""
            for i in response.json()['translateResult'][0]:
                print(i['tgt'])
                translateResult+=i['tgt']
            print(translateResult)
            self.lineEdit_result.repaint()
            self.lineEdit_result.setText(translateResult)
            sett = False

    def BAIDUtranslate(self):
        text = self.jpn.text()
        print("baidu")


        httpClient = None
        myurl = '/api/trans/vip/translate'

        fromLang = 'jp'  # 原文语种
        toLang = 'zh'  # 译文语种
        salt = random.randint(32768, 65536)
        q = text

        sign = appid + q + str(salt) + secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
            salt) + '&sign=' + sign

        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)

            # response是HTTPResponse对象
            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            print('翻译：：')
            print(result['trans_result'][0])
            print(result['trans_result'][0]['src'])
            print(result['trans_result'][0]['dst'])
            translateResult = result['trans_result'][0]['dst']
            self.lineEdit_result.repaint()
            self.lineEdit_result.setText(translateResult)
        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()

    def gpt_35_api_stream(self, messages: list):
        """为提供的对话消息创建新的回答 (流式传输)

        Args:
            messages (list): 完整的对话消息
            api_key (str): OpenAI API 密钥

        Returns:
            tuple: (results, error_desc)
        """
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=messages,
                stream=True,
            )
            completion = {'role': '', 'content': ''}
            for event in response:
                if event['choices'][0]['finish_reason'] == 'stop':
                    # print(f'收到的完成数据: {completion}')
                    break
                for delta_k, delta_v in event['choices'][0]['delta'].items():
                    # print(f'流响应数据: {delta_k} = {delta_v}')
                    completion[delta_k] += delta_v
            messages.append(completion)  # 直接在传入参数 messages 中追加消息

            return (completion)
        except Exception as err:
            return (False, f'OpenAI API 异常: {err}')

    def GPTtranslate(self):
        print("GPT")
        text = self.jpn.text()
        messages = [{'role': 'user', 'content': '翻译以下的日语文本，只写译文：' + text +''}, ]
        result = self.gpt_35_api_stream(messages)
        print(result)
        print(result['content'])
        self.lineEdit_result.repaint()
        self.lineEdit_result.setText(result['content'])


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
