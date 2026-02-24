"""Comprehensive service templates for salon onboarding.

This module contains 75+ service templates across proper ServiceCategory enum values:
- haircut: 16 services
- hair_color: 10 services
- hair_treatment: 8 services
- facial: 10 services
- spa: 6 services (body treatments)
- manicure: 4 services
- pedicure: 4 services
- waxing: 2 services
- threading: 1 service
- bridal: 6 services
- other: 9 services (styling + groom)
"""

from typing import Dict, List, Any
import uuid


def _generate_service_id(name: str) -> str:
    """Generate a unique service ID."""
    return f"svc_{uuid.uuid4().hex[:12]}"


def _create_service_template(
    name: str,
    category: str,
    base_price: int,
    duration_minutes: int,
    description: str = "",
    resource_type: str = "any",
) -> Dict[str, Any]:
    """Create a properly structured service template matching Service schema."""
    return {
        "service_id": _generate_service_id(name),
        "name": name,
        "category": category,
        "description": description,
        "pricing": {
            "base_price": float(base_price),
            "is_variable_pricing": False,
            "peak_hours_surcharge": 0.0,
            "weekend_surcharge": 0.0,
            "member_discount_percent": 0.0,
        },
        "duration": {
            "base_minutes": duration_minutes,
            "buffer_before": 0,
            "buffer_after": 0,
        },
        "resource_requirement": {
            "resource_type": resource_type,
            "is_exclusive": False,
        },
        "is_active": True,
        "is_popular": False,
        "is_featured": False,
        "gst_rate": 0.05,
    }


# ============================================================================
# SERVICE TEMPLATES BY CATEGORY
# ============================================================================

