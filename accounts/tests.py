from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }

    def test_valid_registration(self):
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_missing_field_registration(self):
        # Missing password
        data = self.user_data.copy()
        del data['password']
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        
        # Output the errors
        print(response.data)

    def test_duplicate_user_registration(self):
        # First registration
        self.client.post(self.url, self.user_data)
        
        # Attempt to register again with the same username
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # Still only one user should exist
        
        # Output the errors
        print(response.data)

    def test_password_hashing(self):
        response = self.client.post(self.url, self.user_data)
        user = User.objects.latest('id')
        self.assertNotEqual(user.password, self.user_data['password'])  # Ensure password is not plain text
        self.assertTrue(user.check_password(self.user_data['password']))  # Check correct password is hashed

