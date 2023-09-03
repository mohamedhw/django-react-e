from django.contrib.auth import get_user_model
from rest_framework import generics
from .serializers import UserProfileSerializer, UserSerializer
from .models import Profile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from django.contrib import auth
from rest_framework.parsers import FileUploadParser

User = get_user_model()


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ProfileView(APIView):
    def get(self, request, format=None):
        user = self.request.user
        username = user.username
        user = User.objects.get(id=user.id)
        profile = Profile.objects.get(user=user)
        user_profile = UserProfileSerializer(profile)

        return Response({'profile': user_profile.data, 'username':str(username)})

@method_decorator(ensure_csrf_cookie, name='dispatch')
class UpdateUserView(APIView):
    def put(self, *args, **kwargs):
        try:
            data = self.request.data
            new_username = data['username'] # new username
            user_now = self.request.user # user
            username = user_now.username # username
            user = User.objects.get(id=user_now.id)
            user.username = new_username
            user.save()
            return Response({'success': "updated successfully", 'username':str(user.username)})
        except:
            return Response({"error": "could not update this username!"})
        
@method_decorator(ensure_csrf_cookie, name='dispatch')
class UpdateProfileView(generics.UpdateAPIView):
    parser_classes = (FileUploadParser,)
    queryset =  Profile.objects.all()
    serializer_class = UserProfileSerializer()

    def get_object(self, *args, **kwargs):
        profile = Profile.objects.get(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        instance = self.get_object(user=request.user)
        serializer = UserProfileSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "profile image updated successfully"})
        else:
            return Response({"message": "failed", "details": serializer.errors})

class UserProfileAPIView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()


class UserAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()



@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCsrfCookie(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        return Response({'success': 'CSRF cookie set'})


class LogoutUser(APIView):

    def post(self, request, format=None):
        try:
            auth.logout(request)
            return Response({"success": "loged out successfully!"})
        except:
            return Response({"error": "some thing went wrong loginout!"})


@method_decorator(csrf_protect, name='dispatch')
class LoginUser(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request, format=None):
        data = self.request.data
        username = data['username']
        password = data['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return Response({"success": "login successfully"})
        else:
            return Response({"error": "some thing went wrong!"})


@method_decorator(csrf_protect, name='dispatch')
class CheckAuth(APIView):
    def get(self, request, format=None):
        is_authenticated = User.is_authenticated
        if is_authenticated:
            return Response({"isAuthenticated": "success"})
        else:
            return Response({"isAuthenticated": "error"})
        
@method_decorator(csrf_protect, name='dispatch')
class RegisterUser(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data

        username = data['username']
        password = data['password']
        password2 = data['password2']

        if password == password2:
            # if User.objects.filter(username==username).exists():
            #     return Response({"error": "this username already exists!"})
            # else:
            if len(password) < 6:
                return Response({"error": "password is to short!"})
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                # user = User.objects.get(username=username)

                return Response({"success": "user created successfully!"})
        else:
            return Response({"error": "password do not match!"})