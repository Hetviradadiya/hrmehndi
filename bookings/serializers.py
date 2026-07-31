from rest_framework import serializers
from bookings.models import *

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
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='categories'
    )
    all_images = DesignImageSerializer(many=True, read_only=True)
    category_slugs = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = MehndiDesign
        fields = [
            'id', 'title', 'categories', 'category_ids',
            'cover_image', 'description', 'is_original_work', 
            'all_images', 'category_slugs','is_wishlisted', 'created_at'
        ]
        extra_kwargs = {
            'cover_image': {'required': False, 'allow_null': True}
        }

    def get_category_slugs(self, obj):
        return obj.get_category_slugs()

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        visitor_id = request.headers.get('X-Visitor-Id') or request.GET.get('visitor_id')
        if not visitor_id:
            return False
        return Wishlist.objects.filter(visitor__visitor_id=visitor_id, design=obj).exists()


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

class ReelCommentSerializer(serializers.ModelSerializer):
    visitor_id = serializers.CharField(source='visitor.visitor_id', read_only=True)

    class Meta:
        model = ReelComment
        fields = ['id', 'visitor_id', 'text', 'created_at']

class ReelSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = [
            'id', 'title', 'video_file', 'external_url', 
            'thumbnail', 'description', 'is_active', 'created_at',
            'likes_count', 'comments_count', 'is_liked', 'is_bookmarked'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        visitor_id = request.headers.get('X-Visitor-Id') or request.GET.get('visitor_id')
        if not visitor_id:
            return False
        return ReelLike.objects.filter(visitor__visitor_id=visitor_id, reel=obj).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        visitor_id = request.headers.get('X-Visitor-Id') or request.GET.get('visitor_id')
        if not visitor_id:
            return False
        return ReelBookmark.objects.filter(visitor__visitor_id=visitor_id, reel=obj).exists()
        
class ReelBookmark(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='reel_bookmarks')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('visitor', 'reel')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.visitor.visitor_id[:8]} -> Bookmarked Reel {self.reel.id}"
