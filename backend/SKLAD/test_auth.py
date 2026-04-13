"""Тесты регистрации и входа (Token)."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAPITests(APITestCase):
    def test_register_success_returns_201_and_token(self):
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'newuser', 'password': 'secretpass123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username_returns_400(self):
        User.objects.create_user('dup', password='pass12345')
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'dup', 'password': 'otherpass123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success_returns_200_and_token(self):
        User.objects.create_user('login_ok', password='correctpass123')
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'login_ok', 'password': 'correctpass123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_wrong_password_returns_401(self):
        User.objects.create_user('login_bad', password='rightpass123')
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'login_bad', 'password': 'wrongpass999'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
