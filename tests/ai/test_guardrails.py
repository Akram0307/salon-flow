"""Comprehensive tests for Salon Guardrails System

Tests the salon-only guardrail functionality including:
- Topic validation
- Multi-language rejection responses
- Integration with agents
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.guardrails import (
    SalonGuardrail,
    get_guardrail,
    REJECTION_RESPONSES,
    REDIRECT_MESSAGE,
    SALON_ONLY_INSTRUCTION,
)



@pytest.fixture
def guardrail():
    """Module-level fixture for guardrail tests"""
    return SalonGuardrail()


class TestSalonGuardrail:
    """Test suite for SalonGuardrail class"""
    
    @pytest.fixture
    def guardrail(self):
        """Create a fresh guardrail instance for each test"""
        return SalonGuardrail()
    
    # ============== Topic Detection Tests ==============
    
    def test_allowed_topics_exist(self, guardrail):
        """Test that allowed topics are defined"""
        assert len(guardrail.ALLOWED_TOPICS) > 0
        assert "haircut" in guardrail.ALLOWED_TOPICS
        assert "booking" in guardrail.ALLOWED_TOPICS
        assert "salon" in guardrail.ALLOWED_TOPICS
    
    def test_blocked_topics_exist(self, guardrail):
        """Test that blocked topics are defined"""
        assert len(guardrail.BLOCKED_TOPICS) > 0
        assert "politics" in guardrail.BLOCKED_TOPICS
        assert "sports" in guardrail.BLOCKED_TOPICS
        assert "programming" in guardrail.BLOCKED_TOPICS
    
    # ============== Validation Tests ==============
    
    @pytest.mark.parametrize("query,expected_valid", [
        # Salon-related queries - should be valid
        ("I want to book a haircut", True),
        ("What are your prices for hair coloring?", True),
        ("Can I get a facial tomorrow?", True),
        ("I need a bridal makeup package", True),
        ("What services do you offer?", True),
        ("I'd like to schedule an appointment", True),
        ("Do you have any discounts on hair treatments?", True),
        ("Which stylist is best for keratin treatment?", True),
        ("I want to check my loyalty points", True),
        ("What time does the salon open?", True),
        ("Can I join the waitlist for today?", True),
        ("I need a beard trim", True),
        ("What's the price for spa services?", True),
        ("Do you offer bridal packages?", True),
        ("I want to reschedule my appointment", True),
    ])
    def test_validate_salon_queries(self, guardrail, query, expected_valid):
        """Test that salon-related queries are accepted"""
        is_valid, reason = guardrail.validate_query(query)
        assert is_valid == expected_valid, f"Query '{query}' should be valid: {reason}"
    
    @pytest.mark.parametrize("query,expected_valid", [
        # Blocked topics - should be rejected
        ("What do you think about the election?", False),
        ("Who won the cricket match yesterday?", False),
        ("What's the weather like today?", False),
        ("Can you help me with Python programming?", False),
        ("What's the latest news?", False),
        ("Tell me about Bollywood movies", False),
        ("What's the stock market doing?", False),
        ("How do I cook biryani?", False),
        ("What's the score of the IPL match?", False),
        ("Who is the prime minister?", False),
        ("What religion do you follow?", False),
        ("Can you write code for me?", False),
        ("What's the bitcoin price?", False),
    ])
    def test_validate_blocked_queries(self, guardrail, query, expected_valid):
        """Test that blocked topic queries are rejected"""
        is_valid, reason = guardrail.validate_query(query)
        assert is_valid == expected_valid, f"Query '{query}' should be rejected"
    
    @pytest.mark.parametrize("query", [
        "hi",
        "hello",
        "hey there",
        "good morning",
        "namaste",
        "नमस्ते",
        "నమస్కారం",
    ])
    def test_validate_greetings(self, guardrail, query):
        """Test that greetings are allowed"""
        is_valid, reason = guardrail.validate_query(query)
        assert is_valid is True, f"Greeting '{query}' should be allowed"
    
    @pytest.mark.parametrize("query", [
        "help",
        "what can you do",
        "how can you help me",
        "tell me about yourself",
    ])
    def test_validate_help_requests(self, guardrail, query):
        """Test that help requests are allowed"""
        is_valid, reason = guardrail.validate_query(query)
        assert is_valid is True, f"Help request '{query}' should be allowed"
    
    # ============== Language Detection Tests ==============
    
    @pytest.mark.parametrize("text,expected_lang", [
        ("I want a haircut", "en"),
        ("मुझे हेयरकट चाहिए", "hi"),
        ("నాకు హెయిర్‌కట్ కావాలి", "te"),
        ("Hello, how are you?", "en"),
        ("नमस्ते, आप कैसे हैं?", "hi"),
        ("హలో, మీరు ఎలా ఉన్నారు?", "te"),
    ])
    def test_detect_language(self, guardrail, text, expected_lang):
        """Test language detection from text"""
        detected = guardrail.detect_language(text)
        assert detected == expected_lang
    
    # ============== Rejection Response Tests ==============
    
    def test_get_rejection_response_english(self, guardrail):
        """Test English rejection response"""
        response = guardrail.get_rejection_response("What's the weather?", language="en")
        assert "salon" in response.lower()
        assert REJECTION_RESPONSES["en"] in response
        assert REDIRECT_MESSAGE in response
    
    def test_get_rejection_response_hindi(self, guardrail):
        """Test Hindi rejection response"""
        response = guardrail.get_rejection_response("मौसम कैसा है?", language="hi")
        assert "सैलून" in response or "salon" in response.lower()
        assert REJECTION_RESPONSES["hi"] in response
    
    def test_get_rejection_response_telugu(self, guardrail):
        """Test Telugu rejection response"""
        response = guardrail.get_rejection_response("వాతావరణం ఎలా ఉంది?", language="te")
        assert "సెలూన్" in response or "salon" in response.lower()
        assert REJECTION_RESPONSES["te"] in response
    
    def test_get_rejection_response_auto_detect(self, guardrail):
        """Test auto language detection for rejection"""
        # Hindi query
        response_hi = guardrail.get_rejection_response("आज क्रिकेट मैच कौन जीता?")
        assert "सैलून" in response_hi or "salon" in response_hi.lower()
        
        # Telugu query
        response_te = guardrail.get_rejection_response("ఈరోజు క్రికెట్ మ్యాచ్ ఎవరు గెలిచారు?")
        assert "సెలూన్" in response_te or "salon" in response_te.lower()
    
    # ============== Edge Case Tests ==============
    
    def test_empty_query(self, guardrail):
        """Test empty query handling"""
        is_valid, reason = guardrail.validate_query("")
        assert is_valid is False
        assert "empty" in reason.lower()
    
    def test_whitespace_query(self, guardrail):
        """Test whitespace-only query"""
        is_valid, reason = guardrail.validate_query("   ")
        assert is_valid is False
    
    def test_short_ambiguous_query(self, guardrail):
        """Test short ambiguous queries are allowed"""
        is_valid, _ = guardrail.validate_query("yes")
        assert is_valid is True  # Short queries allowed
    
    def test_mixed_topics_query(self, guardrail):
        """Test query with both salon and blocked topics"""
        # Should be allowed because it has salon topics
        is_valid, reason = guardrail.validate_query(
            "I want a haircut and also want to know about cricket"
        )
        # Has salon topic, so should be allowed
        assert is_valid is True
    
    def test_count_allowed_topics(self, guardrail):
        """Test counting allowed topics in query"""
        count = guardrail.count_allowed_topics("I want a haircut and hair coloring")
        assert count >= 2  # haircut and hair/color
    
    def test_count_blocked_topics(self, guardrail):
        """Test counting blocked topics in query"""
        count = guardrail.count_blocked_topics("What about cricket and politics?")
        assert count >= 2  # cricket and politics
    
    # ============== Singleton Tests ==============
    
    def test_get_guardrail_singleton(self):
        """Test that get_guardrail returns singleton"""
        g1 = get_guardrail()
        g2 = get_guardrail()
        assert g1 is g2


class TestGuardrailIntegration:
    """Test guardrail integration with agents"""
    
    @pytest.mark.asyncio
    async def test_agent_blocks_non_salon_query(self):
        """Test that agent blocks non-salon queries"""
        from app.services.agents import BookingAgent
        
        agent = BookingAgent()
        response = await agent.generate(
            prompt="What's the weather like today?",
            skip_guardrail=False
        )
        
        assert response.success is False
        assert response.blocked is True
        assert "salon" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_agent_accepts_salon_query(self):
        """Test that agent accepts salon queries"""
        from app.services.agents import BookingAgent
        
        # Mock the OpenRouter client
        with patch.object(BookingAgent, '_get_client') as mock_client:
            mock_client.return_value.chat = AsyncMock(
                return_value=MagicMock(content="Sure, I can help you book a haircut!")
            )
            
            agent = BookingAgent()
            response = await agent.generate(
                prompt="I want to book a haircut",
                skip_guardrail=False,
                use_cache=False
            )
            
            # Should not be blocked
            assert response.blocked is False
    
    @pytest.mark.asyncio
    async def test_all_agents_have_guardrails(self):
        """Test that all agents have guardrail protection"""
        from app.services.agents import AGENTS, get_agent
        
        for agent_name, agent_class in AGENTS.items():
            agent = get_agent(agent_name)
            assert hasattr(agent, '_check_guardrail')
            assert hasattr(agent, '_get_guardrail')


class TestGuardrailConstants:
    """Test guardrail constants and configurations"""
    
    def test_rejection_responses_exist(self):
        """Test that rejection responses exist for all languages"""
        assert "en" in REJECTION_RESPONSES
        assert "hi" in REJECTION_RESPONSES
        assert "te" in REJECTION_RESPONSES
    
    def test_redirect_message_exists(self):
        """Test that redirect message exists"""
        assert REDIRECT_MESSAGE is not None
        assert "booking" in REDIRECT_MESSAGE.lower()
        assert "service" in REDIRECT_MESSAGE.lower()
    
    def test_salon_only_instruction_exists(self):
        """Test that salon-only instruction exists"""
        assert SALON_ONLY_INSTRUCTION is not None
        assert "salon" in SALON_ONLY_INSTRUCTION.lower()
        assert "ONLY" in SALON_ONLY_INSTRUCTION


class TestGuardrailPerformance:
    """Performance tests for guardrail"""
    
    def test_validation_speed(self, guardrail):
        """Test that validation is fast"""
        import time
        
        queries = [
            "I want to book a haircut",
            "What's the cricket score?",
            "Can I get a facial?",
            "Tell me about politics",
        ] * 100  # 400 queries
        
        start = time.time()
        for query in queries:
            guardrail.validate_query(query)
        elapsed = time.time() - start
        
        # Should process 400 queries in under 1 second
        assert elapsed < 1.0, f"Validation too slow: {elapsed}s for 400 queries"
    
    def test_pattern_compilation(self, guardrail):
        """Test that patterns are compiled on init"""
        assert guardrail._allowed_patterns is not None
        assert guardrail._blocked_patterns is not None
        assert len(guardrail._allowed_patterns) == len(guardrail.ALLOWED_TOPICS)
        assert len(guardrail._blocked_patterns) == len(guardrail.BLOCKED_TOPICS)


# Run tests with: pytest tests/ai/test_guardrails.py -v
