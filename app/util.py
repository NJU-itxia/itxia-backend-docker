# coding:utf-8
import datetime
import hashlib
import requests
import json
import base64


def message_validate(phone_number, validate_number):
    accountSid = "8aaf0708584c07c201585d02b2070b57"
    accountToken = "3e61e3f146cb475683229c4e9bc77772"
    appid = "8aaf0708584c07c201585d04e8be0b5d"
    templateId = '1'
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    signature = accountSid + accountToken + now
    m = hashlib.md5()
    m.update(signature)
    sigParameter = m.hexdigest().upper()
    # sigParameter = hashlib.md5().update(signature).hexdigest().upper()
    url = "https://sandboxapp.cloopen.com:8883/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s" % (accountSid, sigParameter)
    authorization = accountSid + ':' + now
    new_authorization = base64.encodestring(authorization).strip()
    headers = {'content-type': 'application/json;charset=utf-8', 'accept': 'application/json',
               'Authorization': new_authorization}
    data = {'to': phone_number, 'appId': appid, 'templateId': templateId, 'datas': [str(validate_number), '3']}
    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    if response.json()['statusCode'] == '000000':
        return True, response.json().get('statusMsg')
    else:
        return False, response.json().get('statusMsg')
