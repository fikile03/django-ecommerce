from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Order, OrderItem, Product, Review, Store


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

    def test_vendor_cannot_edit_another_vendors_product(self):
        other_vendor = User.objects.create_user(
            username="other_vendor",
            password="StrongPassword123!",
        )

        vendor_group = Group.objects.get(name="Vendor")
        other_vendor.groups.add(vendor_group)

        product = Product.objects.create(
            store=self.store,
            name="Original Product",
            description="Original description",
            price=500,
            stock=10,
        )

        self.client.force_login(other_vendor)

        response = self.client.post(
            reverse("edit_product", args=[product.id]),
            {
                "name": "Changed Product",
                "description": "Changed description",
                "price": 100,
                "stock": 1,
            },
        )

        self.assertRedirects(response, reverse("store_list"))

        product.refresh_from_db()

        self.assertEqual(product.name, "Original Product")
        self.assertEqual(product.description, "Original description")
        self.assertEqual(product.price, 500)
        self.assertEqual(product.stock, 10)

    def test_vendor_cannot_delete_another_vendors_product(self):
        other_vendor = User.objects.create_user(
            username="delete_vendor",
            password="StrongPassword123!",
        )

        vendor_group = Group.objects.get(name="Vendor")
        other_vendor.groups.add(vendor_group)

        product = Product.objects.create(
            store=self.store,
            name="Protected Product",
            description="This product should not be deleted",
            price=750,
            stock=5,
        )

        self.client.force_login(other_vendor)

        response = self.client.post(
            reverse("delete_product", args=[product.id]),
        )

        self.assertRedirects(response, reverse("store_list"))

        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_logged_in_user_can_submit_unverified_review(self):
        buyer = User.objects.create_user(
            username="review_buyer",
            password="StrongPassword123!",
        )

        product = Product.objects.get(name="Classic Denim Jacket")

        self.client.force_login(buyer)

        response = self.client.post(
            reverse("add_review", args=[product.id]),
            {
                "rating": "5",
                "comment": "Great jacket!",
            },
        )

        self.assertRedirects(response, reverse("product_catalogue"))

        review = Review.objects.get(
            product=product,
            user=buyer,
        )

        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great jacket!")
        self.assertFalse(review.is_verified)

    def test_user_cannot_edit_another_users_review(self):
        reviewer = User.objects.create_user(
            username="reviewer",
            password="StrongPassword123!",
        )

        other_user = User.objects.create_user(
            username="other_user",
            password="StrongPassword123!",
        )

        product = Product.objects.get(name="Classic Denim Jacket")

        review = Review.objects.create(
            product=product,
            user=reviewer,
            rating=4,
            comment="Original review",
            is_verified=False,
        )

        self.client.force_login(other_user)

        response = self.client.post(
            reverse("edit_review", args=[review.id]),
            {
                "rating": "1",
                "comment": "I changed this review!",
            },
        )

        self.assertEqual(response.status_code, 404)

        review.refresh_from_db()

        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "Original review")
        self.assertEqual(review.user, reviewer)

    def test_user_cannot_delete_another_users_review(self):
        reviewer = User.objects.create_user(
            username="delete_reviewer",
            password="StrongPassword123!",
        )

        other_user = User.objects.create_user(
            username="delete_other_user",
            password="StrongPassword123!",
        )

        product = Product.objects.get(name="Classic Denim Jacket")

        review = Review.objects.create(
            product=product,
            user=reviewer,
            rating=4,
            comment="Original review",
            is_verified=False,
        )

        self.client.force_login(other_user)

        response = self.client.post(
            reverse("delete_review", args=[review.id]),
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_cart_cannot_exceed_product_stock(self):
        product = Product.objects.create(
            store=self.store,
            name="Limited Stock Product",
            description="Only two available",
            price=300,
            stock=2,
        )

        self.client.get(reverse("add_to_cart", args=[product.id]))
        self.client.get(reverse("add_to_cart", args=[product.id]))
        self.client.get(reverse("add_to_cart", args=[product.id]))

        cart = self.client.session.get("cart", {})

        self.assertEqual(cart[str(product.id)], 2)

    def test_out_of_stock_product_cannot_be_added_to_cart(self):
        product = Product.objects.create(
            store=self.store,
            name="Out of Stock Product",
            description="This product is unavailable",
            price=250,
            stock=0,
        )

        self.client.get(reverse("add_to_cart", args=[product.id]))

        cart = self.client.session.get("cart", {})

        self.assertNotIn(str(product.id), cart)

    def test_checkout_rejects_insufficient_stock(self):
        buyer = User.objects.create_user(
            username="checkout_buyer",
            email="buyer@example.com",
            password="StrongPassword123!",
        )

        product = Product.objects.create(
            store=self.store,
            name="Limited Checkout Product",
            description="Only two available",
            price=400,
            stock=2,
        )

        self.client.force_login(buyer)

        session = self.client.session
        session["cart"] = {
            str(product.id): 3,
        }
        session.save()

        response = self.client.post(
            reverse("checkout"),
        )

        self.assertRedirects(response, reverse("cart"))

        self.assertFalse(Order.objects.filter(buyer=buyer).exists())

        product.refresh_from_db()

        self.assertEqual(product.stock, 2)

    def test_checkout_creates_order_and_updates_stock(self):
        buyer = User.objects.create_user(
            username="successful_buyer",
            email="buyer@example.com",
            password="StrongPassword123!",
        )

        product = Product.objects.create(
            store=self.store,
            name="Checkout Product",
            description="A product for checkout testing",
            price=400,
            stock=5,
        )

        self.client.force_login(buyer)

        session = self.client.session
        session["cart"] = {
            str(product.id): 2,
        }
        session.save()

        response = self.client.post(
            reverse("checkout"),
        )

        self.assertRedirects(response, reverse("order_success"))

        order = Order.objects.get(buyer=buyer)

        self.assertEqual(order.total_amount, 800)
        self.assertEqual(order.status, "Pending")

        order_item = OrderItem.objects.get(order=order)

        self.assertEqual(order_item.product, product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, 400)

        product.refresh_from_db()

        self.assertEqual(product.stock, 3)

        cart = self.client.session.get("cart", {})

        self.assertEqual(cart, {})

    def test_order_history_only_shows_users_own_orders(self):
        buyer_one = User.objects.create_user(
            username="history_buyer_one",
            password="StrongPassword123!",
        )

        buyer_two = User.objects.create_user(
            username="history_buyer_two",
            password="StrongPassword123!",
        )

        order_one = Order.objects.create(
            buyer=buyer_one,
            total_amount=500,
        )

        order_two = Order.objects.create(
            buyer=buyer_two,
            total_amount=900,
        )

        self.client.force_login(buyer_one)

        response = self.client.get(
            reverse("order_history"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Order #{order_one.id}")
        self.assertNotContains(response, f"Order #{order_two.id}")

    def test_user_cannot_view_another_users_order(self):
        buyer_one = User.objects.create_user(
            username="detail_buyer_one",
            password="StrongPassword123!",
        )

        buyer_two = User.objects.create_user(
            username="detail_buyer_two",
            password="StrongPassword123!",
        )

        order = Order.objects.create(
            buyer=buyer_one,
            total_amount=600,
        )

        self.client.force_login(buyer_two)

        response = self.client.get(
            reverse("order_detail", args=[order.id]),
        )

        self.assertRedirects(response, reverse("home"))

    def test_user_can_view_own_order(self):
        buyer = User.objects.create_user(
            username="own_order_buyer",
            password="StrongPassword123!",
        )

        product = Product.objects.create(
            store=self.store,
            name="Order Detail Product",
            description="A product for order detail testing",
            price=350,
            stock=10,
        )

        order = Order.objects.create(
            buyer=buyer,
            total_amount=700,
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price=350,
        )

        self.client.force_login(buyer)

        response = self.client.get(
            reverse("order_detail", args=[order.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Order #{order.id}")
        self.assertContains(response, "Order Detail Product")
        self.assertContains(response, "Quantity: 2")
        self.assertContains(response, "Price: R350")
        self.assertContains(response, "Total: R700")

    def test_unauthenticated_user_cannot_access_checkout(self):
        response = self.client.get(
            reverse("checkout"),
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("login"),
            response.url,
        )

    def test_unauthenticated_user_cannot_access_order_history(self):
        response = self.client.get(
            reverse("order_history"),
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("login"),
            response.url,
        )
