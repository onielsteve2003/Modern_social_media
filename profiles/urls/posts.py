from django.urls import path
from ..views.posts import CreatePostView, PostListView, PostUpdateView, FollowingPostsView, FollowingAndFollowersPostsView, SharePostToTimelineView
from ..views.likes_comments import LikePostView, CommentOnPostView, EditCommentView, DeleteCommentView, DeleteAnyCommentView, PostCommentsView
from ..views.favorites import AddFavoriteView, ListFavoritesView

urlpatterns = [
    path('add', CreatePostView.as_view(), name='create-post'),
    path('get-posts', PostListView.as_view(), name='post-list'),
    path('<int:pk>', PostUpdateView.as_view(), name='post-detail'),
    path('following', FollowingPostsView.as_view(), name='following-posts'),
    path('following-and-followers', FollowingAndFollowersPostsView.as_view(), name='following-and-followers-posts'),
    path('<int:post_id>/like', LikePostView.as_view(), name='like-post'),
    path('<int:post_id>/comment', CommentOnPostView.as_view(), name='comment-post'),
    path('comments/<int:pk>/edit', EditCommentView.as_view(), name='edit-comment'),
    path('comments/<int:pk>/delete', DeleteCommentView.as_view(), name='delete-comment'),
    path('<int:post_id>/comments/<int:pk>/delete', DeleteAnyCommentView.as_view(), name='delete-any-comment'),
    path('<int:post_id>/comments', PostCommentsView.as_view(), name='post-comments'),
    path('<int:post_id>/favorite', AddFavoriteView.as_view(), name='add_or_remove_favorite'),
    path('favorites', ListFavoritesView.as_view(), name='list_favorites'),
    path('share-post-to-timeline', SharePostToTimelineView.as_view(), name='share-post-to-timeline'),
]
