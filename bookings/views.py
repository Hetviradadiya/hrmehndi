import urllib.parse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MehndiDesign, BookingInquiry


def home_view(request):
    designs = MehndiDesign.objects.all().order_by('-created_at')

    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        phone_number = request.POST.get('phone_number')
        event_date = request.POST.get('event_date')
        event_location = request.POST.get('event_location')
        service_type = request.POST.get('service_type')
        number_of_people = request.POST.get('number_of_people', 1)
        notes = request.POST.get('notes', '')

        # 1. Save to Database
        BookingInquiry.objects.create(
            client_name=client_name,
            phone_number=phone_number,
            event_date=event_date,
            event_location=event_location,
            service_type=service_type,
            number_of_people=number_of_people,
            notes=notes
        )

        # 2. Format WhatsApp Message
        your_whatsapp_number = "919875288682"  # Replace with your actual phone number (with country code, e.g., 91 for India)

        message_text = f"""Hello HR Mehndi! 👋
I would like to book a session. Here are my details:

👤 *Name:* {client_name}
📞 *Phone:* {phone_number}
📅 *Date:* {event_date}
📍 *Location:* {event_location}
✨ *Service:* {service_type}
👥 *Guests:* {number_of_people}
📝 *Notes:* {notes or 'N/A'}

Please confirm availability!"""

        # 3. Encode text for URL
        encoded_message = urllib.parse.quote(message_text)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={your_whatsapp_number}&text={encoded_message}"

        # 4. Redirect client to WhatsApp
        return redirect(whatsapp_url)

    return render(request, 'home.html', {'designs': designs})
