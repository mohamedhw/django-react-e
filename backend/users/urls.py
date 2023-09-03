from django.urls import path
from . import views

urlpatterns = [
    path('api-profile/', views.ProfileView.as_view()),
    path('csrfcookie/', views.GetCsrfCookie.as_view(), name='csrfcookie'),
    path('checkauth/', views.CheckAuth.as_view(), name='profile'),
    path('api-register/', views.RegisterUser.as_view(),),
    path('api-login/', views.LoginUser.as_view(),),
    path('api-logout/', views.LogoutUser.as_view(),),
    path('api-profile-update/', views.UpdateProfileView.as_view()),
    path('api-profile-user-update/', views.UpdateUserView.as_view()),
    ]