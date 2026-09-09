from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Product, Store


class RegistrationTests(TestCase):
    def test_vendor_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testvendor",
                "email": "vendor@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
                "role": "Vendor",
            },
        )

        self.assertRedirects(response, reverse("vendor_dashboard"))

        user = self.client.session.get("_auth_user_id")
        self.assertIsNotNone(user)

        self.assertTrue(
            Group.objects.get(name="Vendor")
            .user_set.filter(username="testvendor")
            .exists()
        )

    def test_buyer_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "testbuyer",
                "email": "buyer@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
                "role": "Buyer",
            },
        )

        self.assertRedirects(response, reverse("home"))

        self.assertTrue(
            Group.objects.get(name="Buyer")
            .user_set.filter(username="testbuyer")
            .exists()
        )


class VendorAccessTests(TestCase):
    def test_buyer_cannot_access_vendor_dashboard(self):
        user = User.objects.create_user(
            username="testbuyer",
            email="buyer@example.com",
            password="StrongPassword123!",
        )

        buyer_group = Group.objects.get(name="Buyer")
        user.groups.add(buyer_group)

        self.client.force_login(user)

        response = self.client.get(reverse("vendor_dashboard"))

        self.assertEqual(
            response.url,
            f"{reverse('home')}?next={reverse('vendor_dashboard')}",
        )


class ProductCatalogueTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username="vendor",
            password="StrongPassword123!",
        )

        vendor_group = Group.objects.get(name="Vendor")
        self.vendor.groups.add(vendor_group)

        self.store = Store.objects.create(
            vendor=self.vendor,
            name="Test Store",
            description="A test store",
        )

        Product.objects.create(
            store=self.store,
            name="Classic Denim Jacket",
            description="A blue denim jacket",
            price=450,
            stock=10,
        )

        Product.objects.create(
            store=self.store,
            name="Hydrating Face Cream",
            description="A moisturising face cream",
            price=180,
            stock=15,
        )

    def test_product_search(self):
        response = self.client.get(
            reverse("product_catalogue"),
            {"q": "Jacket"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Classic Denim Jacket")
        self.assertNotContains(response, "Hydrating Face Cream")

    def test_vendor_can_create_product(self):
        self.client.force_login(self.vendor)

        response = self.client.post(
            reverse("create_product", args=[self.store.id]),
            {
                "name": "Wireless Headphones",
                "description": "Bluetooth wireless headphones",
                "price": 899,
                "stock": 20,
            },
        )

        self.assertRedirects(
            response,
            reverse("product_list", args=[self.store.id]),
        )

        product = Product.objects.get(name="Wireless Headphones")

        self.assertEqual(product.store, self.store)
        self.assertEqual(product.price, 899)
        self.assertEqual(product.stock, 20)
