from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ['image', 'user_u', 'user']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username']