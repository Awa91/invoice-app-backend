from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


from users.user_owned_view_set import UserOwnedViewSet
from .models import Invoice
from .serializers import  InvoiceSerializer
# Create your views here.



class InvoiceViewSet(UserOwnedViewSet):
    # Prefetch both taxes and items (and item products) for performance
    queryset = Invoice.objects.all().prefetch_related('items__product', 
    'taxes',
    'client').order_by('-date')
    serializer_class = InvoiceSerializer
    
    
    # Enable Filtering, Searching, and Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Fields for ?status=paid
    filterset_fields = ['status']
    
    # Fields for ?search=Title
    search_fields = ['title', 'client__name', 'notes']
    
    
    def perform_create(self, serializer):
        # Automatically assign the logged-in user to the invoice
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Ensure users only see their own invoices
        return self.queryset.filter(user=self.request.user)
    
    
    