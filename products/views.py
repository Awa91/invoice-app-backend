from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import pagination, filters


from users.user_owned_view_set import UserOwnedViewSet
from .models import Product,StockHistory
from .serializers import ProductSerializer, StockHistorySerializer
# Create your views here.


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 20  # Items per page
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    

class ProductViewSet(UserOwnedViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description'] # Enables search via ?search=query
    
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Scenario: If someone tries to reduce stock below zero
        new_stock = request.data.get('stock')
        if new_stock is not None and int(new_stock) < 0:
            return Response(
                {"error": "Operation not allowed. Product is out of stock."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().update(request, *args, **kwargs)
    
    
    # To implement a formal Stock Adjustment system, we need to move away from simply overwriting the stock field and instead create a "transaction" style update. This ensures data integrity and allows for auditing (reasons for change).
    # We need to add a custom action to the ProductViewSet to handle adjustments specifically.
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        product = self.get_object()
        adjustment = int(request.data.get('adjustment', 0)) # Integer: e.g., 5 or -3
        reason = request.data.get('reason', 'Manual Adjustment') # String

        if adjustment is None:
            return Response({"error": "Adjustment value required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_stock = product.stock + adjustment
            if new_stock < 0:
                return Response({"error": "Stock cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)
            
            product.stock = new_stock
            product.save()
            
            # Create the history record
            StockHistory.objects.create(
              product=product,
              user=request.user,
              adjustment=adjustment,
              new_stock=new_stock,
              reason=reason)
            
            
            # Note: In a production app, you'd create a StockLog record here
            return Response(ProductSerializer(product).data)
        except ValueError:
            return Response({"error": "Invalid adjustment number"}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        product = self.get_object()
        history = product.history.all()
        serializer = StockHistorySerializer(history, many=True)
        return Response(serializer.data)
        