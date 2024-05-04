from django.contrib.auth.models import User
import datetime
from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    # Define a product category with optional nested subcategories
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    keywords = models.TextField(blank=True, null=True)
    default_location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    # Represent an inventory item with comprehensive details
    SKU = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="items", null=True, blank=True
    )
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    units = models.CharField(max_length=20, blank=True, null=True)
    minimum_stock = models.IntegerField(default=0)
    is_purchaseable = models.BooleanField(default=True)
    is_salable = models.BooleanField(default=True)
    is_trackable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    external_link = models.TextField(blank=True, null=True)
    variant_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="variants",
    )

    def save(self, *args, **kwargs):
        # Validate SKU uniqueness except for the current instance
        if self.SKU and Item.objects.filter(SKU=self.SKU).exclude(id=self.id).exists():
            raise ValidationError("Item with this SKU already exists.")
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class PasswordResetCode(models.Model):
    # Manage password reset codes with expiration logic
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        # Check if the reset code has expired
        return self.expires_at < datetime.datetime.now()
