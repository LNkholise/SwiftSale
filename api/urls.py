from django.urls import path
from .views import ProductViewSet, buy_request

urlpatterns = [
    path('products/', ProductViewSet.as_view({'get':'list','post': 'create'}), name='product-list'),
    path('buy/', buy_request, name='buy-request'),
]

