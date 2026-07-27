from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('my-bookings/', views.admin_bookings_view, name='admin_bookings'),
    path('my-bookings/update/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
]
