from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Store(models.Model):
    """Represent a store owned by a vendor."""

    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the store name as its string representation."""

        return self.name


class Product(models.Model):
    """Represent a product belonging to a store."""

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the product name as its string representation."""

        return self.name


class CartItem(models.Model):
    """Represent a product and quantity associated with a buyer's cart."""

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        """Return the product name and quantity as a string."""

        return f"{self.product.name} - {self.quantity}"


class Order(models.Model):
    """Represent an order placed by a buyer."""

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )

    def __str__(self):
        """Return the order ID as a string."""

        return f"Order {self.id}"


class OrderItem(models.Model):
    """Represent a product included in an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Return the product name and quantity as a string."""

        return f"{self.product.name} - {self.quantity}"


class Review(models.Model):
    """Represent a review submitted by a user for a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Define database constraints for reviews."""

        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        """Return the product name and username as a string."""

        return f"{self.product.name} - {self.user.username}"
