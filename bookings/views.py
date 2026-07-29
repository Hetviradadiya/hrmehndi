import urllib.parse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from bookings.models import *
from bookings.serializers import *


class MehndiDesignViewSet(viewsets.ModelViewSet):
    queryset = MehndiDesign.objects.all().order_by('-created_at')
    serializer_class = MehndiDesignSerializer
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # Dynamically set permissions: GET is open to anyone, CUD (Create/Update/Delete) requires Admin Auth
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # Handle multiple gallery images upload during create/update
    def perform_create(self, serializer):
        design = serializer.save()
        self._handle_gallery_images(design)

    def perform_update(self, serializer):
        design = serializer.save()
        self._handle_gallery_images(design)

    def _handle_gallery_images(self, design):
        gallery_images = self.request.FILES.getlist('gallery_images')
        for img in gallery_images:
            DesignImage.objects.create(design=design, image=img)

class ReelViewSet(viewsets.ModelViewSet):
    queryset = Reel.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ReelSerializer
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_api(request):
    categories = Category.objects.all().order_by('name')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def gallery_api(request):
    designs = MehndiDesign.objects.prefetch_related('categories', 'all_images').order_by('-created_at')
    
    # Check if request is filtering only original works (for Home portfolio)
    originals_only = request.GET.get('original')
    if originals_only == 'true':
        designs = designs.filter(is_original_work=True)

    serializer = MehndiDesignSerializer(designs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking_api(request):
    serializer = BookingInquirySerializer(data=request.data)
    if serializer.is_valid():
        inquiry = serializer.save()

        # Build WhatsApp Redirect Link
        your_whatsapp_number = "919875288682"
        message_text = f"""Hello HETVI! 👋
I would like to book a session. Here are my details:

👤 *Name:* {inquiry.client_name}
📞 *Phone:* {inquiry.phone_number}
📅 *Event Date:* {inquiry.event_date}
📍 *Location:* {inquiry.event_location}
✨ *Service:* {inquiry.service_type}
👥 *Guests:* {inquiry.number_of_people}
📝 *Notes:* {inquiry.notes or 'N/A'}
"""

        if inquiry.attachment:
            attachment_url = request.build_absolute_uri(inquiry.attachment.url)
            message_text += f"\n🖼️ *Design Reference Image:*\n👉 {attachment_url}\n"

        message_text += "\nPlease confirm availability! 🙏"
        encoded_message = urllib.parse.quote(message_text)
        whatsapp_url = f"https://api.whatsapp.com/send?phone={your_whatsapp_number}&text={encoded_message}"

        return Response({
            'status': True,
            'booking': serializer.data,
            'whatsapp_url': whatsapp_url
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_bookings_api(request):
    status_filter = request.GET.get('status', 'ALL')
    all_bookings = BookingInquiry.objects.all().order_by('-created_at')

    if status_filter != 'ALL':
        filtered_bookings = all_bookings.filter(status=status_filter)
    else:
        filtered_bookings = all_bookings

    serializer = BookingInquirySerializer(filtered_bookings, many=True, context={'request': request})

    counts = {
        'total': all_bookings.count(),
        'pending': all_bookings.filter(status='PENDING').count(),
        'confirmed': all_bookings.filter(status='CONFIRMED').count(),
        'completed': all_bookings.filter(status='COMPLETED').count(),
        'cancelled': all_bookings.filter(status='CANCELLED').count(),
    }

    return Response({
        'bookings': serializer.data,
        'counts': counts,
        'status_filter': status_filter
    })


@api_view(['PATCH', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_booking_status_api(request, booking_id):

    booking = get_object_or_404(BookingInquiry, id=booking_id)
    new_status = request.data.get('status')
    valid_statuses = [s[0] for s in BookingInquiry.STATUS_CHOICES]

    if new_status not in valid_statuses:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = new_status
    booking.save()
    return Response({'status': True, 'new_status': new_status})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'status': False, 'error': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'status': True,
            'token': f"Token {token.key}",
            'user': {

                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
        })
    else:
        return Response({'status': False, 'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_api(request):
    if request.user and request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
    logout(request)
    return Response({'status': True, 'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def user_info_api(request):
    if request.user and request.user.is_authenticated:
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({
            'status': True,
            'is_authenticated': True,
            'token': f"Token {token.key}",
            'user': {

                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            }
        })
    return Response({
        'status': False,
        'is_authenticated': False,
        'user': None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def service_list_api(request):
    services = ServicePackage.objects.filter(is_active=True).order_by('order', 'id')
    serializer = ServicePackageSerializer(services, many=True)
    return Response(serializer.data)
