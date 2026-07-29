from django.contrib import admin
from django.utils.html import format_html
from .models import BookingInquiry, MehndiDesign, DesignImage, Category,Reel

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class DesignImageInline(admin.TabularInline):
    model = DesignImage
    extra = 3
    fields = ('image', 'caption')


@admin.register(MehndiDesign)
class MehndiDesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_categories', 'is_original_work', 'created_at')
    list_filter = ('categories', 'is_original_work')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',) 
    inlines = [DesignImageInline]

    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = 'Categories'


@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'phone_number', 'event_date', 'event_location', 'service_type', 'attachment_preview', 'status', 'created_at')
    list_filter = ('status', 'service_type', 'event_date')
    search_fields = ('client_name', 'phone_number', 'event_location')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def attachment_preview(self, obj):
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">View file</a>', obj.attachment.url)
        return '-'
    attachment_preview.short_description = 'Attachment'

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    