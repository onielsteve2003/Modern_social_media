from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from profiles.models import Post, Favorite
from profiles.serializers.favorite_serializer import FavoriteSerializer

# Add and remove posts to favorites
class AddFavoriteView(generics.GenericAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        post_id = kwargs.get('post_id')

        # Check if the post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Post not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the favorite already exists
        favorite, created = Favorite.objects.get_or_create(user=user, post=post)

        if not created:
            # If the favorite already exists, remove it (unfavorite)
            favorite.delete()
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Post removed from favorites."
            }, status=status.HTTP_200_OK)

        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Post added to favorites."
        }, status=status.HTTP_201_CREATED)

# List all favorite posts
class ListFavoritesView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter favorites for the authenticated user
        return Favorite.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({
                "code": status.HTTP_401_UNAUTHORIZED,
                "message": "User is not authenticated."
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Retrieve the favorites
        favorites = self.get_queryset()
        
        # If no favorites are found
        if not favorites.exists():
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "No favorite posts found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get the serialized data
        response = super().get(request, *args, **kwargs)
        
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully retrieved all favorite posts.",
            "data": response.data
        })