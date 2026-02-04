from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
from usersettings.models import UserSettings
# Register your models here.



# These allow you to edit Profile and Settings on the same page as the User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserSettingsInline(admin.StackedInline):
    model = UserSettings
    can_delete = False
    verbose_name_plural = 'Settings'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Use the inlines defined above
    inlines = (UserProfileInline, UserSettingsInline)
    
    # Control the list view
    list_display = ('email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    # These fieldsets are required because CustomUser doesn't have a 'username'
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password'),
        }),
    )

# Also register them separately if you want to access them individually
admin.site.register(UserProfile)
admin.site.register(UserSettings)