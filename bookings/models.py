from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. Bridal, Arabic, Party, Crafts")
    slug = models.SlugField(max_length=50, unique=True, help_text="Short name used for filtering (e.g. bridal, arabic, party, crafts)")

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class BookingInquiry(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    client_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    event_date = models.DateField()
    event_location = models.CharField(max_length=255)
    service_type = models.CharField(max_length=100, default='Bridal Mehndi')
    number_of_people = models.IntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    attachment = models.ImageField(upload_to='booking_attachments/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking Inquiry'
        verbose_name_plural = 'Booking Inquiries'

    def __str__(self):
        return f"{self.client_name} - {self.event_date}"


class MehndiDesign(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='designs', blank=True)
    cover_image = models.ImageField(upload_to='covers/')
    description = models.TextField(blank=True, null=True)
    is_original_work = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mehndi Design'
        verbose_name_plural = 'Mehndi Designs'

    def __str__(self):
        return self.title or f"Mehndi Design #{self.id}"

    # Helper method to get category slugs as string for HTML filtering
    def get_category_slugs(self):
        return " ".join([cat.slug.lower() for cat in self.categories.all()])


class DesignImage(models.Model):
    design = models.ForeignKey(MehndiDesign, related_name='all_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Design Image'
        verbose_name_plural = 'Design Images'

    def __str__(self):
        return f"Image for {self.design.title or self.design.id}"


class ServicePackage(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Emoji or icon identifier (e.g. 💍, 🎉, 🌿, 🎨)")
    price = models.CharField(max_length=50, help_text="e.g. ₹2,500+ or ₹250/person")
    duration = models.CharField(max_length=50, help_text="e.g. 10-12 hrs or 1-2 hrs/person")
    description = models.TextField()
    features = models.JSONField(default=list, help_text="List of feature bullet points")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Service Package'
        verbose_name_plural = 'Service Packages'

    def __str__(self):
        return self.title

class Reel(models.Model):
    title = models.CharField(max_length=150,blank=True, null=True,)
    video_file = models.FileField(upload_to='reels/videos/')
    external_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='reels/thumbnails/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reel / Video'
        verbose_name_plural = 'Reels / Videos'

    def __str__(self):
        return self.title or f"Reel #{self.id}"


class Visitor(models.Model):
    visitor_id = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_visited = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['visitor_id'], name='idx_visitor_id'),
        ]
        verbose_name = 'visitor'
        verbose_name_plural = 'visitors'

    def __str__(self):
        return self.visitor_id


class Wishlist(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='wishlist_items')
    design = models.ForeignKey(MehndiDesign, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('visitor', 'design')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.visitor.visitor_id[:8]} -> {self.design.title or self.design.id}"

class ReelLike(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='reel_likes')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('visitor', 'reel')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.visitor.visitor_id[:8]} -> Reel {self.reel.id}"

class ReelComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='reel_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.visitor.visitor_id[:8]} on Reel {self.reel.id}"
        