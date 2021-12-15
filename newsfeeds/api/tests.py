from newsfeeds.models import NewsFeed
from friendship.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendship/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self) -> None:
        self.tolle = self.create_user('tolle')
        self.tolle_client = APIClient()
        self.tolle_client.force_authenticate(self.tolle)

        self.mark = self.create_user('mark')
        self.mark_client = APIClient()
        self.mark_client.force_authenticate(self.mark)

        # create followers and followings for mark
        for i in range(2):
            follower = self.create_user(f'mark_followers{i}')
            Friendship.objects.create(from_user=follower,to_user=self.mark)

        for i in range(3):
            following = self.create_user(f'mark_followings{i}')
            Friendship.objects.create(from_user=self.mark,to_user=following)

    def test_list(self):
        # 自己看到自己的推文
        self.tolle_client.post(POST_TWEETS_URL, {'content':'lullaby'})
        newsfeed = self.tolle_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(newsfeed.data['newsfeeds']),1)

        # 关注一波，看到推文
        self.mark_client.post(FOLLOW_URL.format(self.tolle.id))
        self.tolle_client.post(POST_TWEETS_URL, {'content': 'aloha heja he'})
        response = self.mark_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['content'],'aloha heja he')

        # 需要登陆才能看推文
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code,403)

        # post 失败
        response = self.tolle_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code,405)



