from rest_framework import serializers
from .models import Expense



# We use a ModelSerializer to convert the data into the JSON format our Flutter app consumes.

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'amount', 'category', 
            'date', 'is_recurring', 'frequency'
        ]
        read_only_fields = ['id']

    # def create(self, validated_data):
    #     # Automatically assign the logged-in user to the expense
    #     user = self.context['request'].user
    #     return Expense.objects.create(user=user, **validated_data)
    
    # REMOVE the create method entirely, or simplify it to this:
    def create(self, validated_data):
        return Expense.objects.create(**validated_data)