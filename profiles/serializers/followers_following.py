from rest_framework import serializers
from ..models import Follow
from profiles.models import CustomUser

# Custom configuration for following and unfollowing users 
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        # We set field to be empty because we are handling it in views already
        fields = []

# Custom configuration for getting followers count 
class UserFollowerCountSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'fullname', 'follower_count')

    def get_follower_count(self, obj):
        return obj.followers.count()
    
# Custom configuration for getting following count
class UserFollowingCountSerializer(serializers.ModelSerializer):
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'fullname', 'following_count')

    def get_following_count(self, obj):
        return obj.following.count()  # Using the 'following' related name


class FollowerWithUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'fullname')

class FollowingWithUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'fullname')