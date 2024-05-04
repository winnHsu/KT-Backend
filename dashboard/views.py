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


# Provides CRUD operations for Category model with authentication
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


# Handles password reset requests by setting a new password
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


# Validates password reset codes and checks for expiration
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
                password_reset_code.delete()  # Invalidate the code after use
                return Response({"message": "Code verified"}, status=status.HTTP_200_OK)
            return Response(
                {"error": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Sends password reset codes to users' email
class PasswordResetRequestView(views.APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            reset_code = get_random_string(
                length=6, allowed_chars="0123456789"
            )  # Generate a 6-digit code
            expiration_time = timezone.now() + datetime.timedelta(
                minutes=10
            )  # Code expires in 10 minutes
            PasswordResetCode.objects.create(
                user=user, reset_code=reset_code, expires_at=expiration_time
            )
            send_mail(
                "Password Reset Code",
                f"Your password reset code is: {reset_code}",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            return Response({"message": "Email sent"}, status=status.HTTP_200_OK)
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# Allows users to delete their account
class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # Only allows deleting the logged-in user


# Handles user registration using custom serialization
class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Manages item data with filtering, searching, and ordering capabilities
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
    ]
    ordering_fields = ["name", "in_stock", "price"]
    search_fields = ["name", "description", "tags"]
