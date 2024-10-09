
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from .models import InventoryItem
from django.core.cache import cache
from parameterized import parameterized

class InventoryAPITestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
       
        cls.login_url = reverse('login')
        cls.register_url = reverse('register')
        cls.item_url = reverse('create_item')

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", 
            password="testpassword", 
            email="test@example.com"
        )
        
       
        self.token = self.get_jwt_token()

        # Set the Authorization header for authenticated requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create a test inventory item
        self.item = InventoryItem.objects.create(
            name="Initial Item",
            description="Initial description",
            price=10.99
        )

    def get_jwt_token(self):
        # Helper function to obtain JWT token for test user
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        }, format='json')
        
        if response.status_code == status.HTTP_200_OK:
            return response.data['access']
        else:
            self.fail(f"Failed to obtain JWT token. Status code: {response.status_code}")

    def test_user_registration(self):
        # Test the user registration functionality
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "User registered successfully")

    def test_user_login_and_token_retrieval(self):
        # Test user login and token retrieval
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    @parameterized.expand([
        ("Test Item 1", "Description 1", 15.50),  # Valid price
        ("Test Item 2", "Description 2", 22.99),  # Valid price
    ])
    def test_create_inventory_item(self, name, description, price):
        # Test creating inventory items with different data
        print(f"Testing item creation: name={name}, description={description}, price={price}")  # Debug print
        response = self.client.post(self.item_url, {
            'name': name,
            'description': description,
            'price': price
        }, format='json')

        print(f"Response: {response.data}")  # Debug print
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], name)
        self.assertEqual(response.data['description'], description)
        self.assertEqual(float(response.data['price']), price)

    def test_create_inventory_item_with_invalid_price(self):
        # Test creating an inventory item with invalid price
        response = self.client.post(self.item_url, {
            'name': 'Invalid Item',
            'description': 'Invalid price test',
            'price': -10.00  # Invalid negative price
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_retrieve_inventory_item(self):
        # Test retrieving an inventory item
        url = reverse('retrieve_item', kwargs={'item_id': self.item.id})
        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Initial Item')

    def test_update_inventory_item(self):
        # Test updating an inventory item
        url = reverse('update_item', kwargs={'item_id': self.item.id})
        
        response = self.client.put(url, {
            'name': 'Updated Item',
            'description': 'Updated description',
            'price': 12.99
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Item')
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(float(response.data['price']), 12.99)

    def test_delete_inventory_item(self):
        # Test deleting an inventory item
        url = reverse('delete_item', kwargs={'item_id': self.item.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Item deleted successfully")

    def test_redis_caching_on_item_retrieval(self):
        # Test Redis caching behavior
        url = reverse('retrieve_item', kwargs={'item_id': self.item.id})
        
        # First request should be from the database, not cache
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Initial Item')

        # Simulate fetching the same item again (should be from cache)
        response_cached = self.client.get(url)
        self.assertEqual(response_cached.status_code, status.HTTP_200_OK)
        self.assertEqual(response_cached.data['name'], 'Initial Item')

        # Ensure we have cached the response correctly
        self.assertEqual(response_cached.data, response.data)  # Check if the data matches

    def test_unauthorized_access(self):
        # Test unauthorized access to inventory endpoints
        self.client.credentials()  # Clear credentials
        
        response = self.client.get(self.item_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
