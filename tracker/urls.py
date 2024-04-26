from django.urls import path
from . import views
from .views import visualization
from .views import advanced_feature
from .views import admin_dashboard
from tracker.views import delete_package


urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('customer/', views.customer, name='customer'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('create_driver/', views.create_driver, name='create_driver'),
    path('create_vehicle/', views.create_vehicle, name='create_vehicle'),
    path('assign_package/', views.assign_package, name='assign_package'),
    path('delete_package/', views.delete_package, name='delete_package'),
    path('update_package/<int:package_id>/', views.update_package, name='update_package'),
    path('delete_shipment/<int:shipment_id>/', views.delete_shipment, name='delete_shipment'),
    path('update_shipment/<int:shipment_id>/', views.update_shipment, name='update_shipment'),
    path('update_driver/<int:driver_id>/', views.update_driver, name='update_driver'),
    path('delete_driver/<int:driver_id>/', views.delete_driver, name='delete_driver'),
    path('update_vehicle/<int:vehicle_id>/', views.update_vehicle, name='update_vehicle'),
    path('delete_vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('visualization/', visualization, name='visualization'),
    path('advanced_feature/', advanced_feature, name='advanced_feature'),
    path('search/', views.search_database, name='search_database'),
    path('update_shipment_status/<int:shipment_id>/', views.update_shipment_status, name='update_shipment_status'),
    path('delete_package/<int:package_id>/', delete_package, name='delete_package'),
    
    
]