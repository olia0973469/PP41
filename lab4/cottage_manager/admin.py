from django.contrib import admin
from . import models


class CottageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(models.Booking)
admin.site.register(models.Cottage, CottageAdmin)
admin.site.register(models.Amenities)
