import requests
import time
import http.client
import hashlib
import urllib
import random
import json

import openai

# openai.api_base = ""  # openai
# openai.api_key = ""  # 密钥
#
# appid = ''  # 填写你的百度appid
# secretKey = ''  # 填写你的密钥
openai.api_base = "https://api.chatanywhere.com.cn/v1"  #openai
openai.api_key = "sk-lMZCS1dNzmt4hDmLJkvWjiylx5YvvO9rHMGtVNf80uBBocqi"#密钥

appid = '20230912001814943'  # 填写你的百度appid
secretKey = 's_3ecwjHG4Ffp68syzhN'  # 填写你的密钥

class BaiDuTranslator:
    def __init__(self):
        super().__init__()

    def BAIDUtranslate(self, text):
        # text = ui.jpn.text()
        print(text)
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
            # ui.lineEdit_result.repaint()
            # ui.lineEdit_result.setText(translateResult)
            return translateResult
        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()


class YouDaoTranslator:
    def __init__(self):
        super().__init__()

    def YOUDAOtranslate(self, text):
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
            print("翻译的结果")
            translateResult = ""
            for i in response.json()['translateResult'][0]:
                print(i['tgt'])
                translateResult += i['tgt']
            # print(translateResult)
            return translateResult
            sett = False


class GptTranslator:
    def __init__(self):
        super().__init__()

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

    def GPTtranslate(self, text):
        print("GPTtranslate")
        # text = ui.jpn.text()
        print(text)
        messages = [{'role': 'user', 'content': '翻译以下的日语文本，只写译文：' + text + ''}, ]
        result = self.gpt_35_api_stream(messages)
        print(result)
        return result['content']
