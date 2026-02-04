from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Sum


from .models import Expense
from .serializers import ExpenseSerializer



# Create your views here.



# We will create a custom pagination class that uses Django's Sum function. This ensures that the calculation happens at the database level, which is much faster than calculating it in Flutter.
class AggregatedExpensePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    
    def get_paginated_response(self, data):
        # We access the filtered queryset we attached in the view
        filtered_qs = getattr(self.request, 'filtered_queryset', None)
        
        total_sum = 0
        if filtered_qs is not None:
            total_sum = filtered_qs.aggregate(total=Sum('amount'))['total'] or 0
            

        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_aggregated_amount': float(total_sum), # Accurate total for Flutter
            'results': data
        })
        


# A ModelViewSet provides the full CRUD (Create, Read, Update, Delete) suite. We override get_queryset to ensure users can only see their own expenses.



    
    
class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing, creating, and managing business expenses.
    Supports:
    - User-specific data isolation
    - Search by title and category
    - Sorting by date and amount
    - Date range filtering
    - Aggregated totals in pagination metadata
    """
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AggregatedExpensePagination
    
    # Enable standard filtering backends
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    # Configure searchable and sortable fields
    search_fields = ['title', 'category']
    ordering_fields = ['date', 'amount']
    ordering = ['-date']  # Default: Most recent expenses first

    def get_queryset(self):
        """
        Returns expenses belonging only to the authenticated user.
        Applies manual date range filters if provided in query parameters.
        """
        user = self.request.user
        queryset = Expense.objects.filter(user=user)

        # Handle Date Range Filtering (e.g., ?start_date=2024-01-01&end_date=2024-03-31)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Overrides the list method to capture the filtered queryset 
        before pagination. This allows the custom paginator to 
        calculate the sum of the filtered results.
        """
        # 1. Apply all filters (search, ordering, date range)
        queryset = self.filter_queryset(self.get_queryset())
        
        # 2. Store this specific queryset on the request object 
        # so AggregatedExpensePagination can access it.
        request.filtered_queryset = queryset

        # 3. Proceed with standard DRF pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback if pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Ensures the newly created expense is linked to the 
        authenticated user making the request.
        """
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Optional: Custom logic before deletion if needed.
        Currently performs a standard delete.
        """
        return super().destroy(request, *args, **kwargs)