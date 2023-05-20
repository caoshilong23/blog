from tools.sms import YunTongXin
from blogpro.celery import app


@app.task
def send_c(phone, code):
    sms_config = {
        'accountSid': '2c94811c87fb7ec6018819833efe0a10',
        'accountToken': '8970c932f9c446cf9fc90c5524d036b9',
        'appId': '2c94811c87fb7ec601881983403a0a17',
        'templateId': '1'
    }
    yun = YunTongXin(**sms_config)
    res = yun.run(phone, code)
    print(res)
