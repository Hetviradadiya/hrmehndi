from django.contrib import admin
from .models import BookingInquiry, MehndiDesign, DesignImage


class DesignImageInline(admin.TabularInline):
    model = DesignImage
    extra = 3
    fields = ('image', 'caption')


@admin.register(MehndiDesign)
class MehndiDesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_original_work', 'created_at')
    list_filter = ('is_original_work',)
    search_fields = ('title', 'description')
    inlines = [DesignImageInline]


@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'phone_number', 'event_date', 'event_location', 'service_type', 'status', 'created_at')
    list_filter = ('status', 'service_type', 'event_date')
    search_fields = ('client_name', 'phone_number', 'event_location')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(DesignImage)
class DesignImageAdmin(admin.ModelAdmin):
    list_display = ('design', 'caption')
    list_filter = ('design',)
