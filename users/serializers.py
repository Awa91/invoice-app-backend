from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import UserProfile
# from usersettings.models import UserSettings
from usersettings.serializers import UserSettingsSerializer


# No need to import authenticate or other token logic

User = get_user_model() 




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'username']
        

# class UserSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserSettings
#         fields = ['theme', 'currency',  'logo', 'account_number', 'account_name']
        
   
# This ensures the UserSerializer can see the profile and settings data.

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'profile', 'settings']
        
         
        

# class UserSettingsSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = UserSettings
#         fields = ['theme', 'currency', 'tax', 'logo', 'account_number', 'account_name']
        


# --- Registration Serializer (Simplified) ---
class RegisterSerializer(serializers.ModelSerializer):
    # Added source='email' for consistency, though not strictly needed here
    email = serializers.EmailField(required=True) 
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)
    
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'profile', 'settings')

    def validate(self, data):
        """
        Check that the two password fields match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        # Remove the confirmation field before creating the user
        validated_data.pop('password_confirm') 
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# --- REMOVE LoginSerializer ---
# The Simple JWT TokenObtainPairSerializer handles login logic automatically.

