from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # Handles login (email/password -> access/refresh token)
    TokenRefreshView,    # Handles refreshing the access token
)

from .views import  RegistrationView, UserViewSet # Only need RegistrationView



router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


# The API URLs are now determined automatically by the router.
urlpatterns = [
    # Authentication Endpoints using Simple JWT
    path('auth/register/', RegistrationView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # JWT Login
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # JWT Refresh
   
    # User endpoints (includes /api/users/me/ and /api/users/delete-account/)
    path('', include(router.urls)),
 
]