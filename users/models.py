import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

from common.models import BaseModel


# Taken from here:
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
# With some modifications


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True, primary_key=True
    )
    username = models.CharField(max_length=128, unique=True)
    # user fields
    mobile_number = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, null=True, blank=True, unique=True)

    # identity
    display_name = models.CharField(max_length=255, default="")
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    # tracking metrics
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")
    last_location = models.CharField(max_length=255, blank=True)
    created_location = models.CharField(max_length=255, blank=True)

    # the is' es
    is_superuser = models.BooleanField(default=False)
    is_managed = models.BooleanField(default=False)
    is_password_expired = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_password_autoset = models.BooleanField(default=False)

    # random token generated
    token = models.CharField(max_length=64, blank=True)

    last_active = models.DateTimeField(default=timezone.now, null=True)
    last_login_time = models.DateTimeField(null=True)
    last_logout_time = models.DateTimeField(null=True)
    last_login_ip = models.CharField(max_length=255, blank=True)
    last_logout_ip = models.CharField(max_length=255, blank=True)
    last_login_medium = models.CharField(max_length=20, default="email")
    last_login_uagent = models.TextField(blank=True)
    token_updated_at = models.DateTimeField(null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.username} <{self.email}>"

    @property
    def is_super_admin(self):
        return self.is_superuser  # or check group membership

    @property
    def is_store_owner(self):
        return self.groups.filter(name='STORE_OWNER').exists()

    @property
    def is_staff_member(self):
        return self.groups.filter(name='STAFF').exists()


class Address(BaseModel):
    ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ADDRESS_TYPES)
    is_default = models.BooleanField(default=False)

    # Address Details
    zip = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    street_address = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class Profile(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    avatar = models.JSONField(default=dict, blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    socials = models.JSONField(null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    notifications = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")

    def __str__(self):
        return f"Customer {self.user.email}"
