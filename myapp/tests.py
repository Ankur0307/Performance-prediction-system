from django.test import TestCase
from django.urls import reverse

from .auth_bootstrap import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD


class HomePageTests(TestCase):
    def test_homepage_renders_login_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_default_admin_can_log_in(self):
        response = self.client.post(
            reverse('login'),
            {"email": DEFAULT_ADMIN_EMAIL, "password": DEFAULT_ADMIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/ads/", response.url)
        self.assertIn("/dashboard/", response.url)
