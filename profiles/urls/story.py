from django.urls import path
from ..views.story_views import CreateStoryView, FriendStoriesView, ViewStoryView, TrackStoryView, StoryViewersView, StoryViewCountView, SharePostToStoryView

urlpatterns = [
    path('', CreateStoryView.as_view(), name='create-story'),
    path('friends', FriendStoriesView.as_view(), name='friend-stories'),
    path('<int:pk>', ViewStoryView.as_view(), name='view-story'),
    path('<int:pk>/track', TrackStoryView.as_view(), name='track-story'),
    path('<int:story_id>/viewers', StoryViewersView.as_view(), name='story-viewers'),
    path('<int:story_id>/view-count', StoryViewCountView.as_view(), name='story-view-count'),
    path('share', SharePostToStoryView.as_view(), name='share-post-to-story'),
]
