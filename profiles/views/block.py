from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models.block import Block
from profiles.serializers.block_serializer import BlockSerializer

# Block or unblock a user
class ToggleBlockView(generics.GenericAPIView):
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_to_block_id = self.kwargs.get('user_id')
        user_to_block = self.get_user(user_to_block_id)

        if not user_to_block:
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "User to block/unblock not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already blocked
        block_exists = Block.objects.filter(blocker=request.user, blocked=user_to_block).exists()

        if block_exists:
            # Unblock the user
            Block.objects.filter(blocker=request.user, blocked=user_to_block).delete()
            return Response({
                "code": status.HTTP_200_OK,
                "message": f"User {user_to_block} has been unblocked."
            }, status=status.HTTP_200_OK)
        else:
            # Block the user
            Block.objects.create(blocker=request.user, blocked=user_to_block)
            return Response({
                "code": status.HTTP_201_CREATED,
                "message": f"User {user_to_block} has been blocked."
            }, status=status.HTTP_201_CREATED)

    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
