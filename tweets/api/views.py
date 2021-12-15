from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        if 'user_id' not in request.query_params:
            return Response('missing user_id',status=400)
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets,many=True)
        return Response({'tweets':serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request':request},
        )
        if not serializer.is_valid():
            return Response({
                'success':False,
                'message':'Please check input.',
                'errors': serializer.errors
            },status=400)
        # trigger create method in TweetSerializerForCreate
        tweet = serializer.save()
        # 创建之后推送给followers
        NewsFeedService.fanout_out_followers(tweet)
        return Response(TweetSerializer(tweet).data,status=201)


