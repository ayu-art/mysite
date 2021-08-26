from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('pools/', include('pools.urls')),
    path('admin/', admin.site.urls),
]
