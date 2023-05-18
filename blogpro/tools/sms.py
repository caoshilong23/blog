import datetime
import hashlib
import base64
import json

import requests


class YunTongXin():
    base_url = "https://app.cloopen.com:8883"
    def __init__(self, accountSid,accountToken,appId,templateId):
        self.accountSid = accountSid  # 账户ID
        self.accountToken = accountToken  # 授权令牌
        self.appId = appId
        self.templateId = templateId

    def get_requset_url(self, sig):
        self.url = self.base_url + "/2013-12-26/Accounts/{}/SMS/TemplateSMS?sig={}".format(self.accountSid, sig)
        return self.url
    def get_datetime(self):
        # 生成时间戳
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def get_sig(self, timestamp):
        s = self.accountSid+self.accountToken+timestamp
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()

    def get_requset_header(self, timestamp):
        s = self.accountSid+':'+timestamp
        auth = base64.b64encode(s.encode()).decode()
        return {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8',
            'Authorization':auth
        }

    def get_request_body(self,phone,code):
        return {
            'to':phone,
            'appId':self.appId,
            'templateId':self.templateId,
            'datas':[code,'3']
        }

    def request_api(self,url,header,body):
        res = requests.post(url=url,headers=header,data=body)
        return res.text


    def run(self,phone,code):
        timestamp = self.get_datetime()
        sig = self.get_sig(timestamp)
        url = self.get_requset_url(sig)
        # print(url)
        header = self.get_requset_header(timestamp)
        # print(header)
        body = self.get_request_body(phone=phone,code=code)
        res = self.request_api(url,header,json.dumps(body))
        return res


if __name__ == "__main__":
    config = {
        # accountSid, accountToken, appId, templateId
        'accountSid':'2c94811c87fb7ec6018819833efe0a10',
        'accountToken':'8970c932f9c446cf9fc90c5524d036b9',
        'appId':'2c94811c87fb7ec601881983403a0a17',
        'templateId':'1'
    }
    yun = YunTongXin(**config)
    res=yun.run('15036759603','1576')
    print(res)