SERVICE_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    # ========================================================================
    # HAIRCUT - 16 services
    # ========================================================================
    "haircut": [
        _create_service_template("Haircut Male", "haircut", 200, 30, "Professional men's haircut with styling", "chair_mens"),
        _create_service_template("Haircut Female", "haircut", 500, 45, "Women's haircut with precision cutting and styling", "chair_womens"),
        _create_service_template("Kids Cut", "haircut", 150, 20, "Gentle haircut for children under 12", "chair_womens"),
        _create_service_template("Buzz Cut", "haircut", 100, 15, "Short buzz cut with clippers", "chair_mens"),
        _create_service_template("Layer Cut", "haircut", 800, 60, "Multi-layered haircut for volume and texture", "chair_womens"),
        _create_service_template("Step Cut", "haircut", 700, 60, "Graduated step cut for a trendy look", "chair_womens"),
        _create_service_template("Bob Cut", "haircut", 600, 45, "Classic bob haircut with clean lines", "chair_womens"),
        _create_service_template("Pixie Cut", "haircut", 650, 45, "Short pixie cut for a bold look", "chair_womens"),
        _create_service_template("Undercut", "haircut", 400, 40, "Modern undercut with faded sides", "chair_mens"),
        _create_service_template("Fade Cut", "haircut", 350, 35, "Skin fade or taper fade haircut", "chair_mens"),
        _create_service_template("Trim", "haircut", 150, 20, "Basic trim to maintain current style", "any"),
        _create_service_template("Bangs/Fringe", "haircut", 200, 20, "Bangs or fringe cutting and styling", "chair_womens"),
        _create_service_template("U-Cut", "haircut", 550, 45, "U-shaped haircut for layered look", "chair_womens"),
        _create_service_template("V-Cut", "haircut", 550, 45, "V-shaped haircut with pointed ends", "chair_womens"),
        _create_service_template("Caesar Cut", "haircut", 250, 25, "Classic Caesar cut with short fringe", "chair_mens"),
        _create_service_template("Mullet", "haircut", 450, 40, "Business in front, party in back - modern mullet", "chair_mens"),
    ],
    
    # ========================================================================
    # HAIR_COLOR - 10 services
    # ========================================================================
    "hair_color": [
        _create_service_template("Global Color", "hair_color", 2500, 120, "Full head hair coloring with premium products", "chair_womens"),
        _create_service_template("Highlights", "hair_color", 3000, 150, "Foil highlights for dimension and contrast", "chair_womens"),
        _create_service_template("Root Touch-up", "hair_color", 800, 60, "Touch up roots to match existing color", "chair_womens"),
        _create_service_template("Balayage", "hair_color", 5000, 180, "Hand-painted natural highlights for sun-kissed look", "chair_womens"),
        _create_service_template("Ombre", "hair_color", 4500, 180, "Gradient color from dark to light", "chair_womens"),
        _create_service_template("Foilayage", "hair_color", 5500, 180, "Combination of balayage and foil techniques", "chair_womens"),
        _create_service_template("Color Correction", "hair_color", 6000, 240, "Fix previous color mistakes and achieve desired shade", "chair_womens"),
        _create_service_template("Toner/Gloss", "hair_color", 500, 30, "Toner to neutralize brassiness and add shine", "chair_womens"),
        _create_service_template("Bleach", "hair_color", 2000, 120, "Hair bleaching for lightening base color", "chair_womens"),
        _create_service_template("Fashion Color", "hair_color", 4000, 180, "Vibrant fashion colors like pink, blue, purple", "chair_womens"),
    ],
    
    # ========================================================================
    # HAIR_TREATMENT - 8 services
    # ========================================================================
    "hair_treatment": [
        _create_service_template("Keratin Treatment", "hair_treatment", 5000, 180, "Smoothing keratin treatment for frizz-free hair", "chair_womens"),
        _create_service_template("Smoothening", "hair_treatment", 3500, 150, "Chemical smoothing for manageable hair", "chair_womens"),
        _create_service_template("Rebonding", "hair_treatment", 6000, 240, "Permanent straightening for pin-straight hair", "chair_womens"),
        _create_service_template("Hair Spa", "hair_treatment", 1000, 60, "Deep conditioning spa treatment for hair health", "chair_womens"),
        _create_service_template("Scalp Treatment", "hair_treatment", 800, 45, "Treatment for dandruff, dryness, or oily scalp", "chair_womens"),
        _create_service_template("Hair Botox", "hair_treatment", 4000, 120, "Deep repair treatment for damaged hair", "chair_womens"),
        _create_service_template("Olaplex Treatment", "hair_treatment", 2500, 90, "Bond-building treatment for hair repair", "chair_womens"),
        _create_service_template("Protein Treatment", "hair_treatment", 1500, 60, "Protein-rich treatment for strength and elasticity", "chair_womens"),
    ],
    
    # ========================================================================
    # FACIAL - 10 services
    # ========================================================================
    "facial": [
        _create_service_template("Cleanup", "facial", 400, 30, "Basic cleanup with cleansing and toning", "room_treatment"),
        _create_service_template("Facial", "facial", 1000, 60, "Deep cleansing facial with massage and mask", "room_treatment"),
        _create_service_template("Bleach", "facial", 300, 20, "Face bleaching for even skin tone", "room_treatment"),
        _create_service_template("De-tan Facial", "facial", 1200, 60, "Specialized facial to remove tan and brighten skin", "room_treatment"),
        _create_service_template("Anti-Aging Facial", "facial", 2000, 75, "Rejuvenating facial targeting fine lines and wrinkles", "room_treatment"),
        _create_service_template("Acne Treatment Facial", "facial", 1500, 60, "Deep cleansing facial for acne-prone skin", "room_treatment"),
        _create_service_template("Gold Facial", "facial", 2500, 75, "Luxury gold facial for radiant, glowing skin", "room_treatment"),
        _create_service_template("Diamond Facial", "facial", 3000, 75, "Premium diamond facial for exfoliation and glow", "room_treatment"),
        _create_service_template("Fruit Facial", "facial", 1200, 60, "Natural fruit-based facial for fresh skin", "room_treatment"),
        _create_service_template("Skin Treatment", "skin_treatment", 1500, 60, "Specialized skin treatment for various concerns", "room_treatment"),
    ],
    
    # ========================================================================
    # SPA - 6 services (body treatments)
    # ========================================================================
    "spa": [
        _create_service_template("Body Spa", "spa", 2000, 90, "Full body spa treatment with massage", "room_spa"),
        _create_service_template("Body Massage", "spa", 1500, 60, "Relaxing full body massage", "room_spa"),
        _create_service_template("Aromatherapy Massage", "spa", 2000, 75, "Therapeutic massage with essential oils", "room_spa"),
        _create_service_template("Body Scrub", "spa", 1200, 45, "Exfoliating body scrub for smooth skin", "room_spa"),
        _create_service_template("Body Polish", "spa", 1500, 60, "Deep exfoliation with moisturizing polish", "room_spa"),
        _create_service_template("Body Wrap", "spa", 1800, 60, "Detoxifying or hydrating body wrap", "room_spa"),
    ],
    
    # ========================================================================
    # MANICURE - 4 services
    # ========================================================================
    "manicure": [
        _create_service_template("Manicure", "manicure", 400, 30, "Basic manicure with nail shaping and polish", "room_spa"),
        _create_service_template("Gel Manicure", "manicure", 800, 45, "Long-lasting gel polish manicure", "room_spa"),
        _create_service_template("Nail Art", "manicure", 600, 45, "Creative nail art designs", "room_spa"),
        _create_service_template("Nail Extension", "manicure", 1500, 60, "Acrylic or gel nail extensions", "room_spa"),
    ],
    
    # ========================================================================
    # PEDICURE - 4 services
    # ========================================================================
    "pedicure": [
        _create_service_template("Pedicure", "pedicure", 500, 45, "Relaxing pedicure with foot soak and massage", "room_spa"),
        _create_service_template("Gel Pedicure", "pedicure", 1000, 60, "Gel polish pedicure with extended wear", "room_spa"),
        _create_service_template("Foot Reflexology", "pedicure", 800, 30, "Therapeutic foot massage targeting pressure points", "room_spa"),
        _create_service_template("Head Massage", "spa", 500, 30, "Relaxing head and scalp massage", "chair_womens"),
    ],
    
    # ========================================================================
    # WAXING - 2 services
    # ========================================================================
    "waxing": [
        _create_service_template("Waxing - Full Body", "waxing", 1500, 60, "Full body waxing for smooth skin", "room_treatment"),
        _create_service_template("Waxing - Half Body", "waxing", 800, 30, "Half body waxing (arms or legs)", "room_treatment"),
    ],
    
    # ========================================================================
    # THREADING - 1 service
    # ========================================================================
    "threading": [
        _create_service_template("Threading", "threading", 100, 15, "Eyebrow and upper lip threading", "any"),
    ],
    
    # ========================================================================
    # BRIDAL - 6 services
    # ========================================================================
    "bridal": [
        _create_service_template("Bridal Package", "bridal", 25000, 300, "Complete bridal makeover including makeup, hair, and draping", "room_bridal"),
        _create_service_template("Bridal Makeup", "bridal", 15000, 120, "Professional bridal makeup with premium products", "room_bridal"),
        _create_service_template("Bridal Hair Styling", "bridal", 5000, 90, "Elegant bridal hairstyle with accessories", "room_bridal"),
        _create_service_template("Mehandi", "bridal", 3000, 120, "Traditional bridal mehandi (henna) application", "room_bridal"),
        _create_service_template("Pre-Bridal Package", "bridal", 8000, 180, "Pre-wedding beauty treatments including facials and spa", "room_bridal"),
        _create_service_template("Engagement Look", "bridal", 10000, 150, "Complete engagement ceremony look", "room_bridal"),
    ],
    
    # ========================================================================
    # OTHER - 9 services (styling + groom)
    # ========================================================================
    "other": [
        _create_service_template("Blow Dry", "other", 300, 30, "Professional blow dry for smooth, voluminous hair", "chair_womens"),
        _create_service_template("Ironing", "other", 400, 30, "Flat iron styling for sleek, straight hair", "chair_womens"),
        _create_service_template("Curling", "other", 500, 45, "Curling iron or wand for beautiful curls", "chair_womens"),
        _create_service_template("Updo", "other", 1000, 60, "Elegant updo for special occasions", "chair_womens"),
        _create_service_template("Braiding", "other", 600, 45, "Various braiding styles and patterns", "chair_womens"),
        _create_service_template("Party Styling", "other", 800, 60, "Glamorous styling for parties and events", "chair_womens"),
        _create_service_template("Groom Package", "other", 8000, 150, "Complete groom makeover including haircut, facial, and styling", "chair_mens"),
        _create_service_template("Groom Makeup", "other", 3000, 60, "Natural groom makeup for a polished look", "room_treatment"),
        _create_service_template("Groom Hair Styling", "other", 1500, 45, "Professional styling for the groom", "chair_mens"),
    ],
}


def get_all_services() -> List[Dict[str, Any]]:
    """Get all services as a flat list with category included."""
    all_services = []
    for category, services in SERVICE_TEMPLATES.items():
        for service in services:
            # Each service already has category, just add to list
            all_services.append(service)
    return all_services


def get_services_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all services for a specific category."""
    return SERVICE_TEMPLATES.get(category, [])


def get_service_count() -> Dict[str, int]:
    """Get count of services per category."""
    return {category: len(services) for category, services in SERVICE_TEMPLATES.items()}


def get_total_service_count() -> int:
    """Get total number of all services."""
    return sum(len(services) for services in SERVICE_TEMPLATES.values())


# Legacy category mapping for backward compatibility
LEGACY_CATEGORY_MAP = {
    "hair_cuts": "haircut",
    "hair_color": "hair_color",
    "hair_treatments": "hair_treatment",
    "facial_skin": "facial",
    "spa": "spa",
    "bridal": "bridal",
    "groom": "other",
    "styling": "other",
}


def map_legacy_category(legacy_category: str) -> str:
    """Map legacy category names to new enum values."""
    return LEGACY_CATEGORY_MAP.get(legacy_category, legacy_category)
