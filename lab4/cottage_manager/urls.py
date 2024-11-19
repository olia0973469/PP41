"""
URL mapping for the resort app.
"""
from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from cottage_manager import views

router = DefaultRouter()
router.register(r'cottages', views.CottageViewSet)
router.register(r'amenities', views.AmenitiesViewSet)
router.register(r'booking', views.BookingViewSet)

app_name = 'cottage-manager'

urlpatterns = [
    path('', include(router.urls)),
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('cottage-availability/', views.CottageAvailabilityView.as_view(), name='cottage-availability'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
]
