from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class CustomUser(AbstractUser):
    username = models.CharField(max_length = 150, unique = True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length = 255, null = True, blank = True)
    contact_number = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField( default=now)
    updated_at = models.DateTimeField(auto_now=True)

class MembershipPlan(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
        ('annual', 'Annual'),
    ]

    name = models.CharField(max_length = 100, unique = True)
    duration = models.CharField(max_length=100, choices = PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places = 2)
    description = models.TextField(blank = True, null = True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()}) - ₹{self.price}"
    

class Membership(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(default = now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} (Active: {self.is_active})"
    
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} ({self.get_status_display()})"
