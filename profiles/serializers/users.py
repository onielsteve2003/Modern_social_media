from rest_framework import serializers
from profiles.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    # Use `write_only=True` for password field only on creation/updating
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, required=False)

    class Meta:
        model = CustomUser
        # Include fields as necessary
        fields = ('id', 'username', 'fullname', 'email', 'dob', 'password')  # Include 'id' if needed

    def create(self, validated_data):
        # Ensure the password is set properly
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