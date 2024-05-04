from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Item
from django.contrib.auth.models import User


class ItemViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up initial data for tests: categories and items
        cls.category = Category.objects.create(
            name="Electronics", description="All electronic items"
        )
        cls.item1 = Item.objects.create(
            SKU="ABC123",
            name="Laptop",
            category=cls.category,
            description="High-performance laptop",
            price=999.99,
            units="pieces",
            in_stock=20,
            available_stock=15,
        )
        cls.item2 = Item.objects.create(
            SKU="XYZ789",
            name="Smartphone",
            category=cls.category,
            price=499.99,
            units="pieces",
            in_stock=50,
            available_stock=45,
        )
        cls.list_url = reverse("item-list")
        cls.user = User.objects.create_user(username="user", password="password")

    def setUp(self):
        # Authenticate user before each test
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "user", "password": "password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])

    def test_list_items(self):
        # Verify that listing items returns correct count and status
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_items_unauthenticated(self):
        # Ensure authentication is required to list items
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_items_by_stock(self):
        # Filter items by stock and verify correct item is returned
        response = self.client.get(self.list_url, {"in_stock": "20"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Laptop")

    def test_filter_items_by_category(self):
        # Filter items by category and check both items are returned
        response = self.client.get(self.list_url, {"category": self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_invalid_filter(self):
        # Test filtering with a non-matching price
        response = self.client.get(self.list_url, {"price": "1000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_order_items_by_price(self):
        # Test ordering items by price
        response = self.client.get(self.list_url, {"ordering": "price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Smartphone")

    def test_invalid_data_type_filter(self):
        # Test handling of invalid data types in filters
        response = self.client.get(self.list_url, {"in_stock": "twenty"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_authenticated(self):
        # Test creation of an item with authentication
        self.client.login(username="user", password="password")
        post_response = self.client.post(
            self.list_url,
            {
                "SKU": "NEW123",
                "name": "New Item",
                "category": self.category.id,
                "price": 199.99,
                "units": "pieces",
                "in_stock": 10,
                "available_stock": 10,
            },
            format="json",
        )
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Item.objects.filter(SKU="NEW123").exists())

    def test_delete_item_unauthenticated(self):
        # Test deletion of an item without authentication
        self.client.credentials()
        delete_response = self.client.delete(
            reverse("item-detail", args=[self.item1.id])
        )
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)
