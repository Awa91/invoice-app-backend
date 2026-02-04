from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Expense
import datetime

# Create your tests here.


User = get_user_model()

class ExpenseSecurityTests(APITestCase):
    def setUp(self):
        # Create two separate users
        self.user_a = User.objects.create_user(username='user_a', password='password123')
        self.user_b = User.objects.create_user(username='user_b', password='password123')
        
        # Create an expense for User A
        self.expense_a = Expense.objects.create(
            user=self.user_a,
            title="User A Software",
            amount=50.00,
            category="software",
            date=datetime.date.today()
        )
        
        # Create an expense for User B
        self.expense_b = Expense.objects.create(
            user=self.user_b,
            title="User B Marketing",
            amount=100.00,
            category="marketing",
            date=datetime.date.today()
        )
        
        self.url = reverse('expense-list') # Matches router basename='expense'

    def test_user_can_only_see_own_expenses(self):
        """Verify User A cannot see User B's expenses in the list view"""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that only 1 expense is returned (User A's)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "User A Software")

    def test_user_cannot_access_others_detail(self):
        """Verify User A gets a 404 when trying to GET User B's specific ID"""
        self.client.force_authenticate(user=self.user_a)
        detail_url = reverse('expense-detail', kwargs={'pk': self.expense_b.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_expense_creation_assigns_correct_user(self):
        """Verify that when User A creates an expense, it is owned by User A"""
        self.client.force_authenticate(user=self.user_a)
        data = {
            "title": "New Equipment",
            "amount": "250.00",
            "category": "equipment",
            "date": "2024-01-01"
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_expense = Expense.objects.get(id=response.data['id'])
        self.assertEqual(new_expense.user, self.user_a)

    def test_user_cannot_delete_others_expense(self):
        """Verify User A cannot delete User B's expense"""
        self.client.force_authenticate(user=self.user_a)
        detail_url = reverse('expense-detail', kwargs={'pk': self.expense_b.id})
        response = self.client.delete(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify expense still exists in DB
        self.assertTrue(Expense.objects.filter(id=self.expense_b.id).exists())