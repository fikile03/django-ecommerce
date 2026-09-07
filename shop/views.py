from decimal import Decimal

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.core.mail import EmailMessage
from django.db import transaction

from .forms import RegistrationForm, StoreForm, ProductForm, ReviewForm
from .models import Store, Product, Order, OrderItem, Review
from .functions.jsonplaceholder import get_jsonplaceholder_posts


def register(request):
    """Register a new user and assign them to the selected user group."""

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            role = form.cleaned_data["role"]
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            login(request, user)

            if role == "Vendor":
                return redirect("vendor_dashboard")

            return redirect("home")
    else:
        form = RegistrationForm()

    return render(request, "shop/register.html", {"form": form})


def user_login(request):
    """Authenticate a user and log them into the application."""

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "shop/login.html", {"form": form})


def user_logout(request):
    """Log the current user out of the application."""

    logout(request)
    return redirect("login")


def home(request):
    """Display the home page and provide vendor-specific navigation."""

    is_vendor = (
        request.user.is_authenticated
        and request.user.groups.filter(name="Vendor").exists()
    )

    return render(
        request,
        "shop/home.html",
        {"is_vendor": is_vendor},
    )


@login_required
def vendor_dashboard(request):
    """Display the dashboard for vendors and their stores."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    stores = Store.objects.filter(vendor=request.user)

    return render(
        request,
        "shop/vendor_dashboard.html",
        {"stores": stores},
    )


@login_required
def create_store(request):
    """Allow a vendor to create a new store."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    if request.method == "POST":
        form = StoreForm(request.POST)

        if form.is_valid():
            store = form.save(commit=False)
            store.vendor = request.user
            store.save()

            return redirect("store_list")
    else:
        form = StoreForm()

    return render(request, "shop/create_store.html", {"form": form})


@login_required
def store_list(request):
    """Display all stores belonging to the logged-in vendor."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    stores = Store.objects.filter(vendor=request.user)

    return render(request, "shop/store_list.html", {"stores": stores})


@login_required
def edit_store(request, store_id):
    """Allow a vendor to edit one of their stores."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    store = Store.objects.get(id=store_id)

    if store.vendor != request.user:
        return redirect("store_list")

    if request.method == "POST":
        form = StoreForm(request.POST, instance=store)

        if form.is_valid():
            form.save()
            return redirect("store_list")
    else:
        form = StoreForm(instance=store)

    return render(request, "shop/edit_store.html", {"form": form, "store": store})


@login_required
def delete_store(request, store_id):
    """Allow a vendor to delete one of their stores."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    store = Store.objects.get(id=store_id)

    if store.vendor != request.user:
        return redirect("store_list")

    if request.method == "POST":
        store.delete()
        return redirect("store_list")

    return render(request, "shop/delete_store.html", {"store": store})


@login_required
def create_product(request, store_id):
    """Allow a vendor to create a product for one of their stores."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    store = Store.objects.get(id=store_id)

    if store.vendor != request.user:
        return redirect("store_list")

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()

            return redirect("product_list", store_id=store.id)
    else:
        form = ProductForm()

    return render(request, "shop/create_product.html", {"form": form, "store": store})


@login_required
def product_list(request, store_id):
    """Display all products belonging to a vendor's store."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    store = Store.objects.get(id=store_id)

    if store.vendor != request.user:
        return redirect("store_list")

    products = Product.objects.filter(store=store)

    return render(
        request, "shop/product_list.html", {"store": store, "products": products}
    )


@login_required
def edit_product(request, product_id):
    """Allow a vendor to edit one of their products."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    product = Product.objects.get(id=product_id)

    if product.store.vendor != request.user:
        return redirect("store_list")

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("product_list", store_id=product.store.id)
    else:
        form = ProductForm(instance=product)

    return render(request, "shop/edit_product.html", {"form": form, "product": product})


@login_required
def delete_product(request, product_id):
    """Allow a vendor to delete one of their products."""

    if not request.user.groups.filter(name="Vendor").exists():
        return redirect("home")

    product = Product.objects.get(id=product_id)

    if product.store.vendor != request.user:
        return redirect("store_list")

    if request.method == "POST":
        store_id = product.store.id
        product.delete()
        return redirect("product_list", store_id=store_id)

    return render(request, "shop/delete_product.html", {"product": product})


