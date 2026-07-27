import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import MehndiDesign, BookingInquiry, Category

def home_view(request):
    # Homepage portfolio shows ONLY real original works
    designs = MehndiDesign.objects.filter(is_original_work=True).order_by('-created_at')

    # Show all categories in the UI, even if they have no designs yet.
    categories = Category.objects.all().order_by('name')

    # categories = MehndiDesign.objects.values_list('service_type', flat=True).distinct()\

    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        phone_number = request.POST.get('phone_number')
        event_date = request.POST.get('event_date')
        event_location = request.POST.get('event_location')
        service_type = request.POST.get('service_type')
        number_of_people = request.POST.get('number_of_people', 1)
        notes = request.POST.get('notes', '')
        attachment = request.FILES.get('attachment')

        inquiry = BookingInquiry.objects.create(
            client_name=client_name,
            phone_number=phone_number,
            event_date=event_date,
            event_location=event_location,
            service_type=service_type,
            number_of_people=number_of_people,
            notes=notes,
            attachment=attachment
        )

        your_whatsapp_number = "919875288682"
        message_text = f"""Hello HETVI! 👋
I would like to book a session. Here are my details:

👤 *Name:* {client_name}
📞 *Phone:* {phone_number}
📅 *Event Date:* {event_date}
📍 *Location:* {event_location}
✨ *Service:* {service_type}
👥 *Guests:* {number_of_people}
📝 *Notes:* {notes or 'N/A'}
"""

        if inquiry.attachment:
            attachment_url = request.build_absolute_uri(inquiry.attachment.url)
            message_text += f"""
🖼️ *Design Reference Image:*
👉 {attachment_url}
_(Tap the link above to view the selected design)_
"""

        message_text += "\nPlease confirm availability! 🙏"

        encoded_message = urllib.parse.quote(message_text)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={your_whatsapp_number}&text={encoded_message}"
        return redirect(whatsapp_url)

    return render(request, 'home.html', {
        'designs': designs,
        'categories': categories
    })


def gallery_view(request):
    gallery_images = []
    designs = MehndiDesign.objects.prefetch_related('categories', 'all_images').order_by('-created_at')
    for design in designs:
        cats = [c.slug.lower() for c in design.categories.all()]
        cat_names = [c.name for c in design.categories.all()]
        category_display = ' · '.join(cat_names) if cat_names else 'General'
        display_title = design.title or category_display
        gallery_images.append({
            'url': design.cover_image.url,
            'title': display_title,
            'caption': design.description or '',
            'category_slugs': ' '.join(cats) if cats else 'general',
            'category_name': category_display,
            'is_original': design.is_original_work,
        })
        for img in design.all_images.all():
            gallery_images.append({
                'url': img.image.url,
                'title': display_title,
                'caption': img.caption or design.description or '',
                'category_slugs': ' '.join(cats) if cats else 'general',
                'category_name': category_display,
                'is_original': design.is_original_work,
            })

    categories = Category.objects.all().order_by('name')

    return render(request, 'gallery.html', {
        'gallery_images': gallery_images,
        'categories': categories,
    })


@login_required
def admin_bookings_view(request):
    """Custom admin dashboard — protected by login."""
    # Status filter
    status_filter = request.GET.get('status', 'ALL')

    all_bookings = BookingInquiry.objects.all().order_by('-created_at')

    if status_filter != 'ALL':
        bookings = all_bookings.filter(status=status_filter)
    else:
        bookings = all_bookings

    # Stats counts
    counts = {
        'total': all_bookings.count(),
        'pending': all_bookings.filter(status='PENDING').count(),
        'confirmed': all_bookings.filter(status='CONFIRMED').count(),
        'completed': all_bookings.filter(status='COMPLETED').count(),
        'cancelled': all_bookings.filter(status='CANCELLED').count(),
    }

    return render(request, 'admin_bookings.html', {
        'bookings': bookings,
        'counts': counts,
        'status_filter': status_filter,
    })


@login_required
@require_POST
def update_booking_status(request, booking_id):
    """AJAX endpoint to update booking status."""
    booking = get_object_or_404(BookingInquiry, id=booking_id)
    new_status = request.POST.get('status')
    valid_statuses = [s[0] for s in BookingInquiry.STATUS_CHOICES]

    if new_status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    booking.status = new_status
    booking.save()
    return JsonResponse({'success': True, 'new_status': new_status})