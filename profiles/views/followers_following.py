from rest_framework import status, generics, serializers
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Follow
from ..serializers import FollowSerializer, UserFollowerCountSerializer, UserFollowingCountSerializer, FollowerWithUsernameSerializer, FollowingWithUsernameSerializer
from profiles.models import CustomUser

# THis is to follow a user
class FollowUserView(generics.CreateAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        follower = self.request.user
        followed_user_id = self.kwargs['user_id']
        
        # Check if the followed user exists
        try:
            followed = CustomUser.objects.get(id=followed_user_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
        # Check if already following
        if Follow.objects.filter(follower=follower, followed=followed).exists():
            raise serializers.ValidationError("You are already following this user.")
        
        # Ensure the follower is not the same as the followed user
        if follower.id == followed.id:
            raise serializers.ValidationError("You cannot follow yourself.")
        
        # Save the follow relationship
        serializer.save(follower=follower, followed=followed)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is already followed
        if Follow.objects.filter(follower=request.user, followed=user_id).exists():
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "You are already following this user."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Follow the user
        response = super().post(request, *args, **kwargs)
        
        # Fetch the followed user
        followed_user = CustomUser.objects.get(id=user_id)
        
        return Response({
            "code": status.HTTP_200_OK,
            "message": f"You followed {followed_user.username}"
        }, status=status.HTTP_200_OK)

# This is to unfollow a user
class UnfollowUserView(generics.DestroyAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        follower = self.request.user
        try:
            return Follow.objects.get(follower=follower, followed=user_id)
        except Follow.DoesNotExist:
            raise serializers.ValidationError("You are not following this user.")

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id is None:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Proceed with unfollow operation
        response = super().delete(request, *args, **kwargs)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "You have unfollowed this user."
        }, status=status.HTTP_200_OK)
    
# This is to get the total numbet of user's followers
class UserFollowerCountView(generics.RetrieveAPIView):
    serializer_class = UserFollowerCountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        if user_id is None:
            # Return the profile of the currently authenticated user if no user_id is provided
            return self.request.user
        
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise NotFound("User not found")

# This is to get the total number of user's followings
class UserFollowingCountView(generics.RetrieveAPIView):
    serializer_class = UserFollowingCountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        if user_id is None:
            # Return the profile of the currently authenticated user if no user_id is provided
            return self.request.user
        
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise NotFound("User not found")
        
# This retrieves the list if a user's followers using their username, It displays their username
class UserFollowersView(generics.ListAPIView):
    serializer_class = FollowerWithUsernameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return a list of users who are following the currently authenticated user
        return CustomUser.objects.filter(followers__follower=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "Successfully retrieved followers",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# This retrieves the list if a user's followings using their username, It displays their username
class UserFollowingView(generics.ListAPIView):
    serializer_class = FollowingWithUsernameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return a list of users whom the currently authenticated user is following
        return CustomUser.objects.filter(following__follower=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "Successfully retrieved followings",
            "data": serializer.data
        }, status=status.HTTP_200_OK)