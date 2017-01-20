# coding:utf-8
import requests
import json
from qiniu import put_file
import time
import random
import hashlib


class API_1_1(object):
    base_url = 'http://127.0.0.1:5000/api/v1_1'

    def __init__(self):
        self.headers = {}
        self.token = None
        self.qiniu_token = None
        self.qiniu_key = None
        self.qiniu_base_url = 'http://ogkkyym4h.bkt.clouddn.com/'


    def login(self, phone_number, password, path='/client/login'):
        random_str = str(random.randint(10000, 100000))
        time_stamp = str(int(time.time()))
        s = hashlib.sha256()
        s.update(password)
        s.update(random_str)
        s.update(time_stamp)
        encryption_str = s.hexdigest()

        payload = {'phone_number': phone_number, 'encryption_str': encryption_str, 'random_str': random_str, 'time_stamp': time_stamp}
        self.headers = {'content-type': 'application/json'}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        self.token = response_data.get('token')
        print json.dumps(response_data, ensure_ascii=False, indent=4)
        return response_data


    def client(self, path='/client'):
        self.headers = {'token': self.token}
        response = requests.get(url=self.base_url + path, headers=self.headers)
        response_data = json.loads(response.content)
        print json.dumps(response_data, ensure_ascii=False, indent=4)
        return response_data


    def logout(self, path='/client/logout'):
        self.headers = {'token': self.token}
        response = requests.get(url=self.base_url + path, headers=self.headers)
        response_data = json.loads(response.content)
        print json.dumps(response_data, ensure_ascii=False, indent=4)
        return response_data


    def get_qiniu_token(self, path='/client/get-qiniu-token'):
        response = requests.get(url=self.base_url + path)
        response_data = json.loads(response.content)
        self.qiniu_token = response_data.get('token')
        self.qiniu_key = response_data.get('key')
        localfile = '1.png'
        ret, info = put_file(self.qiniu_token, self.qiniu_key, localfile)
        print info.status_code
        if info.status_code == 200:
            print '上传成功'
            self.head_picture = self.qiniu_base_url + self.qiniu_key
            print '其url为:' + self.head_picture.encode('utf-8')
        else:
            print '上传失败'
        return response_data


    def set_head_picture(self, path='/client/set-head-picture'):
        payload = {'head_picture': self.head_picture}
        self.headers = {'token': self.token, 'content-type': 'application/json'}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        print response_data.get('message')
        return response_data


    def register_step_1(self, phone_number, path='/client/register-step-1'):
        payload = {'phone_number': phone_number}
        self.headers = {'content-type': 'application/json'}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        print response_data.get('message')
        return response_data


    def register_step_2(self, phone_number, validate_number, path='/client/register-step-2'):
        payload = {'phone_number': phone_number, 'validate_number': validate_number}
        self.headers = {'content-type': 'application/json'}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        print response_data.get('message')
        return response_data


    def register_step_3(self, phone_number, password, password_confirm, path='/client/register-step-3'):
        payload = {'phone_number': phone_number, 'password': password, 'password_confirm': password_confirm}
        self.headers = {'content-type': 'application/json'}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        print response_data.get('message')
        return response_data


    def register_step_4(self, phone_number, email, path='/client/register-step-4'):
        payload = {'phone_number': phone_number, 'email': email}
        self.headers = {'content-type': 'application/json'}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        print response_data.get('message')
        return response_data
      
        
    def get_multi_qiniu_token(self, count, path='/get-multi-qiniu-token'):
        self.headers = {'token': self.token}
        payload = {'count': count}
        response = requests.get(url=self.base_url + path, params=payload, headers=self.headers)
        response_data = json.loads(response.content)
        key_token_s = response_data.get('key_token_s')
        return key_token_s


    def post_form(self, campus, machine_model, OS, description, picture_files, path='/client/forms/post'):
        self.headers = {'token': self.token}
        count = len(picture_files)
        
        pictures = []
        if count != 0:
            key_token_s = self.get_multi_qiniu_token(count=count)
        
            for i in range(count):
                put_file(key_token_s[i]['token'], key_token_s[i]['key'], picture_files[i])
                pictures.append(self.qiniu_base_url + key_token_s[i]['key'])

        payload = {'campus': campus, 'machine_model': machine_model, 'OS': OS, 'description': description, 'pictures': pictures}
        self.headers = {'content-type': 'application/json', 'token': self.token}
        response = requests.post(url=self.base_url + path, data=json.dumps(payload), headers=self.headers)
        response_data = json.loads(response.content)
        print response_data.get('message')
        return response_data


    def get_forms(self, path='/forms'):
        self.headers = {'token': self.token}
        payload = {}
        response = requests.get(url=self.base_url + path, params=payload, headers=self.headers)
        response_data = json.loads(response.content)
        print json.dumps(response_data, ensure_ascii=False, indent=4)
        return response_data
        
    def get_form(self, id, path='/client/forms'):
        self.headers = {'token': self.token}
        payload = {}
        response = requests.get(url=self.base_url + path + '/' + str(id), params=payload, headers=self.headers)
        response_data = json.loads(response.content)
        print json.dumps(response_data, ensure_ascii=False, indent=4)
        return response_data
        

if __name__ == '__main__':
    api = API_1_1()
    quit = 'n'
    while(quit == 'n'):
        print "##########################################"
        print "测试1: 注册用户帐号\n"
        print "测试2: 登录已注册帐号并提交表单\n"
        print "测试3: 在已登录的状态下获取隶属本帐号的表单\n"
        print "测试4: 退出登录\n" 
        testcase = raw_input("请选择你要进行的测试案例(数字):")
        if testcase == '1':
            #测试用户注册
            phone_number = raw_input("请输入你选择接受验证码的手机号码(注册用):\n")
            api.register_step_1(phone_number)
            validate_number = raw_input("请输入你接收到的验证码:\n")
            api.register_step_2(phone_number, validate_number)
            password = raw_input("请设定你的登录密码:\n")
            password_confirm = raw_input("确认你的密码:\n")
            api.register_step_3(phone_number, password, password_confirm)
            email = raw_input("请输入您的邮箱(可以为空):\n")
            api.register_step_4(phone_number, email)

        if testcase == '2':
            #测试登录已注册用户
            phone_number = raw_input("请输入你的登录手机号码:\n")
            password = raw_input("请输入你的登录密码:\n")
            api.login(phone_number, password)
            #测试提交表单，含图片
            print "准备提交表单，已经自动写好"
            api.post_form('xianlin', 'mac', 'win', '電腦壞了',['1.jpg', '2.jpg'])
    
        if testcase == '3':
            #测试用户查看自己的所有表单
            api.get_forms()
            #api.get_form(1)
            #api.get_qiniu_token()
            #api.set_head_picture()
        if testcase == '4':
            #用户退出登录
            anwser = raw_input("确认退出吗？(y or n):")
            if anwser == 'y':
                api.logout()
            else:
                break
        quit = raw_input("要退出测试吗？(y or n):")