def product_catalogue(request):
    """Display all products and their associated reviews."""

    products = Product.objects.select_related("store").all()
    reviews = Review.objects.select_related("user", "product").all()

    return render(
        request,
        "shop/product_catalogue.html",
        {
            "products": products,
            "reviews": reviews,
        },
    )


def cart(request):
    """Display the products currently stored in the user's shopping cart."""

    cart = request.session.get("cart", {})

    products = Product.objects.filter(id__in=cart.keys())

    valid_product_ids = {str(product.id) for product in products}

    cart = {
        product_id: quantity
        for product_id, quantity in cart.items()
        if product_id in valid_product_ids
    }

    request.session["cart"] = cart
    request.session.modified = True

    cart_items = []

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    total = sum(item["subtotal"] for item in cart_items)

    return render(
        request,
        "shop/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )


def add_to_cart(request, product_id):
    """Add a selected product to the user's shopping cart."""

    product = Product.objects.get(id=product_id)

    cart = request.session.get("cart", {})

    product_id = str(product.id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity >= product.stock:
        return redirect("cart")

    cart[product_id] = current_quantity + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def remove_from_cart(request, product_id):
    """Remove a selected product from the user's shopping cart."""

    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


@login_required
def order_history(request):
    """Display the current user's previous orders."""

    orders = Order.objects.filter(buyer=request.user).order_by("-created_at")

    return render(
        request,
        "shop/order_history.html",
        {"orders": orders},
    )


@login_required
def order_detail(request, order_id):
    """Display the details of an order belonging to the logged-in buyer."""

    order = Order.objects.get(id=order_id)

    if order.buyer != request.user:
        return redirect("home")

    items = OrderItem.objects.filter(order=order)

    return render(
        request,
        "shop/order_detail.html",
        {
            "order": order,
            "items": items,
        },
    )


@login_required
def checkout(request):
    """Process the user's shopping cart and create a new order."""

    print("CHECKOUT VIEW CALLED:", request.method)

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    products = Product.objects.filter(id__in=cart.keys())

    total = Decimal("0.00")

    for product in products:
        quantity = cart[str(product.id)]
        total += product.price * quantity

    if request.method == "POST":
        print("CHECKOUT POST REACHED")

        for product in products:
            quantity = cart[str(product.id)]

            if quantity > product.stock:
                return redirect("cart")

        with transaction.atomic():
            order = Order.objects.create(
                buyer=request.user,
                total_amount=total,
            )

            invoice = f"Invoice for Order #{order.id}\n\n"
            invoice += f"Buyer: {request.user.username}\n\n"

            for product in products:
                quantity = cart[str(product.id)]

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

                product.stock -= quantity
                product.save(update_fields=["stock"])

                subtotal = product.price * quantity
                invoice += f"{product.name} x {quantity} = R{subtotal}\n"

            invoice += f"\nTotal: R{total}\n"
            invoice += "\nThank you for your purchase!"

        email = EmailMessage(
            subject=f"Invoice for Order #{order.id}",
            body=invoice,
            to=[request.user.email],
        )

        result = email.send()

        print("EMAIL SEND RESULT:", result)

        request.session["cart"] = {}

        return redirect("order_success")

    return render(
        request,
        "shop/checkout.html",
        {
            "cart_items": [
                {
                    "product": product,
                    "quantity": cart[str(product.id)],
                    "subtotal": product.price * cart[str(product.id)],
                }
                for product in products
            ],
            "total": total,
        },
    )
    return render(
        request,
        "shop/checkout.html",
        {
            "cart_items": [
                {
                    "product": product,
                    "quantity": cart[str(product.id)],
                    "subtotal": product.price * cart[str(product.id)],
                }
                for product in products
            ],
            "total": total,
        },
    )


@login_required
def order_success(request):
    """Display the order success page after a successful checkout."""

    return render(request, "shop/order_success.html")


@login_required
def add_review(request, product_id):
    """Allow a user to submit a review for a product they purchased."""

    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            purchased = OrderItem.objects.filter(
                order__buyer=request.user, product=product
            ).exists()

            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified = purchased
            review.save()

            return redirect("product_catalogue")
    else:
        form = ReviewForm()

    return render(
        request,
        "shop/add_review.html",
        {"product": product, "form": form},
    )


def external_posts(request):
    """Fetch posts from JSONPlaceholder and display them."""

    user_id = request.GET.get("userId")

    posts = get_jsonplaceholder_posts(user_id)

    return render(request, "shop/external_posts.html", {"posts": posts})
