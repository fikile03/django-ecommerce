from rest_framework import serializers

from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    """Serialize store data for the API."""

    class Meta:
        """Define the model and fields used by the store serializer."""

        model = Store
        fields = ["id", "name", "description", "vendor"]


class ProductSerializer(serializers.ModelSerializer):
    """Serialize product data for the API."""

    class Meta:
        """Define the model and fields used by the product serializer."""

        model = Product
        fields = ["id", "name", "description", "price", "stock", "store"]


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize review data for the API."""

    class Meta:
        """Define the model and fields used by the review serializer."""

        model = Review
        fields = [
            "id",
            "product",
            "user",
            "rating",
            "comment",
            "is_verified",
            "created_at",
        ]
