from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Users(AbstractUser):

    CHEF = "Barber"
    MANAGER = "Manager"

    ROLE_CHOICES = [
        (CHEF, "Barber"),
        (MANAGER, "Manager"),
    
    ]
    is_manager = models.BooleanField(default=False)
    is_barber = models.BooleanField(default=False)
    birthdate = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, null=True, blank=True)
    experienceyears = models.IntegerField(null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    user_image = models.ImageField(
        upload_to="user_images/", default="default_user_image.jpg"
    )

    def __str__(self):
        return self.username


    
class PaymentTransaction(models.Model):
    BANK = "bank"
    MPESA = "mpesa"
    CASH = "cash"
    
    PAYMENT_CHOICES = [
        (BANK, "bank"),
        (MPESA, "mpesa"),
        (CASH, "cash"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="payments", on_delete=models.CASCADE, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20 ,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True , null=True, blank=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_CHOICES, null=True, blank=True)
    balance = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    result_desc = models.CharField(max_length=255, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    booking_date = models.DateField(null=True, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='paymenttho')

    def __str__(self):
        return f"Transaction ID: {self.transaction_id}, Amount: {self.amount}, Status: {self.status}"



















