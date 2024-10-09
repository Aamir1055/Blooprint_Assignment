from django.urls import path
from .views import CreateItemView, RetrieveItemView, UpdateItemView, DeleteItemView,RegisterView,CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)





urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('items/', CreateItemView.as_view(), name='create_item'),
    path('items/<int:item_id>/', RetrieveItemView.as_view(), name='retrieve_item'),
    path('item/<int:item_id>/update/', UpdateItemView.as_view(), name='update_item'),
    path('item/<int:item_id>/delete/', DeleteItemView.as_view(), name='delete_item'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
