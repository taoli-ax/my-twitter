from django.contrib.auth.models import User
from friendship.models import Friendship


class FriendshipService(object):
    @classmethod
    def get_followers(cls,user):
        # 错误的写法两种
        # 正确的写法一
        friendships = Friendship.objects.filter(to_user=user)
        followers_ids = [friendship.from_user_id for friendship in friendships]
        followers = User.objects.filter(id__in=followers_ids)
        return followers
        # 正确写法二
        # friendships = Friendship.objects.filter(
        #     to_user=user,
        # ).prefetch_related('from_user')
        # return [friendship.from_user for friendship in friendships]