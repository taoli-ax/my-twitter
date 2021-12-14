from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.api.serializers import UserSerializerforFriendship
from friendship.models import Friendship


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerforFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerforFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You can not follow yourself.'
            })
        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id']
        ).exists():
            raise ValidationError({
                'message': 'You has already followed this user'
            })

        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id
        )
