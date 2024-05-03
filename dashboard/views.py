from rest_framework import viewsets, filters, status, generics, views
from django_filters.rest_framework import DjangoFilterBackend
from .models import Item, PasswordResetCode, Category
from .serializers import ItemSerializer, UserRegistrationSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
import datetime
from rest_framework.decorators import action


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ResetPasswordView(views.APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password has been reset successfully"},
                status=status.HTTP_200_OK,
            )
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class VerifyResetCodeView(views.APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        code = request.data.get("code")
        user = User.objects.filter(email=email).first()
        if user:
            password_reset_code = PasswordResetCode.objects.filter(
                user=user, reset_code=code
            ).first()
            if password_reset_code and not password_reset_code.is_expired():
                # Optionally, invalidate the code immediately after use
                password_reset_code.delete()
                return Response({"message": "Code verified"}, status=status.HTTP_200_OK)
            return Response(
                {"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class PasswordResetRequestView(views.APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            # Generate a 6-digit code
            reset_code = get_random_string(length=6, allowed_chars="0123456789")
            expiration_time = timezone.now() + datetime.timedelta(
                minutes=10
            )  # 10 minutes from now

            # Save the code and expiration time
            PasswordResetCode.objects.create(
                user=user, reset_code=reset_code, expires_at=expiration_time
            )

            # Send email with the code
            send_mail(
                "Password Reset Code",
                f"Your password reset code is: {reset_code}",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            return Response({"message": "Email sent"}, status=status.HTTP_200_OK)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(
                    {"message": "User created successfully"},
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        "SKU",
        "name",
        "category__name",
        "in_stock",
        "is_salable",
        "price",
    ]  # Added price here
    ordering_fields = ["name", "in_stock", "price"]  # Added price here
    search_fields = ["name", "description", "tags"]


# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
