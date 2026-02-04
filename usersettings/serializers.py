from rest_framework import serializers
import json


from .models import   UserSettings

# class UserSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserSettings
#         fields = ['theme', 'currency', 'invoice_footer', 'tax', 'logo', 'account_number', 'account_name']

class UserSettingsSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserSettings
        fields = [
            'id', 'user', 'theme', 'currency', 'invoice_footer', 
            'tax_profiles', 'logo', 'account_number', 
            'account_name', 'company_name','issuer_name', 'issuer_title', 'signature','brand_color','locale'
        ]
        
    # def get_logo(self, obj):
    #     if obj.logo:
    #         # Ensures the full URL (http://domain.com/media/...) is sent to Flutter
    #         request = self.context.get('request')
    #         return request.build_absolute_uri(obj.logo.url)
    #     return None
    
    
  # 2. Add this method to handle the string-to-list conversion
    def to_internal_value(self, data):
        # Create a mutable copy of the data (QueryDicts are immutable)
        if hasattr(data, 'dict'):
            data = data.dict()
        else:
            data = dict(data)

        # If tax_profiles is a string, parse it as JSON
        tax_profiles = data.get('tax_profiles')
        if isinstance(tax_profiles, str):
            try:
                data['tax_profiles'] = json.loads(tax_profiles)
            except (ValueError, TypeError):
                # Fallback or let DRF handle the error
                pass
                
        return super().to_internal_value(data)
    
    
    # This ensures 'logo' is a full URL
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.logo:
            # Get the request from the context to build the absolute URI
            request = self.context.get('request')
            if request is not None:
                representation['logo'] = request.build_absolute_uri(instance.logo.url)
        return representation