from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Item
from django.contrib.auth.models import User


class ItemViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a category
        cls.category = Category.objects.create(
            name="Electronics", description="All electronic items"
        )

        # Create items
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
        # Authenticate and obtain token for each test
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "user", "password": "password"},
            format="json",
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    def test_list_items(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Expect two items returned

    def test_list_items_unauthenticated(self):
        self.client.credentials()  # Remove any authentication credentials
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_items_by_stock(self):
        response = self.client.get(self.list_url, {"in_stock": "20"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Laptop")

    def test_filter_items_by_category(self):
        response = self.client.get(self.list_url, {"category": self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both items should match the category

    def test_invalid_filter(self):
        # This test needs to ensure no item with the exact price of 1000 exists
        response = self.client.get(self.list_url, {"price": "1000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Expect no items to match this filter

    def test_order_items_by_price(self):
        # Assuming that ordering by price ascending would have 'Smartphone' first if it's cheaper
        response = self.client.get(self.list_url, {"ordering": "price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Smartphone")

    def test_invalid_data_type_filter(self):
        response = self.client.get(self.list_url, {"in_stock": "twenty"})
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )  # Expect bad request due to invalid data type

    def test_create_item_authenticated(self):
        self.client.login(username="user", password="password")
        category = Category.objects.get(id=self.category.id)
        post_data = {
            "SKU": "NEW123",
            "name": "New Item",
            "category": category.id,  # Use the re-fetched category ID
            "price": 199.99,
            "units": "pieces",
            "in_stock": 10,
            "available_stock": 10,
        }
        post_response = self.client.post(self.list_url, post_data, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Item.objects.filter(SKU="NEW123").exists())
        new_item = Item.objects.get(SKU="NEW123")
        self.assertEqual(new_item.category.id, category.id)

    def test_delete_item_unauthenticated(self):
        self.client.credentials()  # Clear any credentials
        delete_response = self.client.delete(
            reverse("item-detail", args=[self.item1.id])
        )
        self.assertEqual(delete_response.status_code, status.HTTP_401_UNAUTHORIZED)
