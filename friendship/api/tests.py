from friendship.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendship/{}/follow/'
UNFOLLOW_URL = '/api/friendship/{}/unfollow/'
FOLLOWERS_URL = '/api/friendship/{}/followers/'
FOLLOWINGS_URL = '/api/friendship/{}/followings/'


class FriendshipApiTest(TestCase):
    """
    测试设计：创建两个用户，并为用户创建粉丝和关注的人
    """
    def setUp(self) -> None:
        # 匿名用户
        self.anonymous_client=APIClient()
        # 创建用户，并已登陆
        self.tolle = self.create_user('tolle')
        self.tolle_client=APIClient()
        self.tolle_client.force_authenticate(self.tolle)

        # 创建另一个用户，并已登陆
        self.mark = self.create_user('mark')
        self.mark_client = APIClient()
        self.mark_client.force_authenticate(self.mark)

        # create followings and follower for mark
        for i in range(2):
            follower = self.create_user(f'mark_follower{i}')
            Friendship.objects.create(from_user=follower,to_user=self.mark)

        for i in range(3):
            following = self.create_user(f'mark_followings{i}')
            Friendship.objects.create(from_user=self.mark,to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.tolle.id)
        # 需要登陆才能 follow别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code,403)
        # get方式错误
        response = self.mark_client.get(url)
        self.assertEqual(response.status_code,405)
        # 不可以follow自己
        response = self.tolle_client.post(url)
        self.assertEqual(response.status_code,400)
        # follow成功
        response = self.mark_client.post(url)
        self.assertEqual(response.status_code,201)
        # 重复 follow 静默成功
        response = self.mark_client.post(url)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['duplicate'], True)
        # 反向关注，增加一条数据
        count = Friendship.objects.count()
        response = self.tolle_client.post(FOLLOW_URL.format(self.mark.id))
        self.assertEqual(response.status_code,201)
        self.assertEqual(Friendship.objects.count(),count+1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.tolle.id)

        # 成功 unfollow
        Friendship.objects.create(from_user=self.mark,to_user=self.tolle)
        count = Friendship.objects.count()
        response = self.mark_client.post(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['deleted'],1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # 无法 unfollow 自己
        response = self.tolle_client.post(url)
        self.assertEqual(response.status_code,400)

        # 不登陆无法 unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code,403)

        # 未follow的情况下unfollow，静默不报错
        count = Friendship.objects.count()
        response = self.mark_client.post(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['deleted'],0)
        self.assertEqual(Friendship.objects.count(),count)

    def test_following(self):
        url = FOLLOWINGS_URL.format(self.mark.id)

        # 成功查询 followings
        response = self.mark_client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.data['followings']),3)
        t0 = response.data['followings'][0]['created_at']
        t1 = response.data['followings'][1]['created_at']
        self.assertGreater(t0, t1)
        self.assertEqual(response.data['followings'][0]['user']['username'], 'mark_followings2')
        self.assertEqual(response.data['followings'][1]['user']['username'], 'mark_followings1')

        # post 失败
        response = self.mark_client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.mark.id)
        # post 失败
        response = self.mark_client.post(url)
        self.assertEqual(response.status_code,405)

        # get 成功查询 followers
        response = self.mark_client.get(url)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.data['followers']),2)
        t0 = response.data['followers'][0]['created_at']
        t1 = response.data['followers'][1]['created_at']
        self.assertGreater(t0,t1)
        self.assertEqual(response.data['followers'][0]['user']['username'],'mark_follower1')
        self.assertEqual(response.data['followers'][1]['user']['username'],'mark_follower0')


