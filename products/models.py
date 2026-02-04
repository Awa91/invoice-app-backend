from django.db import models
from django.conf import settings

# Create your models here.
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True) # Automatically updates on save
    stock = models.PositiveIntegerField(default=0)
    initial_stock = models.PositiveIntegerField(default=0) # New Field
    
    
    class Meta:
        ordering = ['-updated_at'] # Optional: Show recently modified first
        

    def save(self, *args, **kwargs):
        # Automatically set initial_stock to match stock on first creation
        if not self.pk and self.initial_stock == 0:
            self.initial_stock = self.stock
        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.name
    
    
class StockHistory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adjustment = models.IntegerField()  # e.g., +10 or -5
    new_stock = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']