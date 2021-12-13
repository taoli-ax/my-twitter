from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
# Create your tests here.
from tweets.models import Tweet
from utils.time_helpers import utc_now


class TweetTest(TestCase):
    def test_hours_to_now(self):
        tolle=User.objects.create_user(username='tolle')
        tweet=Tweet.objects.create(user=tolle,content='hello world!')
        tweet.created_at =utc_now()-timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now,10)