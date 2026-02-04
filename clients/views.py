from users.user_owned_view_set import UserOwnedViewSet
from .models import Client
from .serializers import ClientSerializer 



        

class ClientViewSet(UserOwnedViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer