from django.test import TestCase
from django.urls import reverse
from rest_framework import status

# Test class for registration API
class RegistrationAPITestCase(TestCase):
    def setUp(self):
        # Common headers for all requests
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'http://localhost:3000',
            'Referer': 'http://localhost:3000/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        self.url = reverse('register')  # Assuming 'register' is the name of the registration URL pattern

    def test_registration_with_valid_data(self):
        data = {
            "username": "02022202_OLV",
            "email": "amanra@gmail.com",
            "password": "02022022002_OLV"
        }
        response = self.client.post(self.url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Expected 201, got {response.status_code}")

    def test_registration_with_duplicate_username(self):
        # First registration to create duplicate case
        self.client.post(self.url, {
            "username": "02022022002_OLV",
            "email": "uniqueemail@gmail.com",
            "password": "02022022002_OLV"
        }, content_type='application/json', **self.headers)
        
        # Duplicate username test
        data = {
            "username": "02022022002_OLV",
            "email": "newemail@gmail.com",
            "password": "02022022002_OLV"
        }
        response = self.client.post(self.url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}")

    def test_registration_with_duplicate_email(self):
        # First registration to create duplicate case
        self.client.post(self.url, {
            "username": "firstuser",
            "email": "amangora@gmail.com",
            "password": "password123"
        }, content_type='application/json', **self.headers)
        
        # Duplicate email test
        data = {
            "username": "newuser123",
            "email": "amangora@gmail.com",
            "password": "newpassword123"
        }
        response = self.client.post(self.url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}")

    def test_registration_with_invalid_email_format(self):
        data = {
            "username": "validuser",
            "email": "invalidemail",
            "password": "validpassword123"
        }
        response = self.client.post(self.url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}")

    def test_registration_with_missing_fields(self):
        data = {
            # Missing username
            "email": "validuser123@gmail.com",
            "password": "validpassword123"
        }
        response = self.client.post(self.url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}")
