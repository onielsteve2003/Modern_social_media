from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from profiles.models import Post, Follow
from profiles.serializers import PostSerializer, TimelinePostSerializer 

# Make a post
class CreatePostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Post created successfully.",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

# View all posts in the app 
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved all posts.",
            "data": response.data
        }, status=status.HTTP_200_OK)

# Update a post and Delete a post
class PostUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own posts
        return Post.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        post = self.get_object()

        # Check if the user is the owner of the post
        if post.user != request.user:
            return Response({
                "code": status.HTTP_403_FORBIDDEN,
                "message": "You do not have permission to edit this post."
            }, status=status.HTTP_403_FORBIDDEN)

        response = super().update(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Post updated successfully.",
            "data": response.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        post = self.get_object()

        # Check if the user is the owner of the post
        if post.user != request.user:
            return Response({
                "code": status.HTTP_403_FORBIDDEN,
                "message": "You do not have permission to delete this post."
            }, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Post deleted successfully."
        }, status=status.HTTP_200_OK)

# Retrieve posts of people you are following
class FollowingPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
        return Post.objects.filter(user_id__in=following_ids)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved posts from users you are following.",
            "data": response.data
        }, status=status.HTTP_200_OK)

# Retrieve posts of people you are following and those following you
class FollowingAndFollowersPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
        followers_ids = Follow.objects.filter(followed=user).values_list('follower_id', flat=True)
        user_ids = set(following_ids).union(set(followers_ids))
        return Post.objects.filter(user_id__in=user_ids)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved posts from users you are following and those following you.",
            "data": response.data
        }, status=status.HTTP_200_OK)

# Share a post to the timeline
class SharePostToTimelineView(generics.CreateAPIView):
    serializer_class = TimelinePostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        
        if not post_id:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Post ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Post not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create a new post on the timeline
        timeline_post_data = {
            'title': post.title,
            'description': post.description,
            'image': post.image,
            'user': request.user.id 
        }
        
        serializer = self.get_serializer(data=timeline_post_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # Explicitly set the user field
        
        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Post reshared to timeline successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)