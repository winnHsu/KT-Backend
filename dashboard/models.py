from django.contrib.auth.models import User
import datetime
from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Allow null for text fields
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
    SKU = models.CharField(
        max_length=50, unique=False, blank=True, null=True  # remove unique=True here
    )
    name = models.CharField(max_length=255)  # Only required field
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="items",
        null=True,
        blank=True,  # Category can be optional
    )
    description = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    units = models.CharField(max_length=20, blank=True, null=True)
    minimum_stock = models.IntegerField(default=0)
    desired_stock = models.IntegerField(default=0)
    is_assembly = models.BooleanField(default=False)
    is_component = models.BooleanField(default=False)
    is_purchaseable = models.BooleanField(default=True)
    is_salable = models.BooleanField(default=True)
    is_bundle = models.BooleanField(default=False)
    is_trackable = models.BooleanField(default=True)
    in_stock = models.IntegerField(default=0)
    is_template = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    total_allocated = models.IntegerField(default=0)
    allocated_to_builds = models.IntegerField(default=0)
    allocated_to_sales = models.IntegerField(default=0)
    available_stock = models.IntegerField(default=0)
    incoming_stock = models.IntegerField(default=0)
    on_build_order = models.IntegerField(default=0)
    net_stock = models.IntegerField(default=0)
    external_link = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)  # Made optional
    variant_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="variants",
    )  # Self-referencing ForeignKey
    default_location = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.SKU:
            if Item.objects.filter(SKU=self.SKU).exclude(id=self.id).exists():
                raise ValidationError("Item with this SKU already exists.")
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return self.expires_at < datetime.datetime.now()
