"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings



from clients.views import ClientViewSet
from products.views import ProductViewSet
from invoices.views import InvoiceViewSet
from users.views import UserViewSet
from usersettings.views import UserSettingsViewSet
from expenses.views import ExpenseViewSet


router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'users', UserViewSet, basename='user')
router.register(r'usersettings', UserSettingsViewSet, basename='usersettings')
router.register(r'expenses', ExpenseViewSet, basename='expense')





urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the URLs from the router applications
     path('api/', include(router.urls)),
     # Include the URLs from the 'users' application
    path('api/', include('users.urls')),
    
   
]

# This allows Flutter to load images via http://127.0.0.1:8000/media/logos/image.png
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)