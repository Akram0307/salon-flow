"""Salon Guardrails System

Ensures all AI agents ONLY respond to salon-related queries.
Provides multi-language rejection responses.
"""
import re
from typing import Tuple, Optional
import structlog

logger = structlog.get_logger()


# Multi-language rejection responses
REJECTION_RESPONSES = {
    "en": "I'm your salon assistant! I can only help with salon services, bookings, and beauty-related queries. How can I assist you with your salon needs today?",
    "hi": "मैं आपका सैलून असिस्टेंट हूं! मैं केवल सैलून सेवाओं, बुकिंग और ब्यूटी संबंधी queries में मदद कर सकता हूं। आज मैं आपकी सैलून जरूरतों में कैसे मदद कर सकता हूं?",
    "te": "నేను మీ సెలూన్ అసిస్టెంట్! నేను సెలూన్ సేవలు, బుకింగ్‌లు మరియు అందం సంబంధిత ప్రశ్నలలో మాత్రమే సహాయం చేయగలను. ఈరోజు మీ సెలూన్ అవసరాలలో నేను ఎలా సహాయం చేయగలను?"
}

# Redirect message with helpful suggestions
REDIRECT_MESSAGE = """
I can help you with:
- Booking appointments
- Service information and pricing
- Stylist recommendations
- Offers and packages
- Loyalty points and memberships

How can I help you today?"""

# Salon-only instruction for agent system prompts
SALON_ONLY_INSTRUCTION = """
IMPORTANT: You are a salon assistant ONLY. You must:
1. ONLY respond to queries related to salon services, beauty, hair, and wellness
2. Politely decline any questions about politics, sports, news, technology, or unrelated topics
3. Redirect users back to salon services with helpful suggestions
4. Never provide information outside your salon expertise

If a user asks an unrelated question, respond:
'I'm here to help with your salon needs! I can assist with:
- Booking appointments
- Service information and pricing
- Stylist recommendations
- Offers and packages
- Loyalty points and memberships

How can I help you today?'
"""


