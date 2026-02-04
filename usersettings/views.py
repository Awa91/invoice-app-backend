from rest_framework import viewsets, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import  UserSettings
from .serializers import (
     UserSettingsSerializer
)

class UserSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # MultiPartParser handles file uploads, JSONParser handles standard data
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)
    

    def get_queryset(self):
        # Ensure user only sees their own settings
        return UserSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically link the settings to the logged-in user
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Custom endpoint to get or update the current user's settings 
        without needing the specific ID.
        URL: /api/usersettings/me/
        """
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
            
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




