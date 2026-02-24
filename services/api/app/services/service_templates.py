"""Service templates for Salon Flow.

Provides predefined service templates for different salon types.
Based on Jawed Habib salon menu with realistic Indian pricing.
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal


def get_service_templates(
    template_type: str = "salon",
    categories: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Get service templates based on type and categories.
    
    Args:
        template_type: Type of salon (salon, spa, unisex)
        categories: Optional list of specific categories to include
        
    Returns:
        List of service template dictionaries
    """
    all_services = SALON_SERVICES.copy()
    
    if template_type == "spa":
        all_services.extend(SPA_SERVICES)
    elif template_type == "unisex":
        all_services.extend(UNISEX_SERVICES)
    
    if categories:
        all_services = [
            s for s in all_services
            if s.get("category") in categories
        ]
    
    return all_services


# ============================================================================
# HAIR CUTS - MEN
# ============================================================================

MENS_HAIR_CUTS = [
    {
        "name": "Men's Hair Cut",
        "description": "Professional hair cut with styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 250.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
        "is_popular": True,
    },
    {
        "name": "Men's Hair Cut + Wash",
        "description": "Hair cut with hair wash and blow dry",
        "category": "hair_cuts",
        "pricing": {"base_price": 350.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
        "is_popular": True,
    },
    {
        "name": "Men's Premium Hair Cut",
        "description": "Premium hair cut with senior stylist, consultation and styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 500.0, "senior_price": 500.0, "expert_price": 750.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
    },
    {
        "name": "Men's Beard Trim",
        "description": "Professional beard shaping and trim",
        "category": "hair_cuts",
        "pricing": {"base_price": 100.0},
        "duration": {"base_minutes": 15},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
    },
    {
        "name": "Men's Hair Cut + Beard",
        "description": "Complete grooming with hair cut and beard styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 350.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
        "is_popular": True,
    },
    {
        "name": "Men's Clean Shave",
        "description": "Traditional clean shave with hot towel",
        "category": "hair_cuts",
        "pricing": {"base_price": 150.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
    },
    {
        "name": "Men's Royal Shave",
        "description": "Luxury shave with facial massage and premium products",
        "category": "hair_cuts",
        "pricing": {"base_price": 300.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
    },
]


# ============================================================================
# HAIR CUTS - WOMEN
# ============================================================================

WOMENS_HAIR_CUTS = [
    {
        "name": "Women's Hair Cut",
        "description": "Professional hair cut with basic styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 350.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
        "is_popular": True,
    },
    {
        "name": "Women's Hair Cut + Wash",
        "description": "Hair cut with wash and blow dry",
        "category": "hair_cuts",
        "pricing": {"base_price": 500.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
        "is_popular": True,
    },
    {
        "name": "Women's Premium Hair Cut",
        "description": "Premium hair cut with senior stylist and advanced styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 750.0, "senior_price": 750.0, "expert_price": 1000.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
    },
    {
        "name": "Women's Layer Cut",
        "description": "Trendy layered hair cut with styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 600.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
    },
    {
        "name": "Women's Step Cut",
        "description": "Elegant step cut with volume styling",
        "category": "hair_cuts",
        "pricing": {"base_price": 550.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
    },
    {
        "name": "Women's Fringe/Bangs Cut",
        "description": "Stylish fringe or bangs cut",
        "category": "hair_cuts",
        "pricing": {"base_price": 200.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
    },
    {
        "name": "Women's Trim",
        "description": "Basic trim for maintaining style",
        "category": "hair_cuts",
        "pricing": {"base_price": 200.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
    },
]


# ============================================================================
# KIDS CUTS
# ============================================================================

KIDS_CUTS = [
    {
        "name": "Kids Boy Hair Cut",
        "description": "Hair cut for boys below 10 years",
        "category": "hair_cuts",
        "pricing": {"base_price": 150.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
    },
    {
        "name": "Kids Girl Hair Cut",
        "description": "Hair cut for girls below 10 years",
        "category": "hair_cuts",
        "pricing": {"base_price": 200.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "womens_chair"},
        "gender_preference": "female",
    },
]


# ============================================================================
# HAIR COLOR
# ============================================================================

HAIR_COLOR = [
    {
        "name": "Root Touch Up",
        "description": "Root coloring for grey coverage",
        "category": "hair_color",
        "pricing": {"base_price": 500.0, "is_variable_pricing": True, "min_price": 400.0, "max_price": 700.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "womens_chair"},
        "is_popular": True,
    },
    {
        "name": "Full Hair Color",
        "description": "Complete hair coloring with premium products",
        "category": "hair_color",
        "pricing": {"base_price": 1500.0, "is_variable_pricing": True, "min_price": 1200.0, "max_price": 2500.0},
        "duration": {"base_minutes": 120},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Global Hair Color",
        "description": "Full head color with premium international brand",
        "category": "hair_color",
        "pricing": {"base_price": 2500.0, "is_variable_pricing": True, "min_price": 2000.0, "max_price": 4000.0},
        "duration": {"base_minutes": 150},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Highlights - Partial",
        "description": "Partial highlights for natural look",
        "category": "hair_color",
        "pricing": {"base_price": 2000.0, "is_variable_pricing": True, "min_price": 1500.0, "max_price": 3000.0},
        "duration": {"base_minutes": 120},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Highlights - Full",
        "description": "Full head highlights with premium colors",
        "category": "hair_color",
        "pricing": {"base_price": 4000.0, "is_variable_pricing": True, "min_price": 3000.0, "max_price": 6000.0},
        "duration": {"base_minutes": 180},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Balayage",
        "description": "Hand-painted natural highlights technique",
        "category": "hair_color",
        "pricing": {"base_price": 5000.0, "is_variable_pricing": True, "min_price": 4000.0, "max_price": 8000.0},
        "duration": {"base_minutes": 240},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Ombre Hair Color",
        "description": "Gradient color effect from dark to light",
        "category": "hair_color",
        "pricing": {"base_price": 4500.0, "is_variable_pricing": True, "min_price": 3500.0, "max_price": 7000.0},
        "duration": {"base_minutes": 210},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Foil Highlights",
        "description": "Classic foil highlighting technique",
        "category": "hair_color",
        "pricing": {"base_price": 3000.0, "is_variable_pricing": True, "min_price": 2500.0, "max_price": 5000.0},
        "duration": {"base_minutes": 150},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Men's Hair Color",
        "description": "Natural looking hair color for men",
        "category": "hair_color",
        "pricing": {"base_price": 800.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "mens_chair"},
        "gender_preference": "male",
    },
    {
        "name": "Fashion Colors",
        "description": "Vibrant fashion colors (pink, blue, purple, etc.)",
        "category": "hair_color",
        "pricing": {"base_price": 3500.0, "is_variable_pricing": True, "min_price": 3000.0, "max_price": 6000.0},
        "duration": {"base_minutes": 180},
        "resource_requirement": {"resource_type": "service_room"},
    },
]


# ============================================================================
# HAIR TREATMENTS
# ============================================================================

HAIR_TREATMENTS = [
    {
        "name": "Keratin Treatment",
        "description": "Smoothing treatment for frizz-free hair",
        "category": "hair_treatments",
        "pricing": {"base_price": 5000.0, "is_variable_pricing": True, "min_price": 4000.0, "max_price": 8000.0},
        "duration": {"base_minutes": 180},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Hair Spa",
        "description": "Deep conditioning treatment with massage",
        "category": "hair_treatments",
        "pricing": {"base_price": 800.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "womens_chair"},
        "is_popular": True,
    },
    {
        "name": "Premium Hair Spa",
        "description": "Luxury hair spa with imported products",
        "category": "hair_treatments",
        "pricing": {"base_price": 1500.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Scalp Treatment",
        "description": "Treatment for dandruff and scalp issues",
        "category": "hair_treatments",
        "pricing": {"base_price": 1000.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Hair Botox",
        "description": "Deep repair treatment for damaged hair",
        "category": "hair_treatments",
        "pricing": {"base_price": 4000.0, "is_variable_pricing": True, "min_price": 3000.0, "max_price": 6000.0},
        "duration": {"base_minutes": 150},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Olaplex Treatment",
        "description": "Bond-building treatment for hair repair",
        "category": "hair_treatments",
        "pricing": {"base_price": 2500.0},
        "duration": {"base_minutes": 90},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Hair Rebonding",
        "description": "Permanent hair straightening",
        "category": "hair_treatments",
        "pricing": {"base_price": 6000.0, "is_variable_pricing": True, "min_price": 5000.0, "max_price": 10000.0},
        "duration": {"base_minutes": 240},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Anti-Hair Fall Treatment",
        "description": "Treatment to reduce hair fall",
        "category": "hair_treatments",
        "pricing": {"base_price": 1500.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
    },
]


# ============================================================================
# STYLING
# ============================================================================

STYLING = [
    {
        "name": "Blow Dry",
        "description": "Professional blow dry styling",
        "category": "styling",
        "pricing": {"base_price": 300.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "womens_chair"},
        "is_popular": True,
    },
    {
        "name": "Ironing/Straightening",
        "description": "Temporary hair straightening with iron",
        "category": "styling",
        "pricing": {"base_price": 400.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "womens_chair"},
    },
    {
        "name": "Curling",
        "description": "Professional curling with styling tools",
        "category": "styling",
        "pricing": {"base_price": 500.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "womens_chair"},
    },
    {
        "name": "Party Styling",
        "description": "Special occasion hair styling",
        "category": "styling",
        "pricing": {"base_price": 800.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "womens_chair"},
        "is_popular": True,
    },
    {
        "name": "Bridal Hair Styling",
        "description": "Complete bridal hair styling",
        "category": "styling",
        "pricing": {"base_price": 3000.0},
        "duration": {"base_minutes": 90},
        "resource_requirement": {"resource_type": "bridal_room"},
    },
    {
        "name": "Updo/Bun Styling",
        "description": "Elegant updo or bun for special occasions",
        "category": "styling",
        "pricing": {"base_price": 600.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "womens_chair"},
    },
]


# ============================================================================
# FACIAL & SKIN
# ============================================================================

FACIAL_SKIN = [
    {
        "name": "Basic Cleanup",
        "description": "Cleansing and toning for all skin types",
        "category": "facial_skin",
        "pricing": {"base_price": 400.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Diamond Facial",
        "description": "Luxury diamond facial for glowing skin",
        "category": "facial_skin",
        "pricing": {"base_price": 1500.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Gold Facial",
        "description": "Premium gold facial for radiant skin",
        "category": "facial_skin",
        "pricing": {"base_price": 2000.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Fruit Facial",
        "description": "Natural fruit-based facial for fresh skin",
        "category": "facial_skin",
        "pricing": {"base_price": 800.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Anti-Aging Facial",
        "description": "Treatment for mature skin with anti-aging products",
        "category": "facial_skin",
        "pricing": {"base_price": 2500.0},
        "duration": {"base_minutes": 75},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Acne Treatment Facial",
        "description": "Specialized treatment for acne-prone skin",
        "category": "facial_skin",
        "pricing": {"base_price": 1200.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Whitening Facial",
        "description": "Skin brightening and whitening treatment",
        "category": "facial_skin",
        "pricing": {"base_price": 1800.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Men's Facial",
        "description": "Facial designed specifically for men's skin",
        "category": "facial_skin",
        "pricing": {"base_price": 800.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
        "gender_preference": "male",
    },
    {
        "name": "Bleach - Face",
        "description": "Face bleaching for even skin tone",
        "category": "facial_skin",
        "pricing": {"base_price": 300.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "De-Tan Facial",
        "description": "Treatment to remove tan and brighten skin",
        "category": "facial_skin",
        "pricing": {"base_price": 1000.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
    },
]


# ============================================================================
# SPA SERVICES
# ============================================================================

SPA_SERVICES = [
    {
        "name": "Head Massage",
        "description": "Relaxing head massage with oil",
        "category": "spa",
        "pricing": {"base_price": 300.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "spa_room"},
        "is_popular": True,
    },
    {
        "name": "Full Body Massage",
        "description": "Relaxing full body massage",
        "category": "spa",
        "pricing": {"base_price": 1500.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "spa_room"},
        "is_popular": True,
    },
    {
        "name": "Aromatherapy Massage",
        "description": "Massage with essential oils",
        "category": "spa",
        "pricing": {"base_price": 2000.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "spa_room"},
    },
    {
        "name": "Back Massage",
        "description": "Focused back and shoulder massage",
        "category": "spa",
        "pricing": {"base_price": 600.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "spa_room"},
    },
    {
        "name": "Foot Reflexology",
        "description": "Therapeutic foot massage",
        "category": "spa",
        "pricing": {"base_price": 500.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "spa_room"},
    },
    {
        "name": "Manicure",
        "description": "Complete hand and nail care",
        "category": "spa",
        "pricing": {"base_price": 500.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Pedicure",
        "description": "Complete foot and nail care",
        "category": "spa",
        "pricing": {"base_price": 600.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Premium Manicure",
        "description": "Luxury manicure with spa treatment",
        "category": "spa",
        "pricing": {"base_price": 800.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Premium Pedicure",
        "description": "Luxury pedicure with spa treatment",
        "category": "spa",
        "pricing": {"base_price": 1000.0},
        "duration": {"base_minutes": 60},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Nail Art",
        "description": "Creative nail art design",
        "category": "spa",
        "pricing": {"base_price": 500.0, "is_variable_pricing": True, "min_price": 300.0, "max_price": 1500.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Waxing - Full Arms",
        "description": "Complete arm waxing",
        "category": "spa",
        "pricing": {"base_price": 400.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Waxing - Full Legs",
        "description": "Complete leg waxing",
        "category": "spa",
        "pricing": {"base_price": 600.0},
        "duration": {"base_minutes": 30},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Waxing - Full Body",
        "description": "Complete body waxing",
        "category": "spa",
        "pricing": {"base_price": 2000.0},
        "duration": {"base_minutes": 90},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Threading - Eyebrows",
        "description": "Eyebrow shaping with threading",
        "category": "spa",
        "pricing": {"base_price": 100.0},
        "duration": {"base_minutes": 10},
        "resource_requirement": {"resource_type": "any"},
        "is_popular": True,
    },
    {
        "name": "Threading - Upper Lip",
        "description": "Upper lip threading",
        "category": "spa",
        "pricing": {"base_price": 50.0},
        "duration": {"base_minutes": 5},
        "resource_requirement": {"resource_type": "any"},
    },
    {
        "name": "Threading - Full Face",
        "description": "Complete face threading",
        "category": "spa",
        "pricing": {"base_price": 300.0},
        "duration": {"base_minutes": 20},
        "resource_requirement": {"resource_type": "service_room"},
    },
]


# ============================================================================
# BRIDAL PACKAGES
# ============================================================================

BRIDAL_PACKAGES = [
    {
        "name": "Bridal Makeup - Basic",
        "description": "Basic bridal makeup with HD finish",
        "category": "bridal",
        "pricing": {"base_price": 8000.0},
        "duration": {"base_minutes": 120},
        "resource_requirement": {"resource_type": "bridal_room"},
    },
    {
        "name": "Bridal Makeup - Premium",
        "description": "Premium bridal makeup with airbrush",
        "category": "bridal",
        "pricing": {"base_price": 15000.0},
        "duration": {"base_minutes": 150},
        "resource_requirement": {"resource_type": "bridal_room"},
        "is_popular": True,
    },
    {
        "name": "Bridal Makeup - Luxury",
        "description": "Luxury bridal makeup with international products",
        "category": "bridal",
        "pricing": {"base_price": 25000.0},
        "duration": {"base_minutes": 180},
        "resource_requirement": {"resource_type": "bridal_room"},
    },
    {
        "name": "Bridal Package - Complete",
        "description": "Complete bridal package including makeup, hair, mehndi",
        "category": "bridal",
        "pricing": {"base_price": 35000.0, "is_variable_pricing": True, "min_price": 30000.0, "max_price": 50000.0},
        "duration": {"base_minutes": 300},
        "resource_requirement": {"resource_type": "bridal_room"},
    },
    {
        "name": "Pre-Bridal Package",
        "description": "Complete pre-bridal treatments (5 sessions)",
        "category": "bridal",
        "pricing": {"base_price": 20000.0},
        "duration": {"base_minutes": 120},
        "resource_requirement": {"resource_type": "service_room"},
    },
    {
        "name": "Engagement Makeup",
        "description": "Elegant makeup for engagement ceremony",
        "category": "bridal",
        "pricing": {"base_price": 6000.0},
        "duration": {"base_minutes": 90},
        "resource_requirement": {"resource_type": "bridal_room"},
    },
]


# ============================================================================
# GROOM PACKAGES
# ============================================================================

GROOM_PACKAGES = [
    {
        "name": "Groom Package - Basic",
        "description": "Basic grooming for wedding day",
        "category": "groom",
        "pricing": {"base_price": 3000.0},
        "duration": {"base_minutes": 90},
        "resource_requirement": {"resource_type": "mens_chair"},
    },
    {
        "name": "Groom Package - Premium",
        "description": "Premium grooming with facial and styling",
        "category": "groom",
        "pricing": {"base_price": 5000.0},
        "duration": {"base_minutes": 120},
        "resource_requirement": {"resource_type": "service_room"},
        "is_popular": True,
    },
    {
        "name": "Groom Package - Luxury",
        "description": "Complete luxury grooming package",
        "category": "groom",
        "pricing": {"base_price": 8000.0},
        "duration": {"base_minutes": 150},
        "resource_requirement": {"resource_type": "service_room"},
    },
]


# ============================================================================
# COMBINE ALL SERVICES
# ============================================================================

SALON_SERVICES = (
    MENS_HAIR_CUTS +
    WOMENS_HAIR_CUTS +
    KIDS_CUTS +
    HAIR_COLOR +
    HAIR_TREATMENTS +
    STYLING +
    FACIAL_SKIN +
    BRIDAL_PACKAGES +
    GROOM_PACKAGES
)

UNISEX_SERVICES = [
    {
        "name": "Unisex Hair Cut",
        "description": "Professional hair cut for any gender",
        "category": "hair_cuts",
        "pricing": {"base_price": 400.0},
        "duration": {"base_minutes": 45},
        "resource_requirement": {"resource_type": "any"},
    },
]


__all__ = ["get_service_templates", "SALON_SERVICES", "SPA_SERVICES"]
