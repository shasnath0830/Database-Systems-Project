from django.contrib import admin
from django.urls import path, include
from tracker.views import delete_package

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
    path('delete_package/<int:package_id>/', delete_package, name='delete_package'),
]