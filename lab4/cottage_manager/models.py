from decimal import Decimal

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError


class Amenities(models.Model):
    """Amenities for cottages and hotel."""
    name = models.CharField(max_length=100)
    additional_capacity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} (+{self.additional_capacity})"

    class Meta:
        verbose_name_plural = "Amenities"


class Cottage(models.Model):
    """Cottage object."""
    CATEGORY_CHOICES = [
        ('standard', 'Standard'),
        ('luxury', 'Luxury'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=False, db_index=True, unique=True)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default='standard')
    base_capacity = models.IntegerField(default=0)
    capacity = models.IntegerField(editable=False, default=0)
    amenities = models.ManyToManyField(Amenities, blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    base_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def calculate_total_capacity_and_expenses(self):
        """Calculate the total capacity, price per night and expenses of the cottage including amenities."""
        additional_capacity = sum(amenity.additional_capacity for amenity in self.amenities.all())
        self.capacity = Decimal(self.base_capacity) + additional_capacity
        self.price_per_night = Decimal(self.base_price) + sum(amenity.price for amenity in self.amenities.all())
        self.expenses = Decimal(self.base_expenses) + sum(amenity.expenses for amenity in self.amenities.all())

    def __str__(self):
        return f'{self.name}, {self.category}, max. guests - {self.capacity}, price - {self.price_per_night}'


@receiver(m2m_changed, sender=Cottage.amenities.through)
def update_total_capacity_and_expenses(sender, instance, **kwargs):
    """Update total capacity and expenses when amenities are added or removed."""
    instance.calculate_total_capacity_and_expenses()
    instance.save()


class Booking(models.Model):
    """Booking model for managing cottage reservations."""
    cottage = models.ForeignKey(Cottage, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    is_confirmed = models.BooleanField(default=False)

    def calculate_price(self):
        """Calculate the price based on the number of nights and cottage price."""
        nights = (self.check_out - self.check_in).days
        if nights <= 0:
            raise ValidationError("Invalid dates: Check-out must be after check-in.")

        price = (Decimal(self.cottage.price_per_night)) * Decimal(nights)

        if self.check_in.month in [11, 3] or self.check_out.month in [11, 3]:
            discount = price * Decimal('0.20')
            price -= discount

        return price

    def save(self, *args, **kwargs):
        self.clean()
        self.price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Booking for {self.customer_name} in {self.cottage.name}, {self.price}$'
