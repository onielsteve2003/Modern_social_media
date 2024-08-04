from rest_framework import serializers
from profiles.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'fullname', 'email', 'dob', 'password')

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            fullname=validated_data['fullname'],
            email=validated_data['email'],
            dob=validated_data['dob'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        # Handle updates for existing users
        instance.username = validated_data.get('username', instance.username)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.email = validated_data.get('email', instance.email)
        instance.dob = validated_data.get('dob', instance.dob)

        # Only update password if provided
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance
    

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'fullname')

class DetailedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'fullname', 'email')