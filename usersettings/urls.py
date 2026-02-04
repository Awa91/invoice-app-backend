from django.urls import path, include

from .views import  UserSettingsViewSet  # Only need RegistrationView


# The API URLs are now determined automatically by the router.
urlpatterns = [
   
   
    path('usersettings/me/', UserSettingsViewSet, basename='settings'),
 
]