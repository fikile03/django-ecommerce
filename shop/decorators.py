from django.contrib.auth.decorators import user_passes_test


def is_vendor(user):
    """Return True if the user belongs to the Vendor group."""

    return user.is_authenticated and user.groups.filter(name="Vendor").exists()


def vendor_required(view_func):
    """Require the logged-in user to belong to the Vendor group."""

    return user_passes_test(is_vendor, login_url="home")(view_func)
