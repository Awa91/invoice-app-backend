from django.db import models
from django.conf import settings



class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
    null=True,
    on_delete=models.SET_NULL, # When a user account is deleted, the profile and settings remain in the database with user_id = null.
    related_name='settings')
    theme = models.CharField(max_length=20, default='light')
    currency = models.CharField(max_length=10, default='USD')
    invoice_footer = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True) # Added
    brand_color = models.CharField(max_length=9, default="#263238") # Hex with Alpha
      # Store as JSON to easily handle lists like ["VAT", "Service Tax"]
    locale = models.CharField(max_length=10, default='en_US')  # Add this
    tax_profiles = models.JSONField(default=list)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    issuer_name = models.CharField(max_length=100, blank=True, null=True)
    issuer_title = models.CharField(max_length=100, blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    
    
    def __str__(self):
        return f"Settings for {self.user.email if self.user else 'Archived Data'}"



# To implement the UserSettings functionality, we need a serializer 
# that handles file uploads (for the logo) and a viewset that ensures each user can only access and modify their own settings.