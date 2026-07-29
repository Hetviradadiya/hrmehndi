from django.core.management.base import BaseCommand
from bookings.models import ServicePackage

class Command(BaseCommand):
    help = 'Seeds initial service packages & pricing into the database'

    def handle(self, *args, **options):
        services_data = [
            {
                "title": "Bridal Mehndi",
                "icon": "💍",
                "price": "₹2,500+",
                "duration": "10-12 hrs",
                "description": "Full bridal package — both hands & feet with intricate traditional or fusion designs, includes touch-up service.",
                "features": [
                    "Both hands & feet",
                    "Intricate fine-line work",
                    "Design consultation",
                    "Touch-up on event day"
                ],
                "order": 1,
                "is_active": True
            },
            {
                "title": "Guest / Party Mehndi",
                "icon": "🎉",
                "price": "₹250/person",
                "duration": "1-2 hrs/person",
                "description": "High-speed, beautiful designs for wedding guests, sangeet, or corporate events.",
                "features": [
                    "Single hand or both",
                    "Arabic or simple designs",
                    "Bulk booking discounts",
                    "On-site service available"
                ],
                "order": 2,
                "is_active": True
            },
            {
                "title": "Arabic / Fusion",
                "icon": "🌿",
                "price": "₹300+",
                "duration": "1-2 hrs",
                "description": "Modern Arabic, geometric, and fusion designs for pre-wedding shoots or casual occasions.",
                "features": [
                    "Personalized design selection",
                    "Black or natural henna option",
                    "Minimalist or elaborate styles",
                    "Photo-shoot ready"
                ],
                "order": 3,
                "is_active": True
            },
            {
                "title": "Crafts & Embroidery",
                "icon": "🎨",
                "price": "₹500+",
                "duration": "Custom",
                "description": "Handcrafted lippan art, resin art pieces, paper crafts, and garment embroidery — unique artisan creations.",
                "features": [
                    "Custom size & colors",
                    "Gift packaging available",
                    "Bulk/corporate orders",
                    "Delivery across Gujarat"
                ],
                "order": 4,
                "is_active": True
            }
        ]

        count = 0
        for data in services_data:
            obj, created = ServicePackage.objects.update_or_create(
                title=data["title"],
                defaults=data
            )
            count += 1
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} service package: {obj.title}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} service packages into the database!"))
