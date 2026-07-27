from django.db import models


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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking Inquiry'
        verbose_name_plural = 'Booking Inquiries'

    def __str__(self):
        return f"{self.client_name} - {self.event_date}"


class MehndiDesign(models.Model):
    title = models.CharField(max_length=150)
    cover_image = models.ImageField(upload_to='covers/')
    description = models.TextField(blank=True, null=True)
    is_original_work = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mehndi Design'
        verbose_name_plural = 'Mehndi Designs'

    def __str__(self):
        return self.title


class DesignImage(models.Model):
    design = models.ForeignKey(MehndiDesign, related_name='all_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Design Image'
        verbose_name_plural = 'Design Images'

    def __str__(self):
        return f"Image for {self.design.title}"
