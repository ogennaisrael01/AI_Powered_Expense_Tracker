from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username,password, **kwargs):
        if not any([email, username]):
            raise ValueError("Please fill the blank fields")
        email = self.normalize_email(email=email)
        user = self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, username, password, **extra_kwargs):
        extra_kwargs.setdefault("is_superuser", True)
        extra_kwargs.setdefault("is_staff", True)

        if not extra_kwargs.get("is_superuser"):
            raise ValueError("A super user must have the super user role")
        if not extra_kwargs.get("is_staff"):
            raise ValueError("A super user must have the is staff role")
        
        user = self.create_user(email=email, username=username, password=password, **extra_kwargs)
        return user
    

class Currency(models.TextChoices):
    NAIRA = "NGN", "NGN"
    DOLLARS = "USD", "USD"

class CustomUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True, unique=True, max_length=20)
    email = models.EmailField(max_length=50, unique=True, db_index=True)
    username = models.CharField(max_length=100)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=20, choices=Currency, default=Currency.NAIRA)
    income = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    objects = CustomUserManager()
    @property
    def is_admin(self):
        if self.is_superuser and isinstance(self.is_superuser, bool):
            return True
        return False
    
    def __str__(self):
        return f""