class SalonGuardrail:
    """Guardrail system to ensure salon-only responses"""
    
    # Topics that are ALLOWED - salon related
    ALLOWED_TOPICS = [
        # Core salon services
        "haircut", "hair", "styling", "color", "treatment", "spa",
        "facial", "makeup", "bridal", "groom", "beard", "shave",
        "manicure", "pedicure", "waxing", "threading", "keratin",
        "rebonding", "smoothening", "highlights", "lowlights",
        "blowout", "curls", "straightening", "perm", "balayage",
        
        # Booking & scheduling
        "booking", "appointment", "schedule", "availability",
        "slot", "time", "date", "reservation", "cancel", "reschedule",
        "waitlist", "queue", "reminder",
        
        # Business operations
        "service", "price", "offer", "discount", "package",
        "stylist", "staff", "salon", "beauty", "wellness",
        "loyalty", "membership", "points", "feedback",
        "location", "timing", "contact", "hours",
        
        # Inventory & products (salon-specific)
        "inventory", "product", "shampoo", "conditioner",
        "serum", "oil", "cream", "gel", "spray", "mask",
        "reorder", "expiry", "supply", "usage",
        
        # Customer management
        "customer", "client", "profile", "history", "preference",
        "visit", "retention", "churn", "winback", "reengage",
        "at-risk", "lapsed", "active", "segment",
        
        # Pricing & revenue
        "pricing", "revenue", "demand", "peak", "off-peak",
        "festival", "seasonal", "bundle", "combo", "upsell",
        "addon", "upgrade", "promotion", "campaign",
        
        # Staff management
        "shift", "schedule", "roster", "overtime", "time-off",
        "skill", "availability", "assignment",
        
        # Analytics (salon context)
        "analytics", "report", "dashboard", "metric", "kpi",
        "performance", "trend", "forecast", "analysis",
        
        # Common greetings and help
        "hello", "hi", "hey", "namaste", "assist",
        "thank", "please", "sorry", "welcome",
    ]
    
    # Topics that are BLOCKED - unrelated to salon
    BLOCKED_TOPICS = [
        # Politics & current events
        "politics", "election", "government", "minister", "party",
        "democracy", "vote", "campaign", "policy",
        
        # Sports
        "cricket", "football", "soccer", "tennis", "basketball",
        "sports", "match", "game", "score", "team", "player",
        "ipl", "world cup", "olympics",
        
        # Entertainment
        "movie", "film", "actor", "actress", "celebrity",
        "bollywood", "hollywood", "music", "song", "concert",
        "netflix", "amazon prime", "tv show",
        
        # News & weather
        "news", "weather", "climate", "temperature", "forecast",
        "earthquake", "flood", "storm",
        
        # Technology & programming
        "programming", "coding", "python", "javascript", "java",
        "software", "app development", "website", "database",
        "api", "server", "cloud", "docker", "kubernetes",
        "machine learning", "ai", "artificial intelligence",
        "code", "write code", "program", "developer",
        
        # Finance (non-salon)
        "stock market", "share", "investment", "trading",
        "bitcoin", "cryptocurrency", "crypto", "forex",
        "banking", "loan", "insurance", "tax",
        "stock", "price of bitcoin", "bitcoin price",
        
        # Other unrelated
        "cooking", "recipe", "food", "restaurant",
        "cook", "biryani", "curry", "dish",
        "travel", "vacation", "flight", "hotel",
        "religion", "god", "temple", "church", "mosque",
        "education", "school", "college", "university",
        "health", "medicine", "doctor", "hospital", "disease",
    ]
    
    def __init__(self):
        """Initialize guardrail with compiled patterns"""
        self._allowed_patterns = [
            re.compile(r'\b' + re.escape(topic) + r'\b', re.IGNORECASE)
            for topic in self.ALLOWED_TOPICS
        ]
        self._blocked_patterns = [
            re.compile(r'\b' + re.escape(topic) + r'\b', re.IGNORECASE)
            for topic in self.BLOCKED_TOPICS
        ]
        
        # Hindi character range for detection
        self._hindi_pattern = re.compile(r'[\u0900-\u097F]')
        # Telugu character range for detection
        self._telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate if query is salon-related.
        
        Args:
            query: User query to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not query or not query.strip():
            return False, "Empty query"
        
        query_lower = query.lower().strip()
        
        # Allow very short queries (greetings, yes/no)
        if len(query_lower.split()) <= 2:
            return True, "Short query allowed"
        
        # Count allowed and blocked topics
        allowed_count = self.count_allowed_topics(query)
        blocked_count = self.count_blocked_topics(query)
        
        # Decision logic
        if blocked_count > 0 and allowed_count == 0:
            reason = f"Blocked topics detected: {blocked_count}, no salon topics"
            logger.warning(
                "guardrail_blocked_query",
                query_preview=query[:100],
                reason=reason
            )
            return False, reason
        
        # If salon topics are present, check balance with blocked topics
        if allowed_count > 0:
            # Reject only if blocked topics exceed allowed topics
            if blocked_count > allowed_count:
                reason = f"Blocked topics ({blocked_count}) > allowed topics ({allowed_count})"
                logger.warning(
                    "guardrail_blocked_query",
                    query_preview=query[:100],
                    reason=reason
                )
                return False, reason
            return True, f"Salon-related query (topics: {allowed_count})"
        
        # Ambiguous - no clear topics
        logger.info(
            "guardrail_ambiguous",
            query_preview=query[:100],
            allowed_count=allowed_count,
            blocked_count=blocked_count
        )
        # Allow ambiguous queries by default (better UX)
        return True, "Ambiguous but allowed"
    
    def count_allowed_topics(self, query: str) -> int:
        """Count number of allowed topics in query"""
        count = 0
        for pattern in self._allowed_patterns:
            if pattern.search(query):
                count += 1
        return count
    
    def count_blocked_topics(self, query: str) -> int:
        """Count number of blocked topics in query"""
        count = 0
        for pattern in self._blocked_patterns:
            if pattern.search(query):
                count += 1
        return count
    
    def detect_language(self, text: str) -> str:
        """Detect language from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code: 'en', 'hi', or 'te'
        """
        if self._hindi_pattern.search(text):
            return "hi"
        if self._telugu_pattern.search(text):
            return "te"
        return "en"
    
    def get_rejection_response(
        self, 
        query: str, 
        language: Optional[str] = None
    ) -> str:
        """Get rejection response in appropriate language.
        
        Args:
            query: The blocked query
            language: Optional language code, auto-detected if None
            
        Returns:
            Rejection response string
        """
        if language is None:
            language = self.detect_language(query)
        
        base_response = REJECTION_RESPONSES.get(language, REJECTION_RESPONSES["en"])
        return base_response + REDIRECT_MESSAGE


# Singleton instance
_guardrail_instance: Optional[SalonGuardrail] = None


def get_guardrail() -> SalonGuardrail:
    """Get singleton guardrail instance"""
    global _guardrail_instance
    if _guardrail_instance is None:
        _guardrail_instance = SalonGuardrail()
    return _guardrail_instance
