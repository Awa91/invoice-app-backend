# To integrate UserProfile and UserSettings while ensuring data 
# retention (preventing deletion when a user is removed), we need to 
# change the on_delete logic. By default, CASCADE deletes the child when the parent is deleted. To keep the profile and settings, we use models.SET_NULL or models.PROTECT.

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


# --- Custom User Manager ---
class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

# --- Custom User Model ---
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # No required fields for superuser creation since email is the UNAME_FIELD

    objects = CustomUserManager()

    def __str__(self):
        return self.email








class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, 
            # on_delete=models.CASCADE, 
            on_delete=models.SET_NULL,   # When a user account is deleted, the profile and settings remain in the database with user_id = null.
        null=True,
        related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    # You can add more fields here (e.g., avatar, address)
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        # return f"{self.user.email}'s Profile"
        return f"{self.user.email if self.user else 'Deleted User'}'s Profile"

# Signals to automatically create/update UserProfile when User is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # We can derive a default username from the email 
        # or leave it for the user to fill later.
        default_username = instance.email.split('@')[0]
        UserProfile.objects.create(user=instance, username=default_username)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()