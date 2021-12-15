from django.test import TestCase as DjnagoTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from tweets.models import Tweet


class TestCase(DjnagoTestCase):
    @property
    def anonymous_client(self):
        if hasattr(self,'_anonymoust_client'):
            return self.anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client
    def create_user(self,username,email=None,password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # 不能直接user.objects.create_user()，因为password需要被加密，username和email需要normalize
        return User.objects.create_user(username,email,password)

    def create_tweet(self,user,content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user,content=content)