from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User

from .models import Store, Product, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_store_api(request):
    """Create a new store for the authenticated user."""

    store = Store.objects.create(
        vendor=request.user,
        name=request.data.get("name"),
        description=request.data.get("description", ""),
    )

    serializer = StoreSerializer(store)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_product_api(request, store_id):
    """Retrieve products or create a product for a specified store."""

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response(
            {"error": "Store not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        products = Product.objects.filter(store=store)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    if store.vendor != request.user:
        return Response(
            {"error": "You can only add products to your own store."},
            status=status.HTTP_403_FORBIDDEN,
        )

    product = Product.objects.create(
        store=store,
        name=request.data.get("name"),
        description=request.data.get("description"),
        price=request.data.get("price"),
        stock=request.data.get("stock", 0),
    )

    serializer = ProductSerializer(product)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_stores_api(request, user_id):
    """Return all stores belonging to a specified vendor."""

    stores = Store.objects.filter(vendor_id=user_id)
    serializer = StoreSerializer(stores, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def store_products_api(request, store_id):
    """Return all products belonging to a specified store."""

    products = Product.objects.filter(store_id=store_id)
    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_reviews_api(request, product_id):
    """Return all reviews associated with a specified product."""

    reviews = Review.objects.filter(product_id=product_id)
    serializer = ReviewSerializer(reviews, many=True)

    return Response(serializer.data)
