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

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")
router.register(r"categories", CategoryViewSet, basename="category")


urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    path(
        "password_reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "verify_reset_code/",
        VerifyResetCodeView.as_view(),
        name="verify_reset_code",
    ),
    path(
        "reset_password/",
        ResetPasswordView.as_view(),
        name="reset_password",
    ),
    path("delete_account/", UserDeleteAPIView.as_view(), name="delete_account"),
]
