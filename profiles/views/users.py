from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ..serializers.users import UserSerializer, SimpleUserSerializer
from ..models.users import CustomUser
from profiles.permissions import IsAuthenticatedCustom

# Signup request method
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "code": status.HTTP_201_CREATED,
            "message": "Signup successful"
        }, status=status.HTTP_201_CREATED)
    return Response({
        "code": status.HTTP_400_BAD_REQUEST,
        "error": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# Login request method
@api_view(['POST'])
def login(request):
    username_or_email = request.data.get('username_or_email')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response({
            "code": status.HTTP_400_BAD_REQUEST,
            "error": "Username or email and password are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate user by username
    user = authenticate(username=username_or_email, password=password)
    
    if user is None:
        # If username fails, try email
        try:
            user = CustomUser.objects.get(email=username_or_email)
            if user.check_password(password):
                user = authenticate(username=user.username, password=password)
            else:
                user = None
        except CustomUser.DoesNotExist:
            user = None

    if user is not None:
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({
            "code": status.HTTP_200_OK,
            "message": "Successfully logged in",
            "userId": user.id,
            "Token": access_token
        }, status=status.HTTP_200_OK)
    
    return Response({
        "code": status.HTTP_400_BAD_REQUEST,
        "error": "Invalid username/email or password"
    }, status=status.HTTP_400_BAD_REQUEST)

# List all users (excluding the current user)
@api_view(['GET'])
def list_users(request):
    # Check permission
    if not IsAuthenticatedCustom().has_permission(request, None):
        return Response({
            "code": status.HTTP_401_UNAUTHORIZED,
            "error": "Authentication credentials were not provided"
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Get all users excluding the current user
    users = CustomUser.objects.exclude(id=request.user.id)
    serializer = SimpleUserSerializer(users, many=True)
    return Response({
        "code": status.HTTP_200_OK,
        "message": "Successfully retrieved all users",
        "data": serializer.data
    }, status=status.HTTP_200_OK)