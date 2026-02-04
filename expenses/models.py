# To complete the backend for your financial ecosystem,
# we need to implement the Django logic that handles categorization, recurring status, and user-based filtering.

from django.db import models
from django.conf import settings

# Create your models here.





# This model includes the logic for categories and recurring flags that our Flutter AddExpenseDialog expects.

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('marketing', 'Marketing'),
        ('software', 'Software'),
        ('travel', 'Travel'),
        ('equipment', 'Equipment'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]

    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField()
    
    # Recurring Logic
    is_recurring = models.BooleanField(default=False)
    frequency = models.CharField(
        max_length=10, 
        choices=FREQUENCY_CHOICES, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.category})"
    


