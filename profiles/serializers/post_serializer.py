from rest_framework import serializers
from profiles.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'user', 'title', 'description', 'image', 'created_at')
        read_only_fields = ('user', 'created_at')

    def validate(self, data):
        if not any([data.get('title'), data.get('description'), data.get('image')]):
            raise serializers.ValidationError("At least one of title, description, or image must be provided.")
        return data

