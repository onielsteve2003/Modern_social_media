from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from profiles.models import Post, Like, Comment
from profiles.serializers.like_serializer import LikeSerializer
from profiles.serializers.comment_serializer import CommentSerializer

# Like/Unlike a post
class LikePostView(generics.GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        post_id = kwargs.get('post_id')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Post not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already liked the post
        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            # If the like already exists, remove it (unlike)
            like.delete()
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Post unliked successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Post liked successfully."
        }, status=status.HTTP_201_CREATED)

# Comment on a post
class CommentOnPostView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Post not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer.save(user=self.request.user, post=post)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Edit a comment
class EditCommentView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response({
                "code": status.HTTP_403_FORBIDDEN,
                "message": "You do not have permission to edit this comment."
            }, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

# Delete a comment
class DeleteCommentView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            # Check if the comment belongs to a post created by the user
            if comment.post.user != request.user:
                return Response({
                    "code": status.HTTP_403_FORBIDDEN,
                    "message": "You do not have permission to delete this comment."
                }, status=status.HTTP_403_FORBIDDEN)

        return super().delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            if comment.post.user != request.user:
                return Response({
                    "code": status.HTTP_403_FORBIDDEN,
                    "message": "You do not have permission to delete this comment."
                }, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Comment deleted successfully."
        }, status=status.HTTP_200_OK)

# Delete a comment on a post by post owner
class DeleteAnyCommentView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post = Post.objects.get(id=self.kwargs['post_id'])
        return post.comments.all()

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        post = comment.post
        if post.user != request.user:
            return Response({
                "code": status.HTTP_403_FORBIDDEN,
                "message": "You do not have permission to delete this comment."
            }, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Comment deleted successfully."
        }, status=status.HTTP_200_OK)

# Get all comments on a post
class PostCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]  # Allow all users to view comments

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Comment.objects.none()  # Return an empty queryset if the post is not found

        return post.comments.all()

    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = Post.objects.filter(id=post_id).first()  # Check if the post exists
        
        if not post:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Post not found."
            }, status=status.HTTP_404_NOT_FOUND)

        response = super().get(request, *args, **kwargs)
        response.data = {
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved all post comments.",
            "data": response.data
        }
        return Response(response.data, status=status.HTTP_200_OK)