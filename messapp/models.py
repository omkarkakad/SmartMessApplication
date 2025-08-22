from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username


class OrderModel(models.Model):
    order_id = models.PositiveIntegerField(unique=True, editable=False, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    MENU_CHOICES = [
        ('Poha', 'Poha'),
        ('Sabudana', 'Sabudana'),
        ('Appe', 'Appe'),
        ('Dosa', 'Dosa'),
        ('Yellow Dhokla', 'Yellow Dhokla'),
        ('White Dhokla', 'White Dhokla'),
        ('Methi Thepla', 'Methi Thepla'),
        ('Idli', 'Idli'),
        ('kothambir wadi', 'kothambir wadi'),
        ('Chana Masala', 'Chana Masala'),
        ('Jalebi', 'Jalebi'),
        ('Egg', 'Egg'),
    ]

    order_menu = models.TextField()
    order_place = models.CharField(max_length=100)

    PAID_CHOICES = [
        ('Paid', 'Paid'),
        ('Not Paid', 'Not Paid'),
    ]
    is_paid = models.CharField(max_length=10, choices=PAID_CHOICES)
    order_time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.order_id:
            existing_ids = OrderModel.objects.values_list('order_id', flat=True).order_by('order_id')
            new_id = 1
            for eid in existing_ids:
                if eid == new_id:
                    new_id += 1
                else:
                    break
            self.order_id = new_id
        super().save(*args, **kwargs)

    def order_menu_list(self):
        try:
            return json.loads(self.order_menu).items()
        except:
            return []

    def __str__(self):
        return f"Order {self.order_id} - {self.name}"


class ActiveMenu(models.Model):
    menu_items = models.JSONField(default=list)  # Store list of item keys from OrderModel.MENU_CHOICES
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Active Menu ({self.updated_at})"
