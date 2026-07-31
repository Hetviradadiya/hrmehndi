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
from rest_framework.views import APIView
from bookings.models import *
from bookings.serializers import *
from bookings.pagination import *


class MehndiDesignViewSet(viewsets.ModelViewSet):
    queryset = MehndiDesign.objects.all().order_by('-created_at')
    serializer_class = MehndiDesignSerializer
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Save design instance first
        design = serializer.save()
        self._handle_cover_and_gallery(design)

    def perform_update(self, serializer):
        design = serializer.save()
        
        # # If user explicitly wants to replace existing gallery images
        # if self.request.data.get('clear_gallery') == 'true':
        #     design.all_images.all().delete()

        self._handle_cover_and_gallery(design)

    def _handle_cover_and_gallery(self, design):
        gallery_images = self.request.FILES.getlist('gallery_images')

        # Save all secondary gallery images
        for img in gallery_images:
            DesignImage.objects.create(design=design, image=img)

        # Fallback: If no cover_image was provided, automatically set the first gallery image as cover_image
        if not design.cover_image and gallery_images:
            design.cover_image = gallery_images[0]
            design.save()

class ReelViewSet(viewsets.ModelViewSet):
    queryset = Reel.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ReelSerializer
    authentication_classes = [TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = ReelsResultsSetPagination


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def category_list_api(request):
    categories = Category.objects.all().order_by('name')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def gallery_api(request):
    designs = MehndiDesign.objects.prefetch_related('categories', 'all_images').order_by('-created_at')
    
    # 1. Filter by Original Works if requested
    originals_only = request.GET.get('original')
    if originals_only == 'true':
        designs = designs.filter(is_original_work=True)

    # 2. Filter by Category Slug or ID if passed in URL query params
    category_param = request.GET.get('category')
    if category_param and category_param.lower() != 'all':
        if category_param.isdigit():
            # If an integer ID is passed
            designs = designs.filter(categories__id=category_param)
        else:
            # If a slug/name string is passed (e.g., 'arabic', 'bridal')
            designs = designs.filter(categories__slug__iexact=category_param)

    # Instantiate and execute manual pagination for function-based view
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(designs, request)
    
    if page is not None:
        serializer = MehndiDesignSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    serializer = MehndiDesignSerializer(designs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
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
@authentication_classes([])
@permission_classes([AllowAny])
def logout_api(request):
    if request.user and request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
    logout(request)
    return Response({'status': True, 'message': 'Logged out successfully.'})


@api_view(['GET'])
@authentication_classes([])
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
@authentication_classes([])
@permission_classes([AllowAny])
def service_list_api(request):
    services = ServicePackage.objects.filter(is_active=True).order_by('order', 'id')
    serializer = ServicePackageSerializer(services, many=True)
    return Response(serializer.data)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class RegisterVisitorAPIView(APIView):
    """
    POST: Register or update visitor ID along with GPS location coordinates.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        visitor_id = request.data.get('visitor_id') or request.headers.get('X-Visitor-Id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        visitor, created = Visitor.objects.get_or_create(visitor_id=visitor_id)

        if latitude is not None:
            visitor.latitude = latitude
        if longitude is not None:
            visitor.longitude = longitude

        visitor.ip_address = get_client_ip(request)
        visitor.save()

        return Response({
            'status': True,
            'created': created,
            'visitor_id': visitor.visitor_id,
            'latitude': visitor.latitude,
            'longitude': visitor.longitude
        }, status=status.HTTP_200_OK)


class WishlistAPIView(APIView):
    """
    GET: Retrieve all wishlisted designs for a visitor.
    POST: Toggle wishlist status for a specific design.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        visitor_id = request.headers.get('X-Visitor-Id') or request.GET.get('visitor_id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
        wishlist_items = Wishlist.objects.filter(visitor=visitor).select_related('design')
        designs = [item.design for item in wishlist_items]

        serializer = MehndiDesignSerializer(designs, many=True, context={'request': request})
        return Response({'status': True, 'wishlist': serializer.data})

    def post(self, request):
        visitor_id = request.headers.get('X-Visitor-Id') or request.data.get('visitor_id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        design_id = request.data.get('design_id')
        if not design_id:
            return Response({'status': False, 'error': 'design_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
        design = get_object_or_404(MehndiDesign, id=design_id)

        wishlist_item, created = Wishlist.objects.get_or_create(visitor=visitor, design=design)

        if not created:
            wishlist_item.delete()
            return Response({'status': True, 'is_wishlisted': False, 'message': 'Removed from wishlist'})

        return Response({'status': True, 'is_wishlisted': True, 'message': 'Added to wishlist'})


class ToggleReelLikeAPIView(APIView):
    """
    POST: Toggle like status for a Reel and return the updated count.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        visitor_id = request.headers.get('X-Visitor-Id') or request.data.get('visitor_id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        reel_id = request.data.get('reel_id')
        if not reel_id:
            return Response({'status': False, 'error': 'reel_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
        reel = get_object_or_404(Reel, id=reel_id)

        like_item, created = ReelLike.objects.get_or_create(visitor=visitor, reel=reel)

        if not created:
            like_item.delete()
            return Response({
                'status': True,
                'is_liked': False,
                'likes_count': reel.likes.count(),
                'message': 'Reel unliked'
            })

        return Response({
            'status': True,
            'is_liked': True,
            'likes_count': reel.likes.count(),
            'message': 'Reel liked'
        })

class ReelCommentAPIView(APIView):
    """
    GET: List all comments for a specific reel.
    POST: Add a new comment to a reel.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, reel_id):
        reel = get_object_or_404(Reel, id=reel_id)
        comments = reel.comments.all().select_related('visitor')
        serializer = ReelCommentSerializer(comments, many=True)
        return Response({
            'status': True,
            'comments_count': comments.count(),
            'comments': serializer.data
        })

    def post(self, request, reel_id):
        visitor_id = request.headers.get('X-Visitor-Id') or request.data.get('visitor_id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        text = request.data.get('text', '').strip()
        if not text:
            return Response({'status': False, 'error': 'Comment text cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
        reel = get_object_or_404(Reel, id=reel_id)

        comment = ReelComment.objects.create(reel=reel, visitor=visitor, text=text)
        serializer = ReelCommentSerializer(comment)

        return Response({
            'status': True,
            'comments_count': reel.comments.count(),
            'comment': serializer.data,
            'message': 'Comment added successfully'
        }, status=status.HTTP_201_CREATED)

class ReelBookmarkAPIView(APIView):
    """
    GET: Retrieve all bookmarked/saved reels for a visitor.
    POST: Toggle bookmark/save status for a Reel using the Visitor foreign key.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        visitor_id = request.headers.get('X-Visitor-Id') or request.GET.get('visitor_id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            visitor = Visitor.objects.get(visitor_id=visitor_id)
        except Visitor.DoesNotExist:
            return Response({'status': True, 'count': 0, 'bookmarks': []}, status=status.HTTP_200_OK)

        # Retrieve all bookmarked reels for this visitor
        bookmark_items = ReelBookmark.objects.filter(visitor=visitor).select_related('reel').order_by('-created_at')
        reels = [item.reel for item in bookmark_items if item.reel.is_active]

        serializer = ReelSerializer(reels, many=True, context={'request': request})
        return Response({
            'status': True,
            'count': len(reels),
            'bookmarks': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        visitor_id = request.headers.get('X-Visitor-Id') or request.data.get('visitor_id')
        if not visitor_id:
            return Response({'status': False, 'error': 'visitor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        reel_id = request.data.get('reel_id')
        if not reel_id:
            return Response({'status': False, 'error': 'reel_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
        reel = get_object_or_404(Reel, id=reel_id)

        bookmark_item, created = ReelBookmark.objects.get_or_create(visitor=visitor, reel=reel)

        if not created:
            bookmark_item.delete()
            return Response({
                'status': True,
                'is_bookmarked': False,
                'message': 'Reel removed from saved bookmarks'
            }, status=status.HTTP_200_OK)

        return Response({
            'status': True,
            'is_bookmarked': True,
            'message': 'Reel saved to bookmarks'
        }, status=status.HTTP_201_CREATED)
