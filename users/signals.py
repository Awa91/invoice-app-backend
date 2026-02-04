# We will consolidate the signals into one file. This ensures that 
# every time a CustomUser is created, it gets a "bucket" for profile 
# info (phone, avatar) and a "bucket" for business preferences (tax, 
# currency).

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile
from usersettings.models import UserSettings




@receiver(post_save, sender=CustomUser)
def manage_user_extras(sender, instance, created, **kwargs):
    if created:
        # Create both Profile and Settings at once
        UserProfile.objects.create(user=instance)
        UserSettings.objects.create(user=instance)
    else:
        # Ensure they are saved if they exist
        if hasattr(instance, 'profile'):
            instance.profile.save()
        if hasattr(instance, 'settings'):
            instance.settings.save()
            
            
# @receiver(post_save, sender=CustomUser)
# def create_user_related_entities(sender, instance, created, **kwargs):
#     if created:
#         # Create both Profile and Settings simultaneously
#         UserProfile.objects.create(user=instance)
#         UserSettings.objects.create(user=instance)

# @receiver(post_save, sender=CustomUser)
# def save_user_related_entities(sender, instance, **kwargs):
#     # Save both to ensure data consistency
#     instance.profile.save()
#     if hasattr(instance, 'settings'):
#         instance.settings.save()