from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Story, Follow, StoryView, Post
from profiles.serializers.story_serializer import StorySerializer, StoryViewSerializer

# Add a story
class CreateStoryView(generics.CreateAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Story created successfully.",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

# Get all stories of friends (followers and followings)
class FriendStoriesView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
        followers_ids = Follow.objects.filter(followed=user).values_list('follower_id', flat=True)
        friend_ids = set(following_ids).union(set(followers_ids))
        return Story.objects.filter(user_id__in=friend_ids)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved all stories from friends.",
            "data": response.data
        }, status=status.HTTP_200_OK)

# View any story
class ViewStoryView(generics.RetrieveAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved story.",
            "data": response.data
        }, status=status.HTTP_200_OK)

class TrackStoryView(generics.GenericAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the story object based on the URL parameters
        story_id = self.kwargs.get('pk')
        return Story.objects.filter(id=story_id)

    def get(self, request, *args, **kwargs):
        # Retrieve the story object
        story = self.get_queryset().first()  # Use .first() to get a single object or None
        
        if not story:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Story not found."
            }, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        
        # Track the view
        StoryView.objects.get_or_create(story=story, user=user)
        
        serializer = self.get_serializer(story)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully tracked story view.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
# Get viewers of a story
class StoryViewersView(generics.ListAPIView):
    serializer_class = StoryViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        story_id = self.kwargs.get('story_id')
        return StoryView.objects.filter(story_id=story_id)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved story viewers.",
            "data": response.data
        }, status=status.HTTP_200_OK)

# Get total count of viewers of a story
class StoryViewCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        story_id = self.kwargs.get('story_id')
        count = StoryView.objects.filter(story_id=story_id).count()
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved story view count.",
            "data": {"view_count": count}
        }, status=status.HTTP_200_OK)
    
# Share a post to a story
class SharePostToStoryView(generics.CreateAPIView):
    serializer_class = StorySerializer
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

        # Prepare the data for Story creation
        story_data = {
            'description': post.description,
            'image': post.image,
            'shared_post': post.id
        }

        serializer = self.get_serializer(data=story_data)
        serializer.is_valid(raise_exception=True)

        # Save the story with the current user
        story = serializer.save(user=request.user)

        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Post shared to story successfully.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)