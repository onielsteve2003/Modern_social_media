# from django.contrib.auth import get_user_model
from rest_framework import serializers
from profiles.models import Story, StoryView, Post

# User = get_user_model()

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'user', 'description', 'image', 'created_at', 'shared_post']
        read_only_fields = ['user', 'created_at']

class StoryViewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = StoryView
        fields = ['story', 'username', 'viewed_at']  # Exclude 'user' and only include required fields

    def get_username(self, obj):
        return obj.user.username  # Retrieve the username from the user object