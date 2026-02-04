from rest_framework import serializers
from .models import  Product,StockHistory


class ProductSerializer(serializers.ModelSerializer):
    # Make initial_stock read-only so users don't manually cheat the percentage
    initial_stock = serializers.IntegerField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True) # Include in output
    
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'initial_stock', 'updated_at']
        
    
    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        # If the instance already exists (Update), make stock read_only
        if self.instance is not None:
            extra_kwargs['stock'] = {'read_only': True}
        return extra_kwargs
        
    
    def validate_stock(self, value):
        """
        Check that stock is never negative.
        """
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value
    
    
    
    
class StockHistorySerializer(serializers.ModelSerializer):
    # username = serializers.CharField(source='user.profile.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    
    class Meta:
        model = StockHistory
        fields = ['id', 'adjustment', 'new_stock', 'reason', 'created_at', 'email']
        
        
        
        