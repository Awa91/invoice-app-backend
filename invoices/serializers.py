from rest_framework import serializers
from django.db import transaction

from products.models import Product
from products.serializers import ProductSerializer
from clients.models import Client
from clients.serializers  import ClientSerializer
from .models import  Invoice, InvoiceItem, InvoiceTax


class InvoiceItemSerializer(serializers.ModelSerializer):
    item_total = serializers.ReadOnlyField(source='total')
    # Use nested representation for Product on read
    product = ProductSerializer(read_only=True)
    # Use ID for writing
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'product_id', 'quantity', 'item_total']
        
    
    def validate_quantity(self, value):
        """
        Check that the quantity is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be less than zero.")
        return value
    
    

class InvoiceTaxSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = InvoiceTax
        fields = ['id', 'name', 'rate', 'amount']
        read_only_fields = ['amount']    

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    taxes = InvoiceTaxSerializer(many=True)
    subtotal = serializers.ReadOnlyField() # Useful for the UI
    total = serializers.ReadOnlyField()
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source='client', write_only=True
    )
    tax_amount = serializers.ReadOnlyField()
    
    

    class Meta:
        model = Invoice
        fields = ['id', 'title','client', 'client_id', 'date', 'due_date', 
                  'notes', 
                  'items','status','subtotal','discount_percentage',
                  'taxes','tax_amount',
                  'total','payment_date']

    
    def validate_discount_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount rate must be between 0 and 100.")
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        taxes_data = validated_data.pop('taxes', [])
        # discount_percentage is now included in validated_data automatically
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        for tax in taxes_data:
            InvoiceTax.objects.create(invoice=invoice, **tax)
            
        return invoice
    
    
    
    
    
    
    @transaction.atomic
    def update(self, instance, validated_data):
        # 1. Extract the nested items data
        items_data = validated_data.pop('items', None)
        taxes_data = validated_data.pop('taxes', None)
        
        # 2. Update the main Invoice instance fields (date, notes, client, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 3. Handle Nested Items logic
        # if items_data is not None:
        #     # OPTION A: Delete-and-Recreate (Simple & Clean)
        #     # This is effective if you don't need to preserve specific Item IDs
        #     instance.items.all().delete()
        #     for item_data in items_data:
        #         InvoiceItem.objects.create(invoice=instance, **item_data)
        
        # return instance
        
        # if items_data is not None:
        #     keep_items = []
        #     for item_data in items_data:
        #         # Assuming your items have an 'id' in the payload for updates
        #         item_id = item_data.get('id')
        #         if item_id:
        #             item = InvoiceItem.objects.filter(id=item_id, invoice=instance).first()
        #             if item:
        #                 for attr, value in item_data.items():
        #                     setattr(item, attr, value)
        #                 item.save()
        #                 keep_items.append(item.id)
        #         else:
        #             new_item = InvoiceItem.objects.create(invoice=instance, **item_data)
        #             keep_items.append(new_item.id)
            
        #     # Delete items that weren't in the payload
        #     instance.items.exclude(id__in=keep_items).delete()

        # return instance
        
        if items_data is not None:
            self._sync_nested_relation(instance.items, items_data, InvoiceItem)
        if taxes_data is not None:
            self._sync_nested_relation(instance.taxes, taxes_data, InvoiceTax)

        return instance

    def _sync_nested_relation(self, manager, data_list, model_class):
        """Helper to Create, Update, or Delete nested records."""
        keep_ids = []
        for data in data_list:
            obj_id = data.get('id')
            if obj_id:
                obj = manager.filter(id=obj_id).first()
                if obj:
                    for attr, value in data.items():
                        setattr(obj, attr, value)
                    obj.save()
                    keep_ids.append(obj.id)
            else:
                new_obj = model_class.objects.create(invoice=manager.instance, **data)
                keep_ids.append(new_obj.id)
        
        manager.exclude(id__in=keep_ids).delete()
