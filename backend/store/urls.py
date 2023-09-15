from django.urls import path
from . import views


urlpatterns = [
    path('api-item/', views.Home.as_view()),
    path('api-item/<str:pk>/', views.Detail.as_view()),
    path('<str:pk>/add_to_cart/', views.add_to_cart),
    path('api-cart/', views.cart_view),
    path('<str:pk>/rmone_from_cart/', views.remove_one_item_from_cart),
    path('<str:pk>/rm_from_cart/', views.remove_from_cart),
    path('api-wish/', views.WishList().as_view()),
    path('<str:pk>/api-wish/', views.add_wish),
    path('api-checkout/', views.CheckoutView.as_view()),
    path("oreder_ordered/", views.oreder_ordered),

    #stripe
    path('config/', views.stripe_config),
    path('payment_success/', views.payment_success),
    path('create-checkout-session/', views.create_checkout_session), # new
    path('cancel/', views.payment_cancel),
]