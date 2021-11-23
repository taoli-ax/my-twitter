from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
# Create your tests here.

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.createUser(
            username='admin008',
            email='admin008@outlook.com',
            password='correct password',
        )

    def createUser(self,username,email,password):
        return User.objects.create_user(username,email,password)

    def test_login(self):
        # testcase:用post而不是get
        response=self.client.get(LOGIN_URL,{
            'username': self.user.username,
            'password': self.user.password
        })

        # 如果登陆失败，http status code 返回 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code,405)

        # testcase:密码错误
        response = self.client.post(LOGIN_URL,{
            'username':self.user.username,
            'password': 'worng password'
        })

        self.assertEqual(response.status_code,400)

        # testcse:还没登陆
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],False)

        # 正确的密码
        response = self.client.post(LOGIN_URL,{
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code,200)
        self.assertNotEqual(response.data['user'],None)
        self.assertEqual(response.data['user']['email'],'admin008@outlook.com')
        # testcase:验证已经登陆
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],True)

    def test_logout(self):
        # 先登陆
        self.client.post(LOGIN_URL,{
            'username':self.user.username,
            'password':'correct password',
        })
        # 验证已登陆
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],True)
        # get请求出错
        response=self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code,405)
        # 登出
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code,200)
        # 验证已登出
        response=self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'],False)

    def test_signup(self):
        data ={
            'username':'someone',
            'password':'bugaosuni',
            'email':'guizhidao@jiuzhang.com'
        }
        # get请求失败
        response = self.client.get(SIGNUP_URL,data)
        self.assertEqual(response.status_code,405)
        # 邮箱错误
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'password': 'bugaosuni',
            'email': 'guizhidao'
        })
        self.assertEqual(response.data['message'], 'Please check input.')
        # 用户名错误
        response = self.client.post(SIGNUP_URL, {
            'username': 'someonesomeonesomeonesomeonesomeonesomeonesomeonesomeone',
            'password': 'bugaosuni',
            'email': 'guizhidao@dfdf.com'
        })
        self.assertEqual(response.data['message'], 'Please check input.')
        # 密码错误
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'password': '',
            'email': 'guizhidao@dfdf.com'
        })
        self.assertEqual(response.data['message'], 'Please check input.')
        # 成功注册
        response = self.client.post(SIGNUP_URL,data)
        self.assertNotEqual(response.data['user'],None)
        # 已登陆
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)












