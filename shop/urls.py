from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("vendor-dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("store/create/", views.create_store, name="create_store"),
    path("stores/", views.store_list, name="store_list"),
    path("store/<int:store_id>/edit/", views.edit_store, name="edit_store"),
    path("store/<int:store_id>/delete/", views.delete_store, name="delete_store"),
    path(
        "store/<int:store_id>/product/create/",
        views.create_product,
        name="create_product",
    ),
    path("store/<int:store_id>/products/", views.product_list, name="product_list"),
    path("product/<int:product_id>/edit/", views.edit_product, name="edit_product"),
    path(
        "product/<int:product_id>/delete/", views.delete_product, name="delete_product"
    ),
    path("products/", views.product_catalogue, name="product_catalogue"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/decrease/<int:product_id>/",
        views.decrease_cart_quantity,
        name="decrease_cart_quantity",
    ),
    path(
        "cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("order-success/", views.order_success, name="order_success"),
    path("review/<int:product_id>/", views.add_review, name="add_review"),
    path("review/<int:review_id>/edit/", views.edit_review, name="edit_review"),
    path("review/<int:review_id>/delete/", views.delete_review, name="delete_review"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="shop/password_reset.html",
            email_template_name="shop/password_reset_email.html",
            success_url="/password_reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="shop/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="shop/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="shop/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("external-posts/", views.external_posts, name="external_posts"),
]
