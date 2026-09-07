from django.urls import path
from . import api_views

urlpatterns = [
    path("stores/", api_views.create_store_api, name="api_create_store"),
    path(
        "stores/<int:store_id>/products/",
        api_views.create_product_api,
        name="api_products",
    ),
    path(
        "vendors/<int:user_id>/stores/",
        api_views.vendor_stores_api,
        name="api_vendor_stores",
    ),
    path(
        "products/<int:product_id>/reviews/",
        api_views.product_reviews_api,
        name="api_product_reviews",
    ),
]
