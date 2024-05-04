from rest_framework import serializers
from .models import Category, Item
from django.contrib.auth.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Set password field to write-only and required for security
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("username", "email", "password")

    # Create and return a new user with validated data
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", None),
            password=validated_data["password"],
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        # Specify optional fields
        extra_kwargs = {
            "description": {"required": False},
            "parent": {"required": False},
            "keywords": {"required": False},
            "default_location": {"required": False},
        }


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"

    # Create and return a new item with validated data
    def create(self, validated_data):
        return Item.objects.create(**validated_data)
