from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Store, Product, Review


class RegistrationForm(UserCreationForm):
    """Form used to register a new user as a Vendor or Buyer."""

    ROLE_CHOICES = (
        ("Vendor", "Vendor"),
        ("Buyer", "Buyer"),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        """Define the model and fields used by the registration form."""

        model = User
        fields = ["username", "email", "password1", "password2", "role"]


class StoreForm(forms.ModelForm):
    """Form used to create and edit vendor stores."""

    class Meta:
        """Define the model and fields used by the store form."""

        model = Store
        fields = ["name", "description"]


class ProductForm(forms.ModelForm):
    """Form used to create and edit store products."""

    class Meta:
        """Define the model and fields used by the product form."""

        model = Product
        fields = ["name", "description", "price", "stock"]

    def clean_name(self):
        """Validate that the product name is not blank."""

        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError("Product name cannot be empty.")

        return name

    def clean_description(self):
        """Validate that the product description is not blank."""

        description = self.cleaned_data["description"].strip()

        if not description:
            raise forms.ValidationError("Product description cannot be empty.")

        return description

    def clean_price(self):
        """Validate that the product price is not negative."""

        price = self.cleaned_data["price"]

        if price < 0:
            raise forms.ValidationError("Product price cannot be negative.")

        return price

    def clean_stock(self):
        """Validate that the product stock is not negative."""

        stock = self.cleaned_data["stock"]

        if stock < 0:
            raise forms.ValidationError("Product stock cannot be negative.")

        return stock


class ReviewForm(forms.ModelForm):
    """Form used to submit a review for a product."""

    RATING_CHOICES = (
        (1, "1 - Very Bad"),
        (2, "2 - Bad"),
        (3, "3 - Okay"),
        (4, "4 - Good"),
        (5, "5 - Excellent"),
    )

    rating = forms.ChoiceField(choices=RATING_CHOICES)

    class Meta:
        """Define the model and fields used by the review form."""

        model = Review
        fields = ["rating", "comment"]
