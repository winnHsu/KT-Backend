from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ItemViewSet,
    CategoryViewSet,
    UserRegistrationAPIView,
    UserDeleteAPIView,
    PasswordResetRequestView,
    VerifyResetCodeView,
    ResetPasswordView,
)

# Setup the default router for REST API views.
router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")
router.register(r"categories", CategoryViewSet, basename="category")

# Define URL patterns for the API including registration and password management.
urlpatterns = [
    path(
        "", include(router.urls)
    ),  # Include router-generated URLs for item and category resources.
    path(
        "register/", UserRegistrationAPIView.as_view(), name="register"
    ),  # Endpoint for user registration.
    path(
        "password_reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),  # Endpoint for initiating password reset.
    path(
        "verify_reset_code/", VerifyResetCodeView.as_view(), name="verify_reset_code"
    ),  # Endpoint for verifying password reset codes.
    path(
        "reset_password/", ResetPasswordView.as_view(), name="reset_password"
    ),  # Endpoint for resetting the password.
    path(
        "delete_account/", UserDeleteAPIView.as_view(), name="delete_account"
    ),  # Endpoint for user account deletion.
]
