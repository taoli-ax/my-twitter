from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from friendship.models import Friendship
from friendship.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FollowSerializerForCreate,
    UserSerializerforFriendship,)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    """
    followers 查询某个用户已经拥有的所有粉丝
    followings 查询某个用户已经关注的所有人
    follow 关注某个用户
    unfollow 取消关注某个用户
    from_user 收到某个用户的关注
    from_user_id 发出关注的用户id
    to_user 给予某个用户的关注
    to_user_id 被给予关注的用户id

    """
    queryset = User.objects.all()
    serializer_class=UserSerializerforFriendship

    @action(methods=['GET'],detail=True,permission_classes=[AllowAny])
    def followers(self,request,pk):
        # 查询哪些用户关注了我，用to_user
        friendships = Friendship.objects.filter(to_user_id=pk)
        # 序列化数据
        serializer = FollowerSerializer(data=friendships,many=True)
        # 展示数据
        if not serializer.is_valid():
            Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=400)
        return Response(
            {'followers':serializer.data},
            status=status.HTTP_200_OK)

    @action(methods=['GET'],detail=True,permission_classes=[AllowAny])
    def followings(self,request,pk):
        friendships = Friendship.objects.filter(from_user_id=pk)
        serializer = FollowingSerializer(friendships,many=True)
        return Response(
            {'followings':serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'],detail=True,permission_classes=[IsAuthenticated])
    def follow(self,request,pk):
        # /api/friendship/<target_pk>/follow
        self.get_object()
        if Friendship.objects.filter(from_user=request.user,to_user_id=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
                 },status=status.HTTP_201_CREATED)
        serializer = FollowSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': int(pk)})
        if not serializer.is_valid():
            return Response({
                'success':False,
                'message':'Please check input.',
                'errors':serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'],detail=True,permission_classes=[IsAuthenticated])
    def unfollow(self,request,pk):
        unfollow_user = self.get_object()
        # 无法取消关注自己
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You can not unfollow yourself.'
            },status=status.HTTP_400_BAD_REQUEST)
        # 删除这一对关注关系,deleted 一共删除了多少数据，_具体的删除数据类型和值。例如 foreign key 的 cascade
        deleted,_=Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user
        ).delete()
        return Response({
            'success': True,
            'deleted': deleted
        })

    def list(self,request):
        return Response({'message':'hello world!'})
