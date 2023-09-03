from django.urls import path
from . import views


urlpatterns = [
    path('api-item/', views.Home.as_view()),
    path('api-item/<str:pk>/', views.Detail.as_view()),
    path('<str:pk>/add_to_cart/', views.add_to_cart),
    path('api-cart/', views.cart_view),
    path('<str:pk>/rmone_from_cart/', views.remove_one_item_from_cart),
    path('<str:pk>/rm_from_cart/', views.remove_from_cart),
    path('api-search/', views.PostSearch.as_view()),
    path('wish/', views.WishList().as_view()),
    path('<str:pk>/wish/', views.add_wish),
]