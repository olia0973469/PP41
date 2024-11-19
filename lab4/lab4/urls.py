from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cottage-manager/', include('cottage_manager.urls'))
]
