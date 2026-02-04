from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models.signals import post_save, pre_save,post_delete
from django.dispatch import receiver
from django.db import transaction



from clients.models import Client
from products.models import Product

# Create your models here.


class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    payment_date = models.DateField(null=True, blank=True, help_text="The date the payment was received")
    # Added discount field (0 to 100)
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    # tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) 
    title = models.CharField(max_length=255, blank=True, help_text="A short title for this invoice")
    # Define the possible statuses
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('draft', 'Draft'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    
    
    
    
    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())
    
    @property
    def discounted_subtotal(self):
        return self.subtotal * (1 - (self.discount_percentage / Decimal('100')))
    
    
    # @property
    # def tax_amount(self):
    #     return self.discounted_subtotal * (self.tax_rate / Decimal('100'))
    @property
    def tax_amount(self):
        # Sum of all individual tax profile amounts
        return sum(tax.amount for tax in self.taxes.all())
    
    
    @property
    def total(self):
        return self.discounted_subtotal + self.tax_amount

class InvoiceTax(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='taxes', on_delete=models.CASCADE)
    name = models.CharField(max_length=50) # e.g., "VAT", "GST"
    rate = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def amount(self):
        return self.invoice.discounted_subtotal * (self.rate / Decimal('100'))
    
    
    

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    @property
    def total(self):
        return self.product.price * self.quantity
    
    
    
    
# --- Signals for Stock Management ---

@receiver(pre_save, sender=InvoiceItem)
def capture_old_quantity(sender, instance, **kwargs):
    """
    Before saving, check if the item already exists. 
    If it does, store the old quantity so we can calculate the difference.
    """
    if instance.pk:
        try:
            # We fetch the object directly from DB to get the current stored quantity
            old_obj = InvoiceItem.objects.get(pk=instance.pk)
            instance._old_quantity = old_obj.quantity
            instance._old_product = old_obj.product
        except InvoiceItem.DoesNotExist:
            instance._old_quantity = 0
    else:
        instance._old_quantity = 0

@receiver(post_save, sender=InvoiceItem)
def adjust_stock_on_save(sender, instance, created, **kwargs):
    """
    Adjusts product stock when an InvoiceItem is created or updated.
    """
    with transaction.atomic():
        product = instance.product
        
        if created:
            # New item: Decrease stock by total quantity
            product.stock -= instance.quantity
        else:
            # Updated item: Handle quantity changes or product swaps
            old_qty = getattr(instance, '_old_quantity', 0)
            old_product = getattr(instance, '_old_product', product)

            if old_product == product:
                # Same product, adjust by difference (new - old)
                diff = instance.quantity - old_qty
                product.stock -= diff
            else:
                # Product changed! Return stock to old product, take from new
                old_product.stock += old_qty
                old_product.save()
                product.stock -= instance.quantity
        
        product.save()

@receiver(post_delete, sender=InvoiceItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """
    When an item is removed from an invoice (or invoice deleted), return the stock.
    """
    product = instance.product
    product.stock += instance.quantity
    product.save()