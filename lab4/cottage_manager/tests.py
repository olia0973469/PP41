"""
Tests for cottage manager APIs.
"""
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase

from cottage_manager import models
from django.utils import timezone


class ModelTests(TestCase):
    """Test models."""

    def test_create_cottage(self):
        """Test creating a cottage is successful."""
        cottage = models.Cottage.objects.create(
            name='Sample cottage name',
            capacity=5,
            price_per_night=Decimal('500.50')
        )

        self.assertEqual('Sample cottage name', cottage.name)
        self.assertEqual(5, cottage.capacity)
        self.assertEqual(Decimal(500.50), cottage.price_per_night)

    def test_create_amenity(self):
        """Test creating an amenity is successful."""
        amenity = models.Amenities.objects.create(
            name='Sample amenity name',
            additional_capacity=5
        )

        self.assertEqual('Sample amenity name', amenity.name)
        self.assertEqual(5, amenity.additional_capacity)

    def test_create_cottage_with_additional_capacity(self):
        """Test calculating a cottage total capacity is right."""
        amenity = models.Amenities.objects.create(
            name='Sample amenity name',
            additional_capacity=1
        )
        cottage = models.Cottage.objects.create(
            name='Sample cottage name',
            base_capacity=5,
            price_per_night=Decimal('500.50')
        )

        cottage.amenities.add(amenity)
        cottage.refresh_from_db()

        self.assertEqual('Sample cottage name', cottage.name)
        self.assertEqual(6, cottage.capacity)

    def test_create_booking(self):
        """Test creating a booking is successful."""
        cottage = models.Cottage.objects.create(
            name='Sample cottage name',
            capacity=5,
            price_per_night=Decimal('500.50')
        )
        check_in = timezone.now().date() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)
        booking = models.Booking.objects.create(
            cottage=cottage,
            check_in=check_in,
            check_out=check_out,
            customer_name="username",
            customer_email="example@example.com"
        )

        self.assertEqual(booking.check_in, check_in)
        self.assertEqual(booking.check_out, check_out)
        self.assertEqual(booking.customer_name, "username")
        self.assertEqual(booking.cottage, cottage)
