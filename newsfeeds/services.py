from friendship.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):
    @classmethod
    def fanout_out_followers(cls, tweet):
        # 错误的方法一
        # N+1 Queries问题，filter所有的friendships 耗费N次Queries ,for 循环每个friendship 取from_user又耗费N次Queries
        # 不能将数据库操作放在for循环里，效率会变低
        # for follower in FriendshipService.get_followers(tweet.user):
        #     NewsFeed.objects.create(user=follower, tweet=tweet,)

        # 正确的写法 使用bulk_create,把insert语句合成一条
        newsfeeds = [
            NewsFeed(user=follower,tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user,tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)


