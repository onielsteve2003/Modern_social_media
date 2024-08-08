from django.urls import path
from ..views.followers_following import FollowUserView, UnfollowUserView, UserFollowerCountView, UserFollowingCountView, UserFollowersView, UserFollowingView

urlpatterns = [
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('followers-count/', UserFollowerCountView.as_view(), name='followers-count'),
    path('following-count/', UserFollowingCountView.as_view(), name='following-count-user'),
    path('followers/', UserFollowersView.as_view(), name='user-followers'),
    path('following/', UserFollowingView.as_view(), name='user-following'),
]
