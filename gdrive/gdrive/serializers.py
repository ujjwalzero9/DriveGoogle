from rest_framework import serializers
from .models import User, Entity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'token', 'name', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'read_only': True}
        }

    def create(self, validated_data):
        # Create user and automatically generate token
        user = User.objects.create(**validated_data)
        user.generate_token()
        user.save()
        return user


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'folder_path', 'name', 'content_type', 'hashpath',
                  'is_folder', 'parent_folder', 'user_id', 'url']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
