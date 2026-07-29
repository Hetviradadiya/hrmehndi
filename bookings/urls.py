from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.MehndiDesignViewSet, basename='product')
router.register(r'reels', views.ReelViewSet, basename='reel')

urlpatterns = [
    path('api/categories/', views.category_list_api, name='api_categories'),
    path('api/gallery/', views.gallery_api, name='api_gallery'),
    path('api/bookings/create/', views.create_booking_api, name='api_create_booking'),
    path('api/my-bookings/', views.admin_bookings_api, name='api_admin_bookings'),
    path('api/my-bookings/update/<int:booking_id>/', views.update_booking_status_api, name='api_update_booking_status'),
    path('api/auth/login/', views.login_api, name='api_login'),
    path('api/auth/logout/', views.logout_api, name='api_logout'),
    path('api/auth/me/', views.user_info_api, name='api_user_info'),
    path('api/services/', views.service_list_api, name='api_services'),

    path('api/', include(router.urls)),
]


