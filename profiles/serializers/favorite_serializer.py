from rest_framework import serializers
from profiles.models import Favorite, Post

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'post', 'user']

    def create(self, validated_data):
        post_id = self.context['view'].kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        user = self.context['request'].user
        validated_data['post'] = post
        validated_data['user'] = user
        return super().create(validated_data)
