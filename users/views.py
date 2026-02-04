from rest_framework import generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.decorators import action



from .models import CustomUser
from .serializers import RegisterSerializer,UserSerializer


# --- Helper function to get tokens for a user ---
def get_tokens_for_user(user):
    """
    Manually generate access and refresh tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# --- Registration API View ---
class RegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate and return JWT tokens immediately upon successful registration
        tokens = get_tokens_for_user(user)
        
        return Response({
            "user_email": user.email,
            "access_token": tokens['access'],
            "refresh_token": tokens['refresh']
        }, status=status.HTTP_201_CREATED)

# --- REMOVE LoginView ---
# The JWT TokenObtainPairView handles login logic automatically.



# This view handles the user's basic account and profile data.
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CustomUser. 
    The 'me' action provides the /api/users/me/ endpoint.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        # We fetch the profile related to the current user
        user = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            # Allows updating the User and nested Profile
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# To achieve your goal of deleting a user account while keeping the profile (setting user_id to null), 
# you need to create a custom action in your UserViewSet.

    @action(detail=False, methods=['delete'], url_path='delete-account')
    def delete_account(self, request):
        """
        Deletes the authenticated user's account. 
        Because UserProfile has on_delete=models.SET_NULL, 
        the profile will persist with user=None.
        """
        user = request.user
        user.delete()
        return Response(
            {"detail": "Account deleted successfully. Profile data retained."}, 
            status=status.HTTP_204_NO_CONTENT
        )

