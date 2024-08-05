from django.db import models
from social_media_backend import settings
from .posts import Post

User = settings.AUTH_USER_MODEL

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    description = models.TextField()
    image = models.ImageField(upload_to='stories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shared_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_in_stories')
    
class StoryView(models.Model):
    story = models.ForeignKey(Story, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='viewed_stories', on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'user')
