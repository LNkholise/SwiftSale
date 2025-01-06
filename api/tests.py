from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import Product
import json

class BuyRequestTestCase(TestCase):
    def setUp(self):
        # Create a product to test with
        self.product = Product.objects.create(
            name='Test Product',
            quantity=10,
            price=100
        )
        self.url = reverse('buy-request')  # Adjust the URL to match your configuration

    def print_json_response(self, response, test_name):
        # Print the name of the test being executed
        print(f"\nExecuting: {test_name}")
        # Helper method to print the full JSON response in a formatted way
        print(f"Response status code: {response.status_code}")
        try:
            response_data = response.json()
            print("Response JSON (formatted):")
            print(json.dumps(response_data, indent=4))  # Pretty-print the JSON response
        except ValueError:
            print("Response is not valid JSON. Raw content:")
            print(response.content)  # Print raw content if JSON decoding fails

    def test_buy_request_valid_data(self):
        # Prepare valid data
        data = {
            'sender': '0x1234567890abcdef1234567890abcdef12345678',
            'amount': 100,  # USDT amount
            'product_name': self.product.name,
            'product_quantity': 1,
            'signed_transaction': None  # Simulate unsigned transaction
        }

        # Send POST request with valid data
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        # Print the full JSON response
        self.print_json_response(response, "test_buy_request_valid_data")

        # Assert that the response is a success and contains an unsigned transaction
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unsigned_transaction', response.json())

    def test_buy_request_product_not_found(self):
        # Prepare data with a non-existing product name
        data = {
            'sender': '0x1234567890abcdef1234567890abcdef12345678',
            'amount': 100,
            'product_name': 'Non-Existing Product',
            'product_quantity': 1,
        }

        # Send POST request with invalid product name
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        # Print the full JSON response
        self.print_json_response(response, "test_buy_request_product_not_found")

        # Assert that the response is an error and the product is not found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['error'], 'Product not found')

    def test_buy_request_insufficient_stock(self):
        # Prepare data with quantity greater than available stock
        data = {
            'sender': '0x1234567890abcdef1234567890abcdef12345678',
            'amount': 100,
            'product_name': self.product.name,
            'product_quantity': 20  # Insufficient stock
        }

        # Send POST request with invalid quantity
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        # Print the full JSON response
        self.print_json_response(response, "test_buy_request_insufficient_stock")

        # Assert that the response is an error and insufficient stock is reported
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Insufficient stock available for the requested quantity')

    def test_buy_request_invalid_method(self):
        # Send GET request to a POST-only endpoint
        response = self.client.get(self.url)

        # Print the full JSON response
        self.print_json_response(response, "test_buy_request_invalid_method")

        # Assert that the response returns the correct error for invalid method
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Invalid request method')

