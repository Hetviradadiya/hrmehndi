from rest_framework import serializers
from .models import Category, BookingInquiry, MehndiDesign, DesignImage, ServicePackage, Reel

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class DesignImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignImage
        fields = ['id', 'image', 'caption']


class MehndiDesignSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    all_images = DesignImageSerializer(many=True, read_only=True)
    category_slugs = serializers.SerializerMethodField()

    class Meta:
        model = MehndiDesign
        fields = [
            'id', 'title', 'categories', 'cover_image', 
            'description', 'is_original_work', 'all_images', 
            'category_slugs', 'created_at'
        ]

    def get_category_slugs(self, obj):
        return obj.get_category_slugs()


class BookingInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingInquiry
        fields = [
            'id', 'client_name', 'phone_number', 'email', 
            'event_date', 'event_location', 'service_type', 
            'number_of_people', 'notes', 'attachment', 
            'status', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']


class ServicePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePackage
        fields = [
            'id', 'title', 'icon', 'price', 'duration', 
            'description', 'features', 'is_active', 'order', 
            'created_at'
        ]

class ReelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reel
        fields = [
            'id', 'title', 'video_file', 'external_url', 
            'thumbnail', 'description', 'is_active', 'created_at'
        ]