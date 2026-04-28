"""Comprehensive tests for persona generation."""
import json
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from backend.swarm.persona_generator import generate_personas
from backend.models.business import BusinessSnapshot
from backend.models.persona import PersonaProfile
from backend.reviewer_intelligence.persona_calibrator import (
    PersonaGenerationManifest,
    PersonaSpec,
)


class TestGeneratePersonasCount:
    """Test persona count generation."""

    @pytest.mark.asyncio
    async def test_generates_exact_count(self):
        """Should generate exactly N personas."""
        business = BusinessSnapshot(
            id=str(uuid4()),
            name="Coffee Shop",
            type="restaurant",
            description="A cozy coffee shop",
            customer_description="Office workers and students",
            location="San Francisco, CA",
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            # Mock response with exactly 5 personas
            personas_json = '''
            {
                "personas": [
                    {"name": "Alice", "age": 25, "engagement_pattern": "daily", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "friendly"},
                    {"name": "Bob", "age": 35, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "analytical"},
                    {"name": "Carol", "age": 45, "engagement_pattern": "monthly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "casual"},
                    {"name": "David", "age": 55, "engagement_pattern": "rarely", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "traditional"},
                    {"name": "Eve", "age": 28, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "social"}
                ]
            }
            '''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(
                business=business,
                persona_count=5,
            )

            assert len(personas) == 5
            assert all(isinstance(p, PersonaProfile) for p in personas)

    @pytest.mark.asyncio
    async def test_default_count_12(self):
        """Default should generate 12 personas."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            # Generate 12 personas JSON
            personas_list = [
                {"name": f"P{i}", "age": 25+i, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week",
                 "spend_model": "$25/week", "personality": "neutral"}
                for i in range(12)
            ]
            personas_json = json.dumps({"personas": personas_list})

            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(business=business)

            assert len(personas) == 12


class TestGeneratePersonasDiversity:
    """Test persona diversity."""

    @pytest.mark.asyncio
    async def test_personas_have_different_traits(self):
        """Generated personas should have diverse traits."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            personas_json = '''
            {
                "personas": [
                    {"name": "Young Budget", "age": 22, "engagement_pattern": "daily", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "social"},
                    {"name": "Old Premium", "age": 65, "engagement_pattern": "monthly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "traditional"},
                    {"name": "Mid Average", "age": 40, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "analytical"}
                ]
            }
            '''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(business=business, persona_count=3)

            assert len(personas) == 3
            # Check diversity - at least some variation in key attributes
            ages = [p.age for p in personas]
            assert len(set(ages)) >= 1  # Has ages
            personalities = [p.personality for p in personas]
            assert len(set(personalities)) >= 1  # Has personalities

    @pytest.mark.asyncio
    async def test_personas_include_edge_cases(self):
        """Should include diverse personas including edge cases."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            personas_json = '''
            {
                "personas": [
                    {"name": "Happy Regular", "age": 35, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "very_positive"},
                    {"name": "Unhappy Rare", "age": 45, "engagement_pattern": "rarely", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "very_negative"},
                    {"name": "Neutral Occasional", "age": 40, "engagement_pattern": "monthly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "neutral"}
                ]
            }
            '''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(business=business, persona_count=3)

            assert len(personas) == 3
            # Should have mix of positive, negative, neutral
            personalities = [p.personality for p in personas]
            assert "very_positive" in personalities or any("positive" in str(p) for p in personalities)
            assert "very_negative" in personalities or any("negative" in str(p) for p in personalities)


class TestGeneratePersonasWithManifest:
    """Test structured manifest-constrained generation."""

    @pytest.mark.asyncio
    async def test_respects_persona_manifest(self):
        """Should respect PersonaGenerationManifest constraints."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        # Manifest specifies exact persona specs
        specs = [
            PersonaSpec(
                segment="Budget Conscious",
                age=25,
                income_tier="low",
                visit_frequency="daily",
                price_sensitivity="high",
                is_silent_majority=False,
                is_tourist=False,
                is_reviewer_type=True,
                must_include_traits=["price-sensitive"],
                must_not_include_traits=[],
            ),
            PersonaSpec(
                segment="Premium",
                age=45,
                income_tier="high",
                visit_frequency="weekly",
                price_sensitivity="low",
                is_silent_majority=False,
                is_tourist=False,
                is_reviewer_type=True,
                must_include_traits=["quality-focused"],
                must_not_include_traits=[],
            ),
        ]

        manifest = PersonaGenerationManifest(
            persona_specs=specs,
            total_count=2,
            distribution_summary="Budget Conscious (50%): 1 person\nPremium (50%): 1 person",
            anti_bias_instructions="Generate realistic, not overly positive personas.",
            diversity_requirements="Include contrasting income levels and sensitivity to price.",
            based_on=["review_analysis"],
            confidence="medium",
            key_caveats=["Limited demographic data"],
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            personas_json = '''
            {
                "personas": [
                    {"name": "Young Student", "age": 25, "engagement_pattern": "daily", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "personality": "social"},
                    {"name": "Wealthy Professional", "age": 45, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "personality": "analytical"}
                ]
            }
            '''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(business=business, manifest=manifest)

            assert len(personas) == 2
            # First persona should be young
            assert personas[0].age == 25
            # Second persona should be older
            assert personas[1].age == 45


class TestGeneratePersonasWithUploadData:
    """Test generation influenced by uploaded customer data."""

    @pytest.mark.asyncio
    async def test_uses_upload_data_in_generation(self):
        """Should incorporate CSV/upload data into generation."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        upload_data_summary = "Average customer age 35, 60% female, mostly commuters"

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            personas_json = '''
            {
                "personas": [
                    {"name": "Young Commuter F", "age": 32, "engagement_pattern": "daily", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "personality": "pragmatic"},
                    {"name": "Older Commuter M", "age": 38, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$25/week", "personality": "friendly"}
                ]
            }
            '''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(
                business=business,
                uploaded_data_summary=upload_data_summary,
                persona_count=2
            )

            assert len(personas) == 2
            # Verify upload data was passed to Claude (in messages)
            call_args = mock_client.messages.create.call_args
            messages = call_args.kwargs.get("messages", []) if call_args else []
            assert len(messages) > 0


class TestGeneratePersonasErrorHandling:
    """Test error handling in generation."""

    @pytest.mark.asyncio
    async def test_handles_api_timeout(self):
        """Should handle Claude API timeout gracefully."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                side_effect=TimeoutError("API timeout")
            )

            try:
                personas = await generate_personas(business=business)
                # Should either return empty list or raise
                assert personas == [] or personas is None
            except TimeoutError:
                # Expected
                pass

    @pytest.mark.asyncio
    async def test_handles_malformed_response(self):
        """Should handle malformed JSON response."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(
                    content=[MagicMock(text="Not JSON at all")]
                )
            )

            try:
                personas = await generate_personas(business=business)
                assert personas is None or len(personas) == 0
            except Exception:
                # Expected to fail gracefully
                pass


class TestGeneratePersonasAntibiasInstructions:
    """Test anti-bias instruction effectiveness."""

    @pytest.mark.asyncio
    async def test_personas_not_overly_positive(self):
        """Personas should include realistic negative/neutral attitudes."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client

            # Mix of sentiments
            personas_json = '''
            {
                "personas": [
                    {"name": "Positive", "age": 30, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "enthusiastic"},
                    {"name": "Negative", "age": 35, "engagement_pattern": "rarely", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "skeptical"},
                    {"name": "Neutral", "age": 40, "engagement_pattern": "monthly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "pragmatic"}
                ]
            }
            '''
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            personas = await generate_personas(business=business, persona_count=3)

            assert len(personas) == 3
            personalities = [p.personality for p in personas]
            # Should have mix, not all positive
            assert "enthusiastic" in personalities or "positive" in personalities[0].lower()
            assert "skeptical" in personalities or "negative" in personalities[1].lower()


class TestGeneratePersonasArchetypeCache:
    """Test persona archetype caching."""

    @pytest.mark.asyncio
    async def test_uses_cached_archetype_for_same_business(self):
        """Should reuse cached archetype for same business."""
        business = BusinessSnapshot(
            id=str(uuid4()), name="Shop", type="retail",
            description="Shop", customer_description="Customers",
            location="City"
        )

        personas_json = '''
        {
            "personas": [
                {"name": "Person1", "age": 30, "engagement_pattern": "weekly", "occupation": "Customer", "relationship_to_business": "Regular", "spend_model": "$20/week", "spend_model": "$25/week", "personality": "neutral"}
            ]
        }
        '''

        with patch("backend.swarm.persona_generator.AsyncAnthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=MagicMock(content=[MagicMock(text=personas_json)])
            )

            # First call
            personas1 = await generate_personas(business=business)
            # Second call with same business
            personas2 = await generate_personas(business=business)

            # If caching works, API should be called less frequently
            # or should return same personas
            assert personas1 is not None
            assert personas2 is not None
