from rest_framework import serializers
from profiles.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        # User and post are handled in the view, so they don't need to be in the serializer.
        return super().create(validated_data)
