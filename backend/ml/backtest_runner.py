"""
Backtest Runner

Takes published A/B test cases, fills out Murmur surveys for each,
runs real simulations through the Claude API, and scores our
predictions against what actually happened.

This produces REAL training data for the ML models, not synthetic.

Usage:
    python -m backend.ml.backtest_runner

    # Or run a single test:
    python -m backend.ml.backtest_runner --test 1
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

from backend.models.business import BusinessSnapshot
from backend.swarm import generate_personas, run_simulation, aggregate_responses
from backend.swarm.caveats import generate_caveats
from backend.impact import estimate_impact
from backend.survey.feature_extractor import FeatureExtractor
from backend.ml.backtest_cases import EXTRA_BACKTEST_CASES

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "backtest_results"
RESULTS_DIR.mkdir(exist_ok=True)


# ============================================================
# BACKTEST CASES -- each is a real published A/B test
# ============================================================

BACKTEST_CASES = [
    {
        "id": 1,
        "name": "Booking.com -- Urgency Messaging",
        "source": "Booking.com engineering blog / CXL Institute",
        "real_winner": "with_urgency",
        "real_outcome": "Urgency messaging increased conversions significantly",
        "holdout": False,
        "survey": {
            "name": "City View Hotel",
            "type": "hotel",
            "description": "Small boutique hotel in Amsterdam city centre, 25 rooms across 4 floors. Renovated canal house with modern interiors. Mostly business travellers midweek and weekend tourists. Listed on Booking.com, Expedia, and direct website.",
            "customer_description": "Mix of business travellers (Mon-Thu) and leisure tourists (Fri-Sun). Most book online, compare 3-4 hotels before deciding. Price-aware but willing to pay more for location. Many are repeat visitors to Amsterdam but first-time guests at the hotel.",
            "location": "Amsterdam, Netherlands",
            "location_country": "NL",
            "location_city": "Amsterdam",
            "is_online_only": False,
            "years_open": "3-10",
            "business_role": ["convenience", "destination"],
            "business_not_role": ["treat", "daily_need"],
            "visit_frequency": "occasional",
            "busy_days": ["friday", "saturday"],
            "busy_times": ["evening"],
            "customer_value_drivers": ["convenience", "value"],
            "customer_social_context": ["solo", "couple"],
            "regular_proportion": "very_few",
            "customer_age_distribution": {"18-24": 5, "25-34": 30, "35-44": 30, "45-54": 20, "55-64": 10, "65+": 5},
            "customer_income_bracket": "middle_upper",
            "average_transaction_value": 145.0,
            "customer_gender_split": "balanced",
            "local_vs_visitor_ratio": {"loyal_regulars": 5, "casual_regulars": 10, "occasional_visitors": 25, "first_timers": 40, "tourists": 20},
            "digital_savviness": "high",
            "price_range": "mid_high",
            "customer_discovery": ["booking_platforms", "google_search", "word_of_mouth"],
            "nearby_anchors": ["Centraal Station", "Dam Square", "Anne Frank House"],
            "competitor_advantage": ["lower prices", "bigger rooms", "loyalty programs"],
            "location_advantage": "Canal-side location 5 minutes from Centraal Station",
            "prior_changes": [
                {"change": "Added breakfast package option at booking", "year": 2022, "outcome": "positive", "metrics": "12% of guests added breakfast, average order value up 18 EUR"},
                {"change": "Raised weekend rates by 15%", "year": 2023, "outcome": "mixed", "metrics": "Revenue per room up 8% but occupancy dropped 5% on peak weekends"},
            ],
            "area_demographics": ["tourist", "business"],
            "competitor_count": "six_plus",
            "area_feel": "transactional",
        },
        "question": "Should we show customers a message saying 'Only a few rooms left!' when availability is low?",
        "variant_a": "Show urgency message when few rooms left",
        "variant_b": "No urgency messaging, just show availability normally",
        "expected_winner": "A",
    },
    {
        "id": 2,
        "name": "Netflix -- Artwork Personalization",
        "source": "Netflix Tech Blog 2017",
        "real_winner": "personalized",
        "real_outcome": "Personalized artwork significantly increased engagement",
        "holdout": False,
        "survey": {
            "name": "CineStream",
            "type": "saas",
            "description": "Small streaming recommendation service for film enthusiasts. Curated collections by genre, mood, and director. Monthly subscription at 9.99/mo with a library of 2,000 indie and classic films. Web and mobile apps.",
            "customer_description": "Film buffs aged 25-55 who value curation over mainstream. They come for recommendations they cannot find on Netflix or Amazon. Many are cinephiles who watch 3-5 films per week and discuss them in online forums.",
            "location": "London, UK",
            "location_country": "GB",
            "location_city": "London",
            "is_online_only": True,
            "years_open": "1-3",
            "business_role": ["destination", "treat"],
            "business_not_role": ["daily_need", "convenience"],
            "visit_frequency": "subscription",
            "busy_days": ["friday", "saturday", "sunday"],
            "busy_times": ["evening", "night"],
            "customer_value_drivers": ["specific_product", "quality"],
            "customer_social_context": ["solo", "couple"],
            "regular_proportion": "majority",
            "customer_age_distribution": {"18-24": 10, "25-34": 30, "35-44": 25, "45-54": 20, "55-64": 10, "65+": 5},
            "customer_income_bracket": "middle",
            "average_transaction_value": 9.99,
            "customer_gender_split": "slightly_male",
            "local_vs_visitor_ratio": {"loyal_regulars": 40, "casual_regulars": 30, "occasional_visitors": 20, "first_timers": 10, "tourists": 0},
            "digital_savviness": "very_high",
            "price_range": "low",
            "customer_discovery": ["social_media", "film_forums", "word_of_mouth", "google_search"],
            "nearby_anchors": ["Letterboxd community", "Reddit r/TrueFilm", "film festival audiences"],
            "competitor_advantage": ["larger catalogue", "original content", "lower price", "better apps"],
            "location_advantage": "Strong niche positioning -- known as the place for curated indie film",
            "prior_changes": [
                {"change": "Added director spotlight collections", "year": 2023, "outcome": "positive", "metrics": "Engagement on spotlight pages 2x average, 8% lift in weekly active users"},
                {"change": "Tested annual pricing at 89.99/yr", "year": 2024, "outcome": "positive", "metrics": "22% of subscribers switched to annual, reducing churn by 15%"},
            ],
            "area_demographics": ["residential", "urban_professional"],
            "competitor_count": "three_five",
            "area_feel": "destination",
        },
        "question": "Should we customise which cover image we show for each film based on what we know about the customer's taste?",
        "variant_a": None,
        "variant_b": None,
        "expected_winner": "positive",
    },
    {
        "id": 3,
        "name": "HubSpot -- Remove Landing Page Navigation",
        "source": "HubSpot Marketing Blog",
        "real_winner": "remove_nav",
        "real_outcome": "Removing navigation increased conversions by up to 28%",
        "holdout": False,
        "survey": {
            "name": "Green Consulting",
            "type": "accountant",
            "description": "Small sustainability consulting firm offering free initial consultations. Website drives most leads. Team of 4 consultants specialising in carbon reporting and ESG compliance for SMEs. Average engagement worth 8,000 EUR.",
            "customer_description": "Small business owners and operations managers looking for help with sustainability reporting and ESG compliance. Usually comparison shopping between 2-3 consultants. Motivated by upcoming EU regulations. Not very technical but need to comply.",
            "location": "Dublin, Ireland",
            "location_country": "IE",
            "location_city": "Dublin",
            "is_online_only": False,
            "years_open": "1-3",
            "business_role": ["destination"],
            "business_not_role": ["treat", "convenience"],
            "visit_frequency": "project_based",
            "busy_days": ["monday", "tuesday", "wednesday", "thursday"],
            "busy_times": ["morning", "afternoon"],
            "customer_value_drivers": ["quality", "personal_touch"],
            "customer_social_context": ["business_meeting"],
            "regular_proportion": "handful",
            "customer_age_distribution": {"18-24": 2, "25-34": 15, "35-44": 35, "45-54": 30, "55-64": 15, "65+": 3},
            "customer_income_bracket": "upper",
            "average_transaction_value": 8000.0,
            "customer_gender_split": "balanced",
            "local_vs_visitor_ratio": {"loyal_regulars": 15, "casual_regulars": 20, "occasional_visitors": 30, "first_timers": 35, "tourists": 0},
            "digital_savviness": "medium",
            "price_range": "high",
            "customer_discovery": ["google_search", "linkedin", "referrals", "industry_events"],
            "nearby_anchors": ["IFSC financial district", "Enterprise Ireland", "Local Chamber of Commerce"],
            "competitor_advantage": ["bigger team", "more case studies", "international presence"],
            "location_advantage": "Dublin-based, close to IFSC where many client HQs are located",
            "prior_changes": [
                {"change": "Added ESG compliance calculator to website", "year": 2023, "outcome": "positive", "metrics": "Website leads up 35%, calculator used by 60% of visitors before booking"},
                {"change": "Raised consultation fee from free to 150 EUR", "year": 2024, "outcome": "negative", "metrics": "Lead volume dropped 45%, had to revert to free within 2 months"},
            ],
            "area_demographics": ["business"],
            "competitor_count": "one_two",
            "area_feel": "destination",
        },
        "question": "On our 'Book a Free Consultation' page, should we remove all other navigation links so customers can only book or leave?",
        "variant_a": "Remove all navigation, only show booking form",
        "variant_b": "Keep full site navigation on the booking page",
        "expected_winner": "A",
    },
    {
        "id": 4,
        "name": "Etsy -- Free Shipping Threshold",
        "source": "Etsy Seller Handbook / earnings calls 2019",
        "real_winner": "free_shipping",
        "real_outcome": "Free shipping items had significantly higher conversion rates",
        "holdout": False,
        "survey": {
            "name": "Hannah's Handmade",
            "type": "ecommerce",
            "description": "Small online craft store selling handmade jewellery and home decor. Average order value around $45. Run by a single artisan with occasional help. Listed on Etsy and own Shopify store. Ships within the US.",
            "customer_description": "Women 25-45 who value handmade and unique items. Very price-aware on shipping -- often compare total cost including delivery. Many browse on mobile during lunch breaks. Gift buyers peak around holidays. Repeat purchase rate around 20%.",
            "location": "Portland, USA",
            "location_country": "US",
            "location_city": "Portland",
            "is_online_only": True,
            "years_open": "1-3",
            "business_role": ["treat", "destination"],
            "business_not_role": ["daily_need", "convenience"],
            "visit_frequency": "occasional",
            "busy_days": ["saturday", "sunday"],
            "busy_times": ["afternoon", "evening"],
            "customer_value_drivers": ["specific_product", "quality"],
            "customer_social_context": ["solo", "gift_buying"],
            "regular_proportion": "handful",
            "customer_age_distribution": {"18-24": 10, "25-34": 35, "35-44": 30, "45-54": 15, "55-64": 8, "65+": 2},
            "customer_income_bracket": "middle",
            "average_transaction_value": 45.0,
            "customer_gender_split": "mostly_female",
            "local_vs_visitor_ratio": {"loyal_regulars": 10, "casual_regulars": 15, "occasional_visitors": 30, "first_timers": 40, "tourists": 5},
            "digital_savviness": "high",
            "price_range": "mid",
            "customer_discovery": ["etsy_search", "instagram", "pinterest", "google_search"],
            "nearby_anchors": ["Etsy marketplace", "Instagram craft community", "Pinterest boards"],
            "competitor_advantage": ["lower prices", "faster shipping", "wider selection", "free shipping"],
            "location_advantage": "Portland craft scene gives authenticity and 'maker' credibility",
            "prior_changes": [
                {"change": "Added gift wrapping option for $3", "year": 2023, "outcome": "positive", "metrics": "15% of orders added gift wrap, especially around holidays"},
                {"change": "Ran 20% off sale for Black Friday", "year": 2023, "outcome": "mixed", "metrics": "3x order volume but margins squeezed, many first-time buyers did not return"},
            ],
            "area_demographics": ["residential"],
            "competitor_count": "six_plus",
            "area_feel": "destination",
        },
        "question": "Should we offer free shipping on orders over $35, or keep our current flat $5 shipping rate?",
        "variant_a": "Free shipping on orders over $35",
        "variant_b": "Keep flat $5 shipping on all orders",
        "expected_winner": "A",
    },
    {
        "id": 5,
        "name": "Obama Campaign -- Button Text",
        "source": "Optimizely case study / Dan Siroker",
        "real_winner": "learn_more",
        "real_outcome": "'Learn More' outperformed 'Sign Up' by 18.6%",
        "holdout": False,
        "survey": {
            "name": "The Weekly Brew",
            "type": "cafe",
            "description": "Neighbourhood coffee shop in East Austin with a weekly newsletter about coffee origins and brewing tips. 40 seats, small outdoor patio. Sources beans from local roasters. Also sells bags of beans and brewing equipment online.",
            "customer_description": "Coffee enthusiasts aged 25-40, mix of regulars and curious newcomers. Many visit the website before their first visit. Tech-savvy crowd (Austin startup culture). Care about origin stories and brewing methods. Newsletter has 800 subscribers.",
            "location": "Austin, USA",
            "location_country": "US",
            "location_city": "Austin",
            "is_online_only": False,
            "years_open": "1-3",
            "business_role": ["treat", "community_hub"],
            "business_not_role": ["convenience", "daily_need"],
            "visit_frequency": "weekly",
            "busy_days": ["saturday", "sunday", "friday"],
            "busy_times": ["morning", "afternoon"],
            "customer_value_drivers": ["specific_product", "atmosphere"],
            "customer_social_context": ["solo", "friends", "remote_work"],
            "regular_proportion": "solid_base",
            "customer_age_distribution": {"18-24": 15, "25-34": 40, "35-44": 25, "45-54": 12, "55-64": 5, "65+": 3},
            "customer_income_bracket": "middle",
            "average_transaction_value": 7.50,
            "customer_gender_split": "balanced",
            "local_vs_visitor_ratio": {"loyal_regulars": 30, "casual_regulars": 25, "occasional_visitors": 25, "first_timers": 15, "tourists": 5},
            "digital_savviness": "very_high",
            "price_range": "mid",
            "customer_discovery": ["instagram", "google_maps", "word_of_mouth", "yelp"],
            "nearby_anchors": ["East Austin tech offices", "South Congress shops", "UT campus"],
            "competitor_advantage": ["drive-through", "loyalty apps", "more locations"],
            "location_advantage": "Only specialty roaster on this block, foot traffic from nearby offices",
            "prior_changes": [
                {"change": "Launched online bean subscription", "year": 2023, "outcome": "positive", "metrics": "60 subscribers in first 3 months, 15% of in-store regulars signed up"},
                {"change": "Extended hours to 9pm on Fridays", "year": 2024, "outcome": "mixed", "metrics": "Evening traffic was light, only 8 customers/night on average, but built community event reputation"},
            ],
            "area_demographics": ["residential", "student"],
            "competitor_count": "three_five",
            "area_feel": "community",
        },
        "question": "On our website, should the main button say 'Sign Up for Updates' or 'Learn More About Us'?",
        "variant_a": "Sign Up for Updates",
        "variant_b": "Learn More About Us",
        "expected_winner": "B",
    },
    {
        "id": 6,
        "name": "Airbnb -- Professional Photography",
        "source": "First Round Review / Airbnb growth team",
        "real_winner": "professional_photos",
        "real_outcome": "Listings with professional photos got 2-3x more bookings",
        "holdout": False,
        "survey": {
            "name": "Casa del Sol",
            "type": "hotel",
            "description": "Small vacation rental apartment in a coastal Spanish town. 2 bedrooms, sea view, renovated kitchen. Listed on Airbnb and Booking.com. Managed by the owner who lives nearby. Average stay is 5 nights.",
            "customer_description": "Couples and small families looking for a holiday rental. Book 2-3 months ahead, compare photos heavily before booking. Most are from UK, Germany, and Scandinavia. Price-sensitive but will pay more for a place that looks special in photos.",
            "location": "Malaga, Spain",
            "location_country": "ES",
            "location_city": "Malaga",
            "is_online_only": False,
            "years_open": "1-3",
            "business_role": ["destination", "treat"],
            "business_not_role": ["convenience", "daily_need"],
            "visit_frequency": "occasional",
            "busy_days": ["saturday"],
            "busy_times": ["afternoon"],
            "customer_value_drivers": ["atmosphere", "value"],
            "customer_social_context": ["couple", "family"],
            "regular_proportion": "very_few",
            "customer_age_distribution": {"18-24": 5, "25-34": 25, "35-44": 35, "45-54": 20, "55-64": 10, "65+": 5},
            "customer_income_bracket": "middle_upper",
            "average_transaction_value": 680.0,
            "customer_gender_split": "balanced",
            "local_vs_visitor_ratio": {"loyal_regulars": 5, "casual_regulars": 10, "occasional_visitors": 15, "first_timers": 30, "tourists": 40},
            "digital_savviness": "high",
            "price_range": "mid",
            "customer_discovery": ["airbnb_search", "booking_com", "google_search"],
            "nearby_anchors": ["Malaga beach promenade", "Picasso Museum", "Malaga airport"],
            "competitor_advantage": ["pool access", "newer interiors", "professional management", "instant booking"],
            "location_advantage": "Direct sea view from balcony, 3 minute walk to beach",
            "prior_changes": [
                {"change": "Renovated kitchen and added dishwasher", "year": 2023, "outcome": "positive", "metrics": "Review scores for cleanliness went from 4.3 to 4.7, mentioned in 30% of reviews"},
                {"change": "Added air conditioning to both bedrooms", "year": 2022, "outcome": "positive", "metrics": "Summer bookings increased 25%, no more complaints about heat"},
            ],
            "area_demographics": ["tourist"],
            "competitor_count": "six_plus",
            "area_feel": "destination",
        },
        "question": "Should I invest in professional photos for my rental listing, or are my phone photos good enough?",
        "variant_a": None,
        "variant_b": None,
        "expected_winner": "positive",
    },
    {
        "id": 7,
        "name": "Amazon -- One-Click Checkout",
        "source": "Brad Stone's The Everything Store",
        "real_winner": "one_click",
        "real_outcome": "One-click massively increased purchase completion rates",
        "holdout": False,
        "survey": {
            "name": "The Gadget Shop",
            "type": "ecommerce",
            "description": "Small online electronics store selling phone accessories, chargers, cables, and small gadgets. Average order under 30 EUR. Fast shipping within Germany. Shopify store with 5,000 monthly visitors. Run by 2 people.",
            "customer_description": "Tech-savvy 20-35 year olds who buy impulsively when they see something they want. Very impatient with slow checkouts. Many shop on mobile during commutes. Compare prices across 3-4 sites. Low brand loyalty -- will switch for 2 EUR savings.",
            "location": "Berlin, Germany",
            "location_country": "DE",
            "location_city": "Berlin",
            "is_online_only": True,
            "years_open": "1-3",
            "business_role": ["convenience"],
            "business_not_role": ["destination", "treat"],
            "visit_frequency": "monthly",
            "busy_days": ["monday", "tuesday"],
            "busy_times": ["evening"],
            "customer_value_drivers": ["convenience", "value"],
            "customer_social_context": ["solo"],
            "regular_proportion": "handful",
            "customer_age_distribution": {"18-24": 25, "25-34": 40, "35-44": 20, "45-54": 10, "55-64": 4, "65+": 1},
            "customer_income_bracket": "middle",
            "average_transaction_value": 28.0,
            "customer_gender_split": "slightly_male",
            "local_vs_visitor_ratio": {"loyal_regulars": 10, "casual_regulars": 15, "occasional_visitors": 30, "first_timers": 40, "tourists": 5},
            "digital_savviness": "very_high",
            "price_range": "low",
            "customer_discovery": ["google_search", "google_shopping", "price_comparison_sites", "social_media_ads"],
            "nearby_anchors": ["Amazon.de", "MediaMarkt online", "idealo.de price comparison"],
            "competitor_advantage": ["Prime shipping", "wider selection", "established trust", "easy returns"],
            "location_advantage": "Curated selection of trending gadgets, faster new product listings than big retailers",
            "prior_changes": [
                {"change": "Added PayPal and Klarna payment options", "year": 2023, "outcome": "positive", "metrics": "Cart abandonment dropped 12%, Klarna used by 30% of orders"},
                {"change": "Raised free shipping threshold from 20 to 30 EUR", "year": 2024, "outcome": "negative", "metrics": "Average order value rose 3 EUR but conversion rate dropped 8%, net revenue down"},
            ],
            "area_demographics": ["residential", "student"],
            "competitor_count": "six_plus",
            "area_feel": "transactional",
        },
        "question": "Should we let returning customers buy with a single click using saved payment info, or keep our current 3-step checkout?",
        "variant_a": "One-click checkout for returning customers",
        "variant_b": "Keep 3-step checkout process",
        "expected_winner": "A",
    },
    # Holdout cases (8, 9, 10) -- we DO run them but don't tune prompts against them
    {
        "id": 8,
        "name": "Basecamp -- Long-Form Landing Page",
        "source": "Signal v. Noise blog",
        "real_winner": "long_form",
        "real_outcome": "Long-form page increased signups by 37.5%",
        "holdout": True,
        "survey": {
            "name": "TaskFlow",
            "type": "saas",
            "description": "Small project management SaaS for freelancers and small teams (2-10 people). Monthly subscription at $12/user. Free 14-day trial. Web app with basic mobile support. Competes with Asana, Monday.com, and Basecamp on simplicity.",
            "customer_description": "Freelancers and small agency owners who need to organize projects but hate complex tools. Usually try 2-3 tools during free trials before committing. Value simplicity over features. Most find us through Google search or Product Hunt.",
            "location": "Toronto, Canada",
            "location_country": "CA",
            "location_city": "Toronto",
            "is_online_only": True,
            "years_open": "<1",
            "business_role": ["daily_need"],
            "business_not_role": ["treat", "destination"],
            "visit_frequency": "subscription",
            "busy_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "busy_times": ["morning", "afternoon"],
            "customer_value_drivers": ["convenience", "quality"],
            "customer_social_context": ["solo", "small_team"],
            "regular_proportion": "majority",
            "customer_age_distribution": {"18-24": 8, "25-34": 35, "35-44": 30, "45-54": 18, "55-64": 7, "65+": 2},
            "customer_income_bracket": "middle_upper",
            "average_transaction_value": 12.0,
            "customer_gender_split": "slightly_male",
            "local_vs_visitor_ratio": {"loyal_regulars": 35, "casual_regulars": 25, "occasional_visitors": 20, "first_timers": 20, "tourists": 0},
            "digital_savviness": "very_high",
            "price_range": "low_mid",
            "customer_discovery": ["google_search", "product_hunt", "twitter", "word_of_mouth", "comparison_blogs"],
            "nearby_anchors": ["Asana", "Monday.com", "Basecamp", "Notion"],
            "competitor_advantage": ["more integrations", "bigger teams", "mobile apps", "brand recognition"],
            "location_advantage": "Positioned as the simplest option -- 5-minute setup, no training needed",
            "prior_changes": [
                {"change": "Added Slack integration", "year": 2025, "outcome": "positive", "metrics": "Trial-to-paid conversion up 10%, Slack mentioned in 25% of signup surveys"},
                {"change": "Reduced free trial from 30 to 14 days", "year": 2025, "outcome": "positive", "metrics": "No change in conversion rate but faster decision cycle, support costs down 20%"},
            ],
            "area_demographics": ["business"],
            "competitor_count": "six_plus",
            "area_feel": "transactional",
        },
        "question": "Should our main page be a short clean design with just our tagline and a 'Get Started' button, or a longer page that explains what we do in detail?",
        "variant_a": "Short and minimal",
        "variant_b": "Long and detailed with feature explanations",
        "expected_winner": "B",
    },
    {
        "id": 9,
        "name": "Walmart -- Page Load Speed",
        "source": "Walmart Labs engineering blog",
        "real_winner": "faster",
        "real_outcome": "Every 1 second improvement = up to 2% more conversions",
        "holdout": True,
        "survey": {
            "name": "Craft Corner",
            "type": "ecommerce",
            "description": "Small e-commerce store selling craft supplies -- yarn, fabric, beads, tools. 3,000 SKUs. Website is functional but slow, loads in about 5 seconds on average. Built on WooCommerce. 8,000 monthly visitors. Run by a team of 3.",
            "customer_description": "Crafters aged 30-55, patient but increasingly expect fast websites from the Amazon era. Browse a lot before buying -- average 12 pages per session. Many build wishlists over weeks. Loyal to stores that carry specialty items they cannot find elsewhere.",
            "location": "Manchester, UK",
            "location_country": "GB",
            "location_city": "Manchester",
            "is_online_only": True,
            "years_open": "3-10",
            "business_role": ["destination"],
            "business_not_role": ["convenience", "daily_need"],
            "visit_frequency": "monthly",
            "busy_days": ["saturday", "sunday"],
            "busy_times": ["afternoon", "evening"],
            "customer_value_drivers": ["specific_product", "value"],
            "customer_social_context": ["solo", "craft_groups"],
            "regular_proportion": "solid_base",
            "customer_age_distribution": {"18-24": 5, "25-34": 15, "35-44": 25, "45-54": 30, "55-64": 18, "65+": 7},
            "customer_income_bracket": "middle",
            "average_transaction_value": 32.0,
            "customer_gender_split": "mostly_female",
            "local_vs_visitor_ratio": {"loyal_regulars": 25, "casual_regulars": 25, "occasional_visitors": 25, "first_timers": 20, "tourists": 5},
            "digital_savviness": "medium",
            "price_range": "low_mid",
            "customer_discovery": ["google_search", "craft_forums", "pinterest", "facebook_groups"],
            "nearby_anchors": ["Hobbycraft online", "Amazon craft supplies", "local craft fairs"],
            "competitor_advantage": ["faster websites", "Prime delivery", "click and collect", "bigger range"],
            "location_advantage": "Specialist range of hard-to-find supplies, knowledgeable product descriptions",
            "prior_changes": [
                {"change": "Added customer review system", "year": 2022, "outcome": "positive", "metrics": "Products with reviews had 20% higher conversion, 400 reviews collected in first year"},
                {"change": "Launched loyalty points programme", "year": 2023, "outcome": "mixed", "metrics": "Repeat purchase rate up 5% but programme admin was time-consuming, many points never redeemed"},
            ],
            "area_demographics": ["residential"],
            "competitor_count": "three_five",
            "area_feel": "destination",
        },
        "question": "Our website takes 5 seconds to load. If we invested in making it load in 2 seconds, would customers buy more?",
        "variant_a": None,
        "variant_b": None,
        "expected_winner": "positive",
    },
    {
        "id": 10,
        "name": "Groove -- Personal vs Corporate Email",
        "source": "Groove HQ blog (Alex Turnbull)",
        "real_winner": "personal",
        "real_outcome": "Personal emails had 2x higher response rates",
        "holdout": True,
        "survey": {
            "name": "BrightDesk",
            "type": "saas",
            "description": "Small customer support SaaS, 500 active users. Help desk ticketing system for small businesses. $29/month per team. Free trial for 14 days. Sends onboarding emails to new signups to drive activation during the trial period.",
            "customer_description": "Small business owners and customer support managers who just signed up for a help desk tool. Evaluating during free trial, comparing with 2-3 alternatives (Zendesk, Freshdesk, Intercom). Time-poor, inbox-overloaded. Respond best to emails that feel personal and relevant.",
            "location": "San Francisco, USA",
            "location_country": "US",
            "location_city": "San Francisco",
            "is_online_only": True,
            "years_open": "1-3",
            "business_role": ["daily_need"],
            "business_not_role": ["treat", "destination"],
            "visit_frequency": "subscription",
            "busy_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
            "busy_times": ["morning"],
            "customer_value_drivers": ["convenience", "personal_touch"],
            "customer_social_context": ["small_team", "solo"],
            "regular_proportion": "majority",
            "customer_age_distribution": {"18-24": 5, "25-34": 30, "35-44": 35, "45-54": 20, "55-64": 8, "65+": 2},
            "customer_income_bracket": "upper",
            "average_transaction_value": 29.0,
            "customer_gender_split": "slightly_male",
            "local_vs_visitor_ratio": {"loyal_regulars": 30, "casual_regulars": 20, "occasional_visitors": 15, "first_timers": 35, "tourists": 0},
            "digital_savviness": "very_high",
            "price_range": "mid",
            "customer_discovery": ["google_search", "product_hunt", "saas_review_sites", "word_of_mouth", "twitter"],
            "nearby_anchors": ["Zendesk", "Freshdesk", "Intercom", "Help Scout"],
            "competitor_advantage": ["more features", "better integrations", "bigger brand", "AI-powered"],
            "location_advantage": "Simple and human -- positioned as the anti-enterprise help desk",
            "prior_changes": [
                {"change": "Added in-app onboarding walkthrough", "year": 2024, "outcome": "positive", "metrics": "Day-1 activation up 22%, support tickets from new users down 30%"},
                {"change": "Raised price from $19 to $29/month", "year": 2025, "outcome": "mixed", "metrics": "Revenue per user up 52% but trial-to-paid conversion dropped from 18% to 14%"},
            ],
            "area_demographics": ["business"],
            "competitor_count": "six_plus",
            "area_feel": "transactional",
        },
        "question": "Should our customer emails come from me personally (casual tone, my name) or from the company (professional tone, company name)?",
        "variant_a": "Personal tone from owner (Hi, it's Alex...)",
        "variant_b": "Professional corporate tone (Dear valued customer...)",
        "expected_winner": "A",
    },
]

# Merge extra cases from backtest_cases.py
BACKTEST_CASES.extend(EXTRA_BACKTEST_CASES)


def _score_prediction(case: dict, result: dict) -> dict:
    """Score whether our simulation predicted the right outcome.

    Uses multiple signals:
    1. Explicit winner field (for A/B tests)
    2. Recommendation text analysis (implement/go ahead vs avoid/don't)
    3. Behavioral prediction (would behavior actually change positively?)
    4. Stated-vs-actual gap (if personas say negative but admit they'd still convert)

    Returns dict with was_correct, confidence, our_prediction, real_outcome, reasoning.
    """
    expected = case["expected_winner"]
    summary = (result.get("summary", "") or "").lower()
    recommendation = (result.get("recommendation", "") or "").lower()
    full_text = summary + " " + recommendation
    winner = result.get("winner", "") or ""
    gap = (result.get("stated_vs_actual_gap", "") or "").lower()
    behavioral = result.get("behavioral_prediction") or {}
    override = result.get("research_override") or {}

    # If research override was applied, incorporate its adjusted recommendation
    if override.get("override_applied") and override.get("adjusted_recommendation"):
        full_text += " " + override["adjusted_recommendation"].lower()

    # --- A/B tests with explicit variants ---
    if expected in ("A", "B"):
        if winner and winner.upper() in ("A", "B"):
            our_prediction = winner.upper()
            was_correct = our_prediction == expected
            reasoning = f"Explicit winner field: {our_prediction}, expected: {expected}"
        elif winner and winner.lower() == "tie":
            # A declared tie is a non-prediction. It only counts as correct if the
            # recommendation text STRICTLY leans toward the expected option by a
            # clear margin (>=2 signals). A tie with equal signals is wrong --
            # "we couldn't tell" is not the same as the real-world answer.
            a_signals = sum(1 for w in ["option a", "first option", "variant a", "former"] if w in full_text)
            b_signals = sum(1 for w in ["option b", "second option", "variant b", "latter"] if w in full_text)
            margin = 2
            if expected == "A":
                was_correct = a_signals - b_signals >= margin
            else:
                was_correct = b_signals - a_signals >= margin
            our_prediction = "A" if a_signals > b_signals else "B" if b_signals > a_signals else "tie"
            reasoning = f"Tie declared, leaning: A={a_signals} B={b_signals}, margin_required={margin}"
        else:
            # No winner field -- infer from full text, require a clear margin
            a_words = ["option a", "first option", "recommend a", "variant a", "go with a"]
            b_words = ["option b", "second option", "recommend b", "variant b", "go with b"]
            a_count = sum(1 for w in a_words if w in full_text)
            b_count = sum(1 for w in b_words if w in full_text)
            margin = 2
            if a_count - b_count >= margin:
                our_prediction = "A"
            elif b_count - a_count >= margin:
                our_prediction = "B"
            else:
                our_prediction = "unknown"
            was_correct = our_prediction == expected
            reasoning = f"Inferred: A={a_count} B={b_count}, predicted={our_prediction}, margin_required={margin}"

    # --- Positive/negative outcome tests (no A/B) ---
    elif expected == "positive":
        # Multiple scoring passes -- a positive prediction means the system recommends doing it

        # Pass 1: Does the recommendation say to do it?
        do_it_words = ["implement", "go ahead", "worth", "invest", "should", "recommend",
                       "proceed", "try it", "test it", "roll out", "adopt", "add",
                       "low risk", "low-risk", "no downside", "upside"]
        dont_words = ["avoid", "don't", "do not", "not worth", "won't help",
                      "won't move", "waste", "focus elsewhere", "skip"]

        do_score = sum(1 for w in do_it_words if w in full_text)
        dont_score = sum(1 for w in dont_words if w in full_text)

        # Pass 2: Does the behavioral prediction suggest positive change?
        beh_positive = False
        if behavioral:
            eng = str(behavioral.get("engagement_change", "")).lower()
            spend = str(behavioral.get("spend_change", "")).lower()
            if any(w in eng for w in ["increase", "more", "higher", "grow", "improve"]):
                beh_positive = True
                do_score += 2
            if any(w in spend for w in ["increase", "more", "higher"]):
                do_score += 1

        # Pass 3: Does the say-do gap suggest the change works despite stated resistance?
        gap_positive = False
        if gap:
            gap_hints = ["would still", "end up", "actually", "despite saying",
                         "admit", "behavior would change", "convert", "respond to"]
            if any(h in gap for h in gap_hints):
                gap_positive = True
                do_score += 2

        # Pass 4: Check for hedged positive ("low risk", "could help", "worth testing")
        hedge_positive = ["could help", "might help", "worth testing", "try it",
                          "small improvement", "incremental", "won't hurt",
                          "no risk", "low risk"]
        if any(h in full_text for h in hedge_positive):
            do_score += 1

        was_correct = do_score > dont_score
        our_prediction = "positive" if was_correct else "negative"
        reasoning = (
            f"Do-it signals: {do_score}, Don't signals: {dont_score}. "
            f"Behavioral: {'positive' if beh_positive else 'neutral'}. "
            f"Say-do gap: {'supports' if gap_positive else 'neutral'}."
        )

    # --- Tie cases (null/no-difference outcomes) ---
    elif expected == "tie":
        # For null cases, we're testing whether the system correctly predicts
        # "no clear winner" / "tie" when variants perform equivalently.
        # A correct prediction is either:
        # 1. Explicit "tie" winner field
        # 2. Very balanced text signals (a_count ≈ b_count)
        if winner and winner.lower() == "tie":
            was_correct = True
            our_prediction = "tie"
            reasoning = "Explicitly predicted tie (correct for null case)"
        else:
            a_words = ["option a", "first option", "recommend a", "variant a", "go with a"]
            b_words = ["option b", "second option", "recommend b", "variant b", "go with b"]
            a_count = sum(1 for w in a_words if w in full_text)
            b_count = sum(1 for w in b_words if w in full_text)
            # For null cases, predictions are correct when a_count and b_count
            # are very close (diff <= 1) OR when neither is strongly favored
            diff = abs(a_count - b_count)
            was_correct = diff <= 1
            our_prediction = "A" if a_count > b_count else "B" if b_count > a_count else "tie"
            reasoning = f"Tie case: A={a_count}, B={b_count}, diff={diff}, correct=(diff<=1)"

    else:
        was_correct = False
        our_prediction = "unknown"
        reasoning = "Could not determine prediction"

    return {
        "was_correct": was_correct,
        "confidence": result.get("confidence_score", "unknown"),
        "our_prediction": our_prediction,
        "real_outcome": case["real_outcome"],
        "reasoning": reasoning,
    }


async def run_single_backtest(case: dict, persona_count: int = 15) -> dict:
    """Run a single backtest case through the full simulation pipeline.

    Mirrors the production pipeline in simulations.py: builds RAG context
    from survey data, psychological profile, research context, then runs
    focus group interviews with full context enrichment.
    """
    start = time.monotonic()
    survey = case["survey"]

    # Build FULL BusinessSnapshot with ALL available fields
    snapshot_fields = {}
    for field_name in BusinessSnapshot.model_fields:
        if field_name in survey:
            snapshot_fields[field_name] = survey[field_name]
    business = BusinessSnapshot(**snapshot_fields)

    logger.info("Running backtest %d: %s", case["id"], case["name"])

    try:
        # -- Step 1: Build RAG context from survey data --
        survey_context = ""
        try:
            from backend.survey.rag_builder import build_rag_context
            survey_context = build_rag_context(survey)
            logger.info("Survey RAG context: %d chars", len(survey_context))
        except Exception as e:
            logger.warning("Survey RAG builder failed (non-fatal): %s", e)

        # -- Step 2: Build psychological profile --
        profile_context = ""
        try:
            from backend.context.profile_builder import build_profile
            country = survey.get("location_country", "")
            psych_profile = build_profile(business, country_code=country)
            if psych_profile.summary:
                profile_context = psych_profile.summary
                logger.info("Psychological profile: %d chars, confidence=%s",
                            len(profile_context), psych_profile.confidence)
        except Exception as e:
            logger.warning("Profile builder failed (non-fatal): %s", e)

        # -- Step 3: Build research context (targeted by business type + question) --
        research_context = ""
        try:
            from research.rag_library import get_simulation_context
            country = survey.get("location_country", "DEFAULT")
            research_context = get_simulation_context(
                country_code=country,
                simulation_type="consumer",
                business_type=business.type,
                question=case["question"],
                demographics={
                    "age": business.customer_age_distribution,
                    "income": business.customer_income_bracket,
                    "digital": business.digital_savviness,
                },
            )
            logger.info("Research context: %d chars for country=%s, type=%s",
                        len(research_context), country, business.type)
        except Exception as e:
            logger.warning("Research library failed (non-fatal): %s", e)

        # -- Step 4: Combine all context sources --
        enriched_parts = []
        if survey_context:
            enriched_parts.append(survey_context)
        if profile_context:
            enriched_parts.append(profile_context)
        if research_context:
            enriched_parts.append(research_context[:4000])
        context_narrative = "\n\n---\n\n".join(enriched_parts) if enriched_parts else None

        if context_narrative:
            logger.info("Enriched context: %d chars total (survey=%d, profile=%d, research=%d)",
                        len(context_narrative), len(survey_context),
                        len(profile_context), min(len(research_context), 4000))

        # -- Step 5: Generate personas WITH context --
        personas = await generate_personas(
            business, persona_count, context_narrative=context_narrative,
        )

        # -- Step 6: Run focus group interviews WITH context --
        responses = await run_simulation(
            personas, business, case["question"],
            case.get("variant_a"), case.get("variant_b"),
            context_narrative=context_narrative,
            focus_group=True,
        )

        # -- Step 7: Aggregate WITH context --
        result = await aggregate_responses(
            business, case["question"], responses,
            case.get("variant_a"), case.get("variant_b"),
            context_narrative=context_narrative,
            expected_persona_count=len(personas),
        )

        # -- Step 7.5: Research override --
        # Strong + high-confidence overrides now mutate the aggregation:
        # they flip `winner` and prefix `recommendation`. See
        # backend.swarm.research_override.apply_override_to_result.
        research_override = None
        try:
            from backend.swarm.research_override import (
                apply_research_override,
                apply_override_to_result,
            )
            research_override = await apply_research_override(
                question=case["question"],
                aggregation_result=result,
                persona_responses=responses,
                business_type=business.type,
            )
            if research_override and research_override.get("override_applied"):
                result = apply_override_to_result(result, research_override)
                logger.info(
                    "Research override: tactic=%s, conflict=%s, flipped=%s",
                    research_override.get("tactic_detected"),
                    research_override.get("conflict_level"),
                    result.get("winner_flipped", False),
                )
        except Exception as e:
            logger.warning("Research override failed (non-fatal): %s", e)

        # -- Step 7.6: Structural bias correction --
        try:
            from backend.swarm.bias_correction import (
                apply_bias_correction,
                average_sentiments_from_responses,
            )
            tactic = (research_override or {}).get("tactic_detected")
            if tactic:
                stated_avg, revealed_avg = average_sentiments_from_responses(responses)
                result = apply_bias_correction(
                    result,
                    question=case["question"],
                    tactic=tactic,
                    average_stated_sentiment=stated_avg,
                    average_revealed_sentiment=revealed_avg,
                )
        except Exception as e:
            logger.warning("Bias correction failed (non-fatal): %s", e)

        # -- Step 8: Impact estimate --
        impact = estimate_impact(responses, case["question"], business_type=business.type)

        # -- Step 9: Caveats --
        caveats = generate_caveats(
            business, case["question"], persona_count, len(responses),
            case.get("variant_a"), case.get("variant_b"),
        )

        # -- Step 10: Score prediction against reality --
        score = _score_prediction(case, result)

        # -- Step 11: Compute diversity metrics (for methodology assessment) --
        diversity = _compute_diversity_metrics(responses)

        elapsed = time.monotonic() - start

        # Extract features for ML training
        extractor = FeatureExtractor()
        features = extractor.extract(survey)

        return {
            "case_id": case["id"],
            "case_name": case["name"],
            "holdout": case.get("holdout", False),
            "was_correct": score["was_correct"],
            "our_prediction": score["our_prediction"],
            "expected_winner": case["expected_winner"],
            "real_outcome": case["real_outcome"],
            "confidence": score["confidence"],
            "reasoning": score["reasoning"],
            "summary": result.get("summary", ""),
            "recommendation": result.get("recommendation", ""),
            "winner": result.get("winner"),
            "behavioral_prediction": result.get("behavioral_prediction"),
            "stated_vs_actual_gap": result.get("stated_vs_actual_gap"),
            "baseline_summary": result.get("baseline_summary"),
            "research_override": result.get("research_override"),
            "winner_flipped": result.get("winner_flipped", False),
            "winner_flipped_from": result.get("winner_flipped_from"),
            "bias_correction": result.get("bias_correction"),
            "persona_count": len(personas),
            "response_count": len(responses),
            "caveat_count": len(caveats),
            "impact_decision": impact.decision,
            "diversity_metrics": diversity,
            "elapsed_seconds": round(elapsed, 1),
            "features": features,
            "feature_names": extractor.feature_names,
            "context_chars": len(context_narrative) if context_narrative else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        elapsed = time.monotonic() - start
        logger.error("Backtest %d failed: %s", case["id"], e)
        return {
            "case_id": case["id"],
            "case_name": case["name"],
            "holdout": case.get("holdout", False),
            "was_correct": None,
            "error": str(e),
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": datetime.utcnow().isoformat(),
        }


async def run_all_backtests(
    persona_count: int = 15,
    only_ids: list[int] = None,
    aa_repeats: int = 1,
) -> list[dict]:
    """Run all backtest cases and produce a scored report.

    When ``aa_repeats > 1`` each case is executed that many times with the
    SAME inputs. This is an A/A-style noise measurement: two runs that
    disagree reveal the within-simulation variance. Each repeat is a
    separate result row, tagged with ``aa_run_index`` (0-based) so we can
    compute winner stability per case.
    """
    results = []

    for case in BACKTEST_CASES:
        if only_ids and case["id"] not in only_ids:
            continue

        for run_idx in range(aa_repeats):
            result = await run_single_backtest(case, persona_count)
            if aa_repeats > 1:
                result["aa_run_index"] = run_idx
                result["aa_total_runs"] = aa_repeats
            results.append(result)

            # Save incrementally
            _save_results(results)

            # Print live progress
            status = "CORRECT" if result.get("was_correct") else "WRONG" if result.get("was_correct") is False else "ERROR"
            holdout = " [HOLDOUT]" if result.get("holdout") else ""
            run_label = f" run={run_idx+1}/{aa_repeats}" if aa_repeats > 1 else ""
            print(f"  [{status}] {result['case_name']}{holdout}{run_label} ({result.get('elapsed_seconds', 0)}s)")

    if aa_repeats > 1:
        _print_aa_noise_report(results)

    # Print methodology assessment reports
    _print_methodology_assessment(results)

    return results


def _compute_diversity_metrics(responses: list[dict]) -> dict:
    """Compute swarm diversity metrics from persona responses.

    Returns:
    - sentiment_std_dev: std deviation of sentiment scores across personas
    - sentiment_range: (min, max) sentiment values
    - agreement_level: "low" if std_dev > 0.25, "medium" if 0.15-0.25, "high" if < 0.15
    """
    import statistics

    sentiments = []
    for r in responses:
        core = r.get("core") or {}
        try:
            s = float(core.get("sentiment", 0.0))
            sentiments.append(s)
        except (TypeError, ValueError):
            pass

    if len(sentiments) < 2:
        return {
            "sentiment_std_dev": None,
            "sentiment_range": None,
            "agreement_level": "insufficient_data",
            "persona_count_with_sentiment": len(sentiments),
        }

    std_dev = statistics.stdev(sentiments)
    agreement = "high" if std_dev < 0.15 else "medium" if std_dev < 0.25 else "low"

    return {
        "sentiment_std_dev": round(std_dev, 3),
        "sentiment_range": (round(min(sentiments), 3), round(max(sentiments), 3)),
        "agreement_level": agreement,
        "persona_count_with_sentiment": len(sentiments),
    }


def _print_methodology_assessment(results: list[dict]) -> None:
    """Print methodology assessment: calibration, diversity, and test categorization."""
    from collections import defaultdict

    # Categorize results
    by_category = defaultdict(list)
    for r in results:
        if r.get("was_correct") is None:
            continue
        case_id = r["case_id"]
        # Categorize by test type
        if case_id <= 10:
            category = "Original (1-10)"
        elif case_id <= 35:
            category = "Extra published (11-35)"
        elif case_id <= 38:
            category = "Reversed (36-38)"
        elif case_id <= 42:
            category = "Dark cases (39-42)"
        elif case_id <= 44:
            category = "Null cases (43-44)"
        else:
            category = "Other"
        by_category[category].append(r)

    # Calibration analysis
    print()
    print("=" * 70)
    print("METHODOLOGY ASSESSMENT")
    print("=" * 70)

    # Accuracy by test category
    print()
    print("Accuracy by Test Category:")
    print("-" * 70)
    for category in ["Original (1-10)", "Extra published (11-35)", "Reversed (36-38)",
                     "Dark cases (39-42)", "Null cases (43-44)", "Other"]:
        if category not in by_category:
            continue
        rows = by_category[category]
        correct = sum(1 for r in rows if r.get("was_correct"))
        total = len(rows)
        pct = (correct / total * 100) if total > 0 else 0
        print(f"  {category:<30} {correct:>3}/{total:<3} ({pct:>5.1f}%)")

    # Diversity analysis
    print()
    print("Swarm Diversity (sentiment agreement level):")
    print("-" * 70)
    diversity_counts = defaultdict(int)
    for r in results:
        if r.get("was_correct") is None:
            continue
        div = r.get("diversity_metrics", {})
        agreement = div.get("agreement_level", "unknown")
        diversity_counts[agreement] += 1

    for level in ["low", "medium", "high"]:
        count = diversity_counts.get(level, 0)
        if count > 0 or level in diversity_counts:
            print(f"  {level.capitalize():>8} agreement: {count:>3} cases (sentiment std_dev across personas)")

    # Null case handling
    print()
    print("Null Case Predictions (tests where real outcome was 'tie'):")
    print("-" * 70)
    if "Null cases (43-44)" in by_category:
        null_results = by_category["Null cases (43-44)"]
        null_correct = sum(1 for r in null_results if r.get("was_correct"))
        null_total = len(null_results)
        null_pct = (null_correct / null_total * 100) if null_total > 0 else 0
        print(f"  Correctly predicted 'no difference': {null_correct}/{null_total} ({null_pct:.0f}%)")
        for r in null_results:
            pred = r.get("our_prediction", "?")
            outcome = r.get("expected_winner", "?")
            status = "✓" if r.get("was_correct") else "✗"
            print(f"    {status} Case {r['case_id']}: predicted '{pred}', expected '{outcome}'")

    # Reversed case analysis (contamination test)
    print()
    print("Reversed Cases (contamination check):")
    print("-" * 70)
    if "Reversed (36-38)" in by_category:
        reversed_results = by_category["Reversed (36-38)"]
        original_results = by_category.get("Original (1-10)", [])

        # Match reversed cases to originals
        reversed_correct = sum(1 for r in reversed_results if r.get("was_correct"))
        reversed_total = len(reversed_results)
        reversed_pct = (reversed_correct / reversed_total * 100) if reversed_total > 0 else 0

        original_pct = (sum(1 for r in original_results if r.get("was_correct")) / len(original_results) * 100) if original_results else 0

        print(f"  Original cases accuracy:  {original_pct:.0f}%")
        print(f"  Reversed cases accuracy:  {reversed_pct:.0f}%")
        if reversed_pct < original_pct - 10:
            print(f"  ⚠ WARNING: Accuracy dropped {original_pct - reversed_pct:.0f} points on reversed cases.")
            print(f"    This suggests potential data contamination or label dependency.")
        else:
            print(f"    ✓ No significant contamination detected.")

    print("=" * 70)


def _print_aa_noise_report(results: list[dict]) -> None:
    """Summarise A/A noise: for each case, how often did we get the same winner?"""
    from collections import Counter, defaultdict

    by_case: dict[int, list[dict]] = defaultdict(list)
    for r in results:
        if r.get("was_correct") is None:
            continue
        by_case[r["case_id"]].append(r)

    print()
    print("=" * 60)
    print("A/A NOISE REPORT")
    print("=" * 60)
    print(f"{'Case':<42} {'Runs':>5} {'Stability':>10}")
    print("-" * 60)
    stabilities: list[float] = []
    for case_id in sorted(by_case):
        runs = by_case[case_id]
        if len(runs) < 2:
            continue
        winners = [r.get("our_prediction") or r.get("winner") or "?" for r in runs]
        counts = Counter(winners)
        modal_count = counts.most_common(1)[0][1]
        stability = modal_count / len(runs)
        stabilities.append(stability)
        name = runs[0]["case_name"][:40]
        print(f"{name:<42} {len(runs):>5} {stability*100:>9.0f}%")
    print("-" * 60)
    if stabilities:
        avg = sum(stabilities) / len(stabilities)
        print(f"Mean winner stability across cases: {avg*100:.0f}%")
        print(
            "  -- lower stability = higher within-simulation noise. "
            "Predictions below 100% are a coin-flip component."
        )
    print("=" * 60)


def _save_results(results: list[dict]):
    """Save results to JSON (incremental)."""
    # Remove non-serializable items
    clean = []
    for r in results:
        c = {k: v for k, v in r.items() if k != "features"}
        clean.append(c)

    path = RESULTS_DIR / f"backtest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(clean, f, indent=2)


def print_report(results: list[dict]):
    """Print a human-readable backtest report."""
    scored = [r for r in results if r.get("was_correct") is not None]
    train_set = [r for r in scored if not r.get("holdout")]
    holdout_set = [r for r in scored if r.get("holdout")]

    train_correct = sum(1 for r in train_set if r["was_correct"])
    holdout_correct = sum(1 for r in holdout_set if r["was_correct"])

    print()
    print("=" * 60)
    print("BACKTEST REPORT")
    print("=" * 60)
    print()
    print(f"{'#':<4} {'Case':<40} {'Result':<10} {'Time':<8}")
    print("-" * 60)
    for r in results:
        if r.get("was_correct") is None:
            status = "ERROR"
        elif r["was_correct"]:
            status = "CORRECT"
        else:
            status = "WRONG"
        holdout = " *" if r.get("holdout") else ""
        print(f"{r['case_id']:<4} {r['case_name'][:38]:<40} {status:<10} {r.get('elapsed_seconds', 0):.0f}s{holdout}")

    print("-" * 60)
    if train_set:
        print(f"Training set accuracy: {train_correct}/{len(train_set)} ({train_correct/len(train_set)*100:.0f}%)")
    if holdout_set:
        print(f"Holdout set accuracy:  {holdout_correct}/{len(holdout_set)} ({holdout_correct/len(holdout_set)*100:.0f}%)")
    if scored:
        total_correct = train_correct + holdout_correct
        print(f"Overall accuracy:      {total_correct}/{len(scored)} ({total_correct/len(scored)*100:.0f}%)")
    print()
    print("* = holdout case (not used for prompt tuning)")
    print("=" * 60)


def get_training_data_from_results(results: list[dict]) -> tuple:
    """Extract ML training data from backtest results.

    Returns (X, y, feature_names) for training the calibration model.
    Only uses non-holdout cases.
    """
    import numpy as np

    train_results = [r for r in results
                     if r.get("was_correct") is not None
                     and not r.get("holdout")
                     and "features" in r]

    if not train_results:
        return np.array([]), np.array([]), []

    feature_names = train_results[0].get("feature_names", [])
    X = []
    y = []

    for r in train_results:
        feat = r["features"]
        vec = [feat.get(name, 0.0) for name in feature_names]
        X.append(vec)
        y.append(1 if r["was_correct"] else 0)

    return np.array(X), np.array(y), feature_names


# CLI entry point
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    only_ids = None
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        if idx + 1 < len(sys.argv):
            only_ids = [int(sys.argv[idx + 1])]

    persona_count = 15
    if "--personas" in sys.argv:
        idx = sys.argv.index("--personas")
        if idx + 1 < len(sys.argv):
            persona_count = int(sys.argv[idx + 1])

    print(f"Running backtests with {persona_count} personas per simulation...")
    print()

    results = asyncio.run(run_all_backtests(persona_count=persona_count, only_ids=only_ids))
    print_report(results)
