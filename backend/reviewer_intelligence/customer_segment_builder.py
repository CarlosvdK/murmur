"""
Builds a realistic customer segment distribution from all available signals.

THIS IS THE MOST IMPORTANT FILE IN THE REVIEWER INTELLIGENCE SYSTEM.
If the segment distribution is wrong, every persona is wrong.

Based on NeurIPS 2025 / ICLR 2024: personas MUST be anchored in structured
demographic data FIRST, then narrative detail added SECOND.
The CustomerSegmentProfile IS the structured anchor.

Industry-configurable: segment templates are selected based on business type,
so the system works for SaaS, e-commerce, B2B, healthcare, and more --
not just restaurants.
"""

import logging
from dataclasses import dataclass

from backend.models.business import BusinessSnapshot
from backend.reviewer_intelligence.bias_corrector import BiasAdjustedSignals
from backend.reviewer_intelligence.silent_majority_estimator import SilentMajorityProfile

logger = logging.getLogger(__name__)


@dataclass
class CustomerSegment:
    name: str
    description: str
    estimated_proportion: float
    price_sensitivity: str       # "low", "moderate", "high"
    loyalty_likelihood: float    # 0.0 to 1.0
    is_silent_majority: bool
    age_range: str               # "25-45" etc
    income_tier: str             # "budget", "mid", "affluent"
    visit_frequency: str         # "weekly", "monthly", "occasional", "one-time"
    key_decision_factors: list[str]


@dataclass
class CustomerSegmentProfile:
    segments: list[CustomerSegment]
    total_estimated_customers: str
    dominant_segment: str
    most_price_sensitive_segment: str
    silent_majority_proportion: float
    signals_used: list[str]
    confidence_level: str
    plain_english_summary: str


# ---------------------------------------------------------------------------
# Industry segment templates
# ---------------------------------------------------------------------------
# Each template defines 6 segments in a fixed order:
#   [0] silent_regular   -- high-volume silent users (silent majority, loyal)
#   [1] silent_occasional -- low-volume silent users (silent majority, flaky)
#   [2] vocal_loyalist   -- leaves positive reviews / advocates
#   [3] vocal_critic     -- leaves negative reviews / complaints
#   [4] transient        -- one-time / low-commitment (analogous to "tourists")
#   [5] price_driven     -- price is the primary decision lever
#
# Fields per segment:
#   name, description, price_sensitivity, loyalty_likelihood, is_silent_majority,
#   age_range, income_tier, engagement_label (replaces visit_frequency),
#   key_decision_factors

_SegmentTemplate = dict  # alias for readability

INDUSTRY_SEGMENT_TEMPLATES: dict[str, list[_SegmentTemplate]] = {

    # ------------------------------------------------------------------
    # PHYSICAL SERVICE (default) -- barbershops, salons, restaurants,
    # cafes, gyms, clinics, auto repair, dry cleaners
    # ------------------------------------------------------------------
    "physical_service": [
        {
            "name": "Silent Regulars",
            "description": "Come often, never leave feedback. Their routine spending is the backbone of your revenue, but you rarely hear what they actually think.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.6,
            "is_silent_majority": True,
            "age_range": "30-55",
            "income_tier": "mid",
            "engagement_label": "weekly",
            "key_decision_factors": ["convenience", "habit", "price", "consistency"],
        },
        {
            "name": "Silent Occasionals",
            "description": "Drop in a few times a year. Easily pulled away by a competitor opening nearby or a price change. You would not notice they left until the revenue dip shows up.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "22-50",
            "income_tier": "budget to mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["price", "convenience", "mood", "what friends suggest"],
        },
        {
            "name": "Loyal Advocates",
            "description": "Your most enthusiastic customers. They leave positive reviews and recommend you in person. Overrepresented in your online perception -- they make you look better than the average experience.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.9,
            "is_silent_majority": False,
            "age_range": "28-60",
            "income_tier": "mid to affluent",
            "engagement_label": "weekly",
            "key_decision_factors": ["quality", "relationship", "atmosphere", "consistency"],
        },
        {
            "name": "Frustrated Customers",
            "description": "Had a bad experience and told the internet about it. Included for balance -- they represent real friction points that your silent customers also feel but never mention.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": False,
            "age_range": "25-55",
            "income_tier": "mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["service quality", "feeling valued", "price fairness"],
        },
        {
            "name": "One-time Visitors",
            "description": "Passing through the area or trying you once on a whim. Unlikely to return regardless of what you do. Their reviews can skew your rating without reflecting your core customer base.",
            "price_sensitivity": "low to moderate",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": True,
            "age_range": "25-50",
            "income_tier": "mid to affluent",
            "engagement_label": "one-time",
            "key_decision_factors": ["location", "reviews", "atmosphere", "novelty"],
        },
        {
            "name": "Value Seekers",
            "description": "Chose you specifically because they see you as affordable. Most vulnerable to price increases -- even a small bump can push them to a competitor.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.4,
            "is_silent_majority": True,
            "age_range": "20-45",
            "income_tier": "budget",
            "engagement_label": "monthly",
            "key_decision_factors": ["price", "deals", "value for money", "portion or scope"],
        },
    ],

    # ------------------------------------------------------------------
    # SaaS -- software subscriptions, cloud tools, dev tools
    # ------------------------------------------------------------------
    "saas": [
        {
            "name": "Power Users",
            "description": "Use the product daily and depend on it. They rarely leave public reviews but will notice every regression. Losing even one is a revenue and word-of-mouth hit.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.75,
            "is_silent_majority": True,
            "age_range": "28-50",
            "income_tier": "mid to affluent",
            "engagement_label": "daily",
            "key_decision_factors": ["reliability", "feature depth", "integrations", "speed"],
        },
        {
            "name": "Casual Users",
            "description": "Log in a few times a month and use a fraction of features. Easy to lose to a simpler competitor. Often do not realize how much they pay relative to how little they use.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "22-45",
            "income_tier": "mid",
            "engagement_label": "monthly",
            "key_decision_factors": ["simplicity", "price", "habit", "switching cost"],
        },
        {
            "name": "Loyal Subscribers",
            "description": "Renew without hesitation and recommend you on social media, Slack channels, or G2. Their reviews define your brand perception but overrepresent the happy path.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.9,
            "is_silent_majority": False,
            "age_range": "30-55",
            "income_tier": "mid to affluent",
            "engagement_label": "weekly",
            "key_decision_factors": ["product quality", "support", "community", "brand trust"],
        },
        {
            "name": "Churn-Risk Users",
            "description": "Submitted support tickets, left critical reviews, or quietly reduced usage. They have already mentally left -- a price increase or outage will be the final push.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": False,
            "age_range": "25-50",
            "income_tier": "mid",
            "engagement_label": "declining",
            "key_decision_factors": ["support responsiveness", "bugs", "value for money", "alternatives"],
        },
        {
            "name": "Trial / Evaluating",
            "description": "Signed up recently and are comparing you against alternatives. Most will not convert. The ones who do are heavily influenced by onboarding friction and first-hour experience.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": True,
            "age_range": "24-40",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["onboarding ease", "time to value", "pricing clarity", "competitor comparison"],
        },
        {
            "name": "Price-Sensitive Tier",
            "description": "On the cheapest plan or constantly looking for discounts. They will downgrade or cancel the moment price rises. Often the loudest about pricing on social media.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.35,
            "is_silent_majority": True,
            "age_range": "20-35",
            "income_tier": "budget",
            "engagement_label": "monthly",
            "key_decision_factors": ["price", "free tier limits", "competitor pricing", "perceived value"],
        },
    ],

    # ------------------------------------------------------------------
    # E-COMMERCE -- online retail, DTC brands, marketplaces
    # ------------------------------------------------------------------
    "ecommerce": [
        {
            "name": "Repeat Buyers",
            "description": "Order regularly and know your product line. They rarely review but their lifetime value is high. A change in shipping cost or quality hits them hardest.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.65,
            "is_silent_majority": True,
            "age_range": "28-55",
            "income_tier": "mid",
            "engagement_label": "monthly",
            "key_decision_factors": ["product consistency", "shipping speed", "reorder convenience", "price stability"],
        },
        {
            "name": "Bargain Hunters",
            "description": "Only buy during sales or with coupons. High volume during promotions, zero activity at full price. They train themselves -- and your algorithm -- to expect discounts.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.2,
            "is_silent_majority": True,
            "age_range": "20-45",
            "income_tier": "budget to mid",
            "engagement_label": "seasonal",
            "key_decision_factors": ["price", "discounts", "free shipping thresholds", "deal timing"],
        },
        {
            "name": "Brand Loyalists",
            "description": "Buy because they believe in the brand. Leave positive reviews, share on social media, and refer friends. They are your marketing engine -- but they are a small minority.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.85,
            "is_silent_majority": False,
            "age_range": "25-50",
            "income_tier": "mid to affluent",
            "engagement_label": "monthly",
            "key_decision_factors": ["brand values", "product quality", "packaging", "story"],
        },
        {
            "name": "Disappointed Returners",
            "description": "Received something that did not match expectations. Left a negative review or initiated a return. Their complaints reveal gaps between your product photos and reality.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": False,
            "age_range": "22-55",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["product accuracy", "return policy", "customer service", "refund speed"],
        },
        {
            "name": "One-time Browsers",
            "description": "Found you through an ad or search, bought once, and moved on. They have no relationship with your brand and will not remember your name next week.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": True,
            "age_range": "18-50",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["search ranking", "ad creative", "price at that moment", "reviews"],
        },
        {
            "name": "High-Value Customers",
            "description": "Top 5-10% by spend. They buy premium products and add-ons without flinching. Losing even a few has an outsized revenue impact.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.7,
            "is_silent_majority": True,
            "age_range": "30-60",
            "income_tier": "affluent",
            "engagement_label": "weekly",
            "key_decision_factors": ["quality", "exclusivity", "convenience", "customer experience"],
        },
    ],

    # ------------------------------------------------------------------
    # B2B -- consulting, logistics, agencies, enterprise services
    # ------------------------------------------------------------------
    "b2b": [
        {
            "name": "Strategic Accounts",
            "description": "Long-term contracts, deep integrations, high switching cost. They will not leave easily -- but when they do, it is catastrophic. Their silence does not mean satisfaction.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.8,
            "is_silent_majority": True,
            "age_range": "35-55",
            "income_tier": "affluent",
            "engagement_label": "ongoing",
            "key_decision_factors": ["reliability", "account management", "customization", "SLA compliance"],
        },
        {
            "name": "Transactional Buyers",
            "description": "Buy project-by-project or as needed. No emotional attachment -- they compare quotes every time. Easy to lose on price alone.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.25,
            "is_silent_majority": True,
            "age_range": "30-50",
            "income_tier": "mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["price", "turnaround time", "availability", "past performance"],
        },
        {
            "name": "Loyal Partners",
            "description": "Refer you to their network, provide testimonials, and co-market with you. They amplify your reputation but represent a small fraction of your client base.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.9,
            "is_silent_majority": False,
            "age_range": "35-60",
            "income_tier": "mid to affluent",
            "engagement_label": "ongoing",
            "key_decision_factors": ["trust", "relationship", "results", "communication quality"],
        },
        {
            "name": "At-Risk Contracts",
            "description": "Sent complaints, delayed renewals, or started evaluating competitors. The decision-maker has already been pitched by your rival -- you just do not know it yet.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.15,
            "is_silent_majority": False,
            "age_range": "30-55",
            "income_tier": "mid",
            "engagement_label": "declining",
            "key_decision_factors": ["unresolved issues", "competitor offerings", "internal politics", "ROI proof"],
        },
        {
            "name": "New Prospects",
            "description": "Evaluating you for the first time. Their decision depends heavily on your proposal, references, and first impression. Most will not convert.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": True,
            "age_range": "28-50",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["credentials", "case studies", "proposal quality", "cultural fit"],
        },
        {
            "name": "Price-Driven Buyers",
            "description": "Procurement-led decisions where your contact has no budget discretion. They will squeeze margins every renewal cycle. Winning on price means you lose on price next time.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "30-50",
            "income_tier": "mid",
            "engagement_label": "annual",
            "key_decision_factors": ["price", "procurement policy", "volume discounts", "contract terms"],
        },
    ],

    # ------------------------------------------------------------------
    # SUBSCRIPTION -- gyms with memberships, streaming, meal kits, boxes
    # ------------------------------------------------------------------
    "subscription": [
        {
            "name": "Engaged Members",
            "description": "Use the service regularly and get real value from it. They do not think about cancelling, but they also do not leave reviews. Their satisfaction is invisible to you.",
            "price_sensitivity": "low to moderate",
            "loyalty_likelihood": 0.7,
            "is_silent_majority": True,
            "age_range": "28-50",
            "income_tier": "mid",
            "engagement_label": "weekly",
            "key_decision_factors": ["perceived value", "habit", "results", "convenience"],
        },
        {
            "name": "Zombie Subscribers",
            "description": "Still paying but barely using the service. They forget they are subscribed or keep meaning to cancel. Revenue from them is real but fragile -- one bank statement review away from gone.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.15,
            "is_silent_majority": True,
            "age_range": "22-45",
            "income_tier": "mid",
            "engagement_label": "rare",
            "key_decision_factors": ["inertia", "cancellation friction", "guilt", "price awareness"],
        },
        {
            "name": "Champions",
            "description": "Leave five-star reviews and tell their friends. They genuinely love the service and their enthusiasm shapes your public image. But they are a small slice of your member base.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.9,
            "is_silent_majority": False,
            "age_range": "25-55",
            "income_tier": "mid to affluent",
            "engagement_label": "daily",
            "key_decision_factors": ["community", "quality", "brand identity", "personal results"],
        },
        {
            "name": "Cancel-Pending",
            "description": "Already looked up how to cancel or paused their membership. A price increase will finalize the decision. Winning them back requires addressing the root cause, not a discount.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": False,
            "age_range": "22-40",
            "income_tier": "budget to mid",
            "engagement_label": "declining",
            "key_decision_factors": ["unmet expectations", "better alternatives", "budget pressure", "lack of results"],
        },
        {
            "name": "New Sign-ups",
            "description": "Joined in the last 30-90 days. Still in the honeymoon phase or already regretting the decision. Their retention depends entirely on the first few weeks of experience.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.2,
            "is_silent_majority": True,
            "age_range": "20-40",
            "income_tier": "mid",
            "engagement_label": "variable",
            "key_decision_factors": ["onboarding quality", "early wins", "community welcome", "ease of use"],
        },
        {
            "name": "Discount Dependents",
            "description": "Joined on a promotional rate and have never paid full price. They will leave the moment the introductory offer expires. Their lifetime value is often negative after acquisition cost.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.2,
            "is_silent_majority": True,
            "age_range": "18-35",
            "income_tier": "budget",
            "engagement_label": "monthly",
            "key_decision_factors": ["price", "promotional offers", "free trial length", "competitor deals"],
        },
    ],

    # ------------------------------------------------------------------
    # RETAIL -- physical stores, boutiques, hardware stores, bookshops
    # ------------------------------------------------------------------
    "retail": [
        {
            "name": "Neighbourhood Regulars",
            "description": "Shop here out of proximity and habit. They know the layout, the staff, and what you carry. Losing them is slow and invisible -- they just start going somewhere else.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.6,
            "is_silent_majority": True,
            "age_range": "30-60",
            "income_tier": "mid",
            "engagement_label": "weekly",
            "key_decision_factors": ["proximity", "familiarity", "product availability", "staff friendliness"],
        },
        {
            "name": "Occasional Shoppers",
            "description": "Come in for specific needs a few times a year. They compare prices with Amazon before buying. Their loyalty depends entirely on whether you have what they need at a fair price.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.25,
            "is_silent_majority": True,
            "age_range": "25-50",
            "income_tier": "budget to mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["price competitiveness", "product selection", "convenience", "online comparison"],
        },
        {
            "name": "Brand Enthusiasts",
            "description": "Love the store experience and tell friends about it. They leave Google reviews, post on social media, and attend events. They define your brand image but are a tiny minority.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.85,
            "is_silent_majority": False,
            "age_range": "25-55",
            "income_tier": "mid to affluent",
            "engagement_label": "weekly",
            "key_decision_factors": ["store atmosphere", "curation", "staff expertise", "brand story"],
        },
        {
            "name": "Disgruntled Buyers",
            "description": "Had a bad return experience or received unhelpful service. Their negative review sits at the top of your Google listing, shaping first impressions for everyone who searches you.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": False,
            "age_range": "25-55",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["return policy", "staff attitude", "product quality", "feeling respected"],
        },
        {
            "name": "Impulse Visitors",
            "description": "Walked in because the window display caught their eye or they had time to kill. No pre-existing relationship. Unlikely to return unless something makes a strong impression.",
            "price_sensitivity": "low to moderate",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": True,
            "age_range": "18-50",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["visual appeal", "curiosity", "location", "in-store experience"],
        },
        {
            "name": "Deal Chasers",
            "description": "Only come during sales and clearance events. They are trained to wait for discounts and will not pay full price. Running more sales attracts more of them and fewer full-price buyers.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "20-45",
            "income_tier": "budget",
            "engagement_label": "seasonal",
            "key_decision_factors": ["sale events", "clearance prices", "coupons", "price comparison"],
        },
    ],

    # ------------------------------------------------------------------
    # HOSPITALITY -- hotels, hostels, B&Bs, tour operators, resorts
    # ------------------------------------------------------------------
    "hospitality": [
        {
            "name": "Returning Guests",
            "description": "Book the same property year after year. They are your most profitable segment because acquisition cost is zero. They notice changes -- a renovation excites them, a price jump worries them.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.7,
            "is_silent_majority": True,
            "age_range": "35-65",
            "income_tier": "mid to affluent",
            "engagement_label": "annual",
            "key_decision_factors": ["consistency", "familiarity", "location attachment", "loyalty rewards"],
        },
        {
            "name": "Platform-Dependent Bookers",
            "description": "Found you on Booking.com or Airbnb and picked you based on price and rating. No brand loyalty -- they will book a competitor next time if the algorithm ranks them higher.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.15,
            "is_silent_majority": True,
            "age_range": "25-50",
            "income_tier": "budget to mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["platform ranking", "price", "photos", "recent review score"],
        },
        {
            "name": "Enthusiastic Reviewers",
            "description": "Leave detailed positive reviews with photos. They had a great stay and want the world to know. Their testimonials drive bookings but set expectations you must consistently meet.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.6,
            "is_silent_majority": False,
            "age_range": "28-55",
            "income_tier": "mid to affluent",
            "engagement_label": "occasional",
            "key_decision_factors": ["experience quality", "unique touches", "staff warmth", "Instagram-worthiness"],
        },
        {
            "name": "Vocal Complainers",
            "description": "Something went wrong and they made sure everyone knows. Cleanliness, noise, or a rude interaction. One bad review at the top of your listing can cost dozens of bookings.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": False,
            "age_range": "30-60",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["cleanliness", "noise", "accuracy of listing", "staff responsiveness"],
        },
        {
            "name": "Business Travellers",
            "description": "Book for work, often on expense accounts. They care about Wi-Fi, location, and efficiency -- not charm. Loyal to chains or to properties near their client site, not to your brand.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "30-55",
            "income_tier": "affluent",
            "engagement_label": "occasional",
            "key_decision_factors": ["location", "Wi-Fi quality", "check-in speed", "work-friendly space"],
        },
        {
            "name": "Budget Travellers",
            "description": "Chose you because you were the cheapest acceptable option. They tolerate imperfections that a luxury traveller would not. A 10% price increase pushes them to the hostel down the road.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": True,
            "age_range": "18-35",
            "income_tier": "budget",
            "engagement_label": "one-time",
            "key_decision_factors": ["price", "safety", "location", "basic cleanliness"],
        },
    ],

    # ------------------------------------------------------------------
    # HEALTHCARE -- clinics, dental, veterinary, physiotherapy, optometry
    # ------------------------------------------------------------------
    "healthcare": [
        {
            "name": "Loyal Patients",
            "description": "Have been coming for years and trust the provider. They rarely leave reviews but will follow their doctor if they move practices. Losing one often means losing their entire family.",
            "price_sensitivity": "low to moderate",
            "loyalty_likelihood": 0.8,
            "is_silent_majority": True,
            "age_range": "35-70",
            "income_tier": "mid to affluent",
            "engagement_label": "regular",
            "key_decision_factors": ["trust in provider", "continuity of care", "staff familiarity", "outcomes"],
        },
        {
            "name": "Anxious Patients",
            "description": "Avoid appointments until the problem is urgent. Their anxiety means they are hyper-sensitive to wait times, bedside manner, and feeling rushed. A bad experience confirms their fear and they vanish.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "25-55",
            "income_tier": "mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["bedside manner", "wait time", "feeling heard", "pain management"],
        },
        {
            "name": "Grateful Advocates",
            "description": "Had a positive health outcome and credit the provider. They leave glowing reviews and refer friends. Their stories are powerful but represent the best-case scenario, not the average.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.85,
            "is_silent_majority": False,
            "age_range": "30-65",
            "income_tier": "mid to affluent",
            "engagement_label": "regular",
            "key_decision_factors": ["clinical outcome", "personal connection", "communication", "follow-up care"],
        },
        {
            "name": "Dissatisfied Patients",
            "description": "Felt dismissed, overcharged, or misdiagnosed. In healthcare, a negative review carries extra weight because prospective patients are already nervous. One bad story can override ten good ones.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": False,
            "age_range": "25-60",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["feeling dismissed", "billing surprise", "diagnosis accuracy", "wait time"],
        },
        {
            "name": "Insurance-Driven",
            "description": "Chose you because you are in-network. They have zero brand loyalty -- if their plan changes, they leave. They often do not know or care what things actually cost until the bill arrives.",
            "price_sensitivity": "low (until bill arrives)",
            "loyalty_likelihood": 0.2,
            "is_silent_majority": True,
            "age_range": "25-65",
            "income_tier": "mid",
            "engagement_label": "annual",
            "key_decision_factors": ["insurance network", "referral requirements", "location", "availability"],
        },
        {
            "name": "Price Shoppers",
            "description": "Uninsured or underinsured and comparing costs explicitly. They call ahead to ask prices and will drive further for a cheaper option. Transparent pricing wins them; surprise bills lose them forever.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.35,
            "is_silent_majority": True,
            "age_range": "22-50",
            "income_tier": "budget",
            "engagement_label": "as-needed",
            "key_decision_factors": ["upfront pricing", "payment plans", "cost transparency", "value for money"],
        },
    ],

    # ------------------------------------------------------------------
    # EDUCATION -- schools, tutoring centres, bootcamps, online courses
    # ------------------------------------------------------------------
    "education": [
        {
            "name": "Committed Learners",
            "description": "Enrolled with a clear goal and show up consistently. They finish courses and apply what they learn. Their retention is high but they expect tangible results -- a certificate, a job, a skill.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.65,
            "is_silent_majority": True,
            "age_range": "22-45",
            "income_tier": "mid",
            "engagement_label": "weekly",
            "key_decision_factors": ["curriculum quality", "career outcomes", "instructor expertise", "credentials"],
        },
        {
            "name": "Dabblers",
            "description": "Sign up on impulse and disengage within weeks. They bought the idea of learning but not the discipline. They represent a large share of enrolments and a small share of completions.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": True,
            "age_range": "20-40",
            "income_tier": "budget to mid",
            "engagement_label": "short-term",
            "key_decision_factors": ["ease of starting", "time commitment", "price", "perceived effort"],
        },
        {
            "name": "Success Stories",
            "description": "Got the outcome they wanted -- a job, a grade, a skill -- and tell everyone about it. They write testimonials and refer peers. Their stories are your marketing, but survivorship bias is real.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.8,
            "is_silent_majority": False,
            "age_range": "24-40",
            "income_tier": "mid to affluent",
            "engagement_label": "completed",
            "key_decision_factors": ["measurable outcome", "personal growth", "community", "instructor quality"],
        },
        {
            "name": "Disappointed Drop-outs",
            "description": "Expected more and got less. Felt the teaching was generic, the content outdated, or the promise oversold. Their negative reviews hit hard because prospective students read them carefully.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": False,
            "age_range": "22-45",
            "income_tier": "mid",
            "engagement_label": "dropped",
            "key_decision_factors": ["content relevance", "instructor quality", "pacing", "refund policy"],
        },
        {
            "name": "Parent Decision-Makers",
            "description": "Not the student but the one paying. They evaluate ROI differently -- is this worth it for their child? Price sensitivity is high because education competes with other family spending.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.5,
            "is_silent_majority": True,
            "age_range": "35-55",
            "income_tier": "mid",
            "engagement_label": "ongoing",
            "key_decision_factors": ["child's progress", "safety", "cost vs alternatives", "schedule flexibility"],
        },
        {
            "name": "Scholarship / Aid Seekers",
            "description": "Cannot afford full price and are actively looking for discounts, scholarships, or payment plans. They are motivated but price-constrained. Losing them means losing diversity in your student body.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.6,
            "is_silent_majority": True,
            "age_range": "18-35",
            "income_tier": "budget",
            "engagement_label": "term-based",
            "key_decision_factors": ["financial aid availability", "payment flexibility", "value for money", "opportunity cost"],
        },
    ],

    # ------------------------------------------------------------------
    # PROFESSIONAL SERVICES -- accounting, legal, consulting, design
    # ------------------------------------------------------------------
    "professional_services": [
        {
            "name": "Retained Clients",
            "description": "On a retainer or annual engagement. They are your stable revenue base and rarely shop around -- but they also rarely tell you when they are unhappy until they serve notice.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.75,
            "is_silent_majority": True,
            "age_range": "35-60",
            "income_tier": "mid to affluent",
            "engagement_label": "ongoing",
            "key_decision_factors": ["trust", "responsiveness", "expertise", "consistency"],
        },
        {
            "name": "Project-Based Clients",
            "description": "Hire you for a specific engagement and may or may not return. Each project is a new sales cycle. They compare proposals and your relationship resets to zero every time.",
            "price_sensitivity": "moderate to high",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "30-55",
            "income_tier": "mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["proposal quality", "timeline", "price", "relevant experience"],
        },
        {
            "name": "Referral Champions",
            "description": "Send you new clients and vouch for you publicly. They are your highest-ROI marketing channel. A single disappointed champion can cut off an entire referral pipeline.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.9,
            "is_silent_majority": False,
            "age_range": "35-60",
            "income_tier": "affluent",
            "engagement_label": "ongoing",
            "key_decision_factors": ["relationship depth", "results delivered", "professionalism", "reciprocity"],
        },
        {
            "name": "Unhappy Former Clients",
            "description": "Left because of a missed deadline, a billing dispute, or feeling ignored. In professional services, reputation spreads through word of mouth faster than through online reviews.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": False,
            "age_range": "30-55",
            "income_tier": "mid",
            "engagement_label": "former",
            "key_decision_factors": ["missed expectations", "communication breakdown", "billing transparency", "responsiveness"],
        },
        {
            "name": "First-Time Buyers",
            "description": "Never hired this type of professional before. They do not know what good looks like, so they rely heavily on credentials, reviews, and how the initial consultation feels.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.3,
            "is_silent_majority": True,
            "age_range": "28-50",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["credentials", "consultation experience", "clarity of process", "trustworthiness"],
        },
        {
            "name": "Fee-Sensitive Clients",
            "description": "Compare hourly rates and push for flat fees. They see professional services as a commodity and will switch for a 10% saving. They consume disproportionate negotiation time.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.2,
            "is_silent_majority": True,
            "age_range": "30-55",
            "income_tier": "budget to mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["hourly rate", "flat fee options", "scope clarity", "competitor quotes"],
        },
    ],

    # ------------------------------------------------------------------
    # ENTERTAINMENT -- cinemas, arcades, escape rooms, bowling, events
    # ------------------------------------------------------------------
    "entertainment": [
        {
            "name": "Regular Visitors",
            "description": "Come multiple times a month because it is part of their routine -- movie night, weekend bowling, arcade habit. They do not review, but they are your bread and butter.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.6,
            "is_silent_majority": True,
            "age_range": "18-45",
            "income_tier": "mid",
            "engagement_label": "weekly",
            "key_decision_factors": ["habit", "social routine", "convenience", "variety of offerings"],
        },
        {
            "name": "Occasional Fun-Seekers",
            "description": "Come for birthdays, special occasions, or when there is nothing else to do. They are price-aware and will pick the cheapest entertainment option that sounds fun enough.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.2,
            "is_silent_majority": True,
            "age_range": "20-40",
            "income_tier": "budget to mid",
            "engagement_label": "occasional",
            "key_decision_factors": ["price", "group suitability", "novelty", "reviews from friends"],
        },
        {
            "name": "Superfans",
            "description": "Follow you on social media, attend opening nights, and tell everyone about you. They leave detailed reviews and create user-generated content. They feel ownership over your brand.",
            "price_sensitivity": "low",
            "loyalty_likelihood": 0.85,
            "is_silent_majority": False,
            "age_range": "18-40",
            "income_tier": "mid",
            "engagement_label": "weekly",
            "key_decision_factors": ["novelty", "exclusivity", "community", "brand identity"],
        },
        {
            "name": "Bad-Experience Voices",
            "description": "Had a terrible time -- long wait, broken equipment, rude staff, dirty venue. They post about it immediately. In entertainment, one bad review kills the 'fun' expectation for future visitors.",
            "price_sensitivity": "moderate",
            "loyalty_likelihood": 0.05,
            "is_silent_majority": False,
            "age_range": "20-50",
            "income_tier": "mid",
            "engagement_label": "one-time",
            "key_decision_factors": ["cleanliness", "wait times", "staff attitude", "equipment quality"],
        },
        {
            "name": "Tourists and Visitors",
            "description": "In town for a limited time and looking for something to do tonight. They found you on Google Maps or TripAdvisor. They will never return but their review stays forever.",
            "price_sensitivity": "low to moderate",
            "loyalty_likelihood": 0.02,
            "is_silent_majority": True,
            "age_range": "20-55",
            "income_tier": "mid to affluent",
            "engagement_label": "one-time",
            "key_decision_factors": ["location", "ratings", "photos", "time availability"],
        },
        {
            "name": "Coupon Redeemers",
            "description": "Came because of a Groupon, voucher, or promotional deal. They would not have come at full price and likely will not return at full price. They fill capacity but dilute per-head revenue.",
            "price_sensitivity": "high",
            "loyalty_likelihood": 0.1,
            "is_silent_majority": True,
            "age_range": "20-40",
            "income_tier": "budget",
            "engagement_label": "one-time",
            "key_decision_factors": ["deal value", "price", "novelty", "social proof"],
        },
    ],
}


# ---------------------------------------------------------------------------
# Business type -> category mapping (80+ types)
# ---------------------------------------------------------------------------

BUSINESS_TYPE_TO_CATEGORY: dict[str, str] = {
    # physical_service (default catch-all for local service businesses)
    "restaurant": "physical_service",
    "cafe": "physical_service",
    "coffee shop": "physical_service",
    "bakery": "physical_service",
    "bar": "physical_service",
    "pub": "physical_service",
    "food truck": "physical_service",
    "catering": "physical_service",
    "barbershop": "physical_service",
    "barber": "physical_service",
    "hair salon": "physical_service",
    "salon": "physical_service",
    "hair_salon": "physical_service",
    "beauty salon": "physical_service",
    "nail salon": "physical_service",
    "spa": "physical_service",
    "massage": "physical_service",
    "tattoo parlor": "physical_service",
    "auto repair": "physical_service",
    "mechanic": "physical_service",
    "car wash": "physical_service",
    "dry cleaner": "physical_service",
    "laundromat": "physical_service",
    "pet grooming": "physical_service",
    "dog grooming": "physical_service",
    "florist": "physical_service",
    "photography studio": "physical_service",
    "printing shop": "physical_service",
    "tailor": "physical_service",
    "locksmith": "physical_service",
    "cleaning service": "physical_service",
    "pest control": "physical_service",
    "plumber": "physical_service",
    "electrician": "physical_service",
    "hvac": "physical_service",
    "landscaping": "physical_service",
    "moving company": "physical_service",
    "daycare": "physical_service",
    # Schema ID aliases (underscore format from survey_schema.yaml)
    "food_truck": "physical_service",
    "desserts": "physical_service",
    "nail_salon": "physical_service",
    "tattoo": "physical_service",
    "physio": "physical_service",
    "auto": "physical_service",
    "dry_cleaning": "physical_service",
    "photography": "physical_service",
    "printing": "physical_service",
    "cleaning": "physical_service",

    # saas
    "saas": "saas",
    "software": "saas",
    "app": "saas",
    "mobile app": "saas",
    "web app": "saas",
    "platform": "saas",
    "cloud service": "saas",
    "developer tools": "saas",
    "dev tools": "saas",
    "api service": "saas",
    "it_services": "saas",
    "web_design": "saas",
    "hosting": "saas",
    "cybersecurity": "saas",
    "data_analytics": "saas",
    "analytics platform": "saas",
    "crm": "saas",
    "erp": "saas",
    "project management": "saas",
    "productivity tool": "saas",

    # ecommerce
    "ecommerce": "ecommerce",
    "e-commerce": "ecommerce",
    "online store": "ecommerce",
    "online shop": "ecommerce",
    "marketplace": "ecommerce",
    "dtc": "ecommerce",
    "direct to consumer": "ecommerce",
    "dropshipping": "ecommerce",
    "online retail": "ecommerce",
    "webshop": "ecommerce",
    "etsy shop": "ecommerce",

    # b2b
    "b2b": "b2b",
    "consulting": "b2b",
    "logistics": "b2b",
    "freight": "b2b",
    "staffing": "b2b",
    "recruitment agency": "b2b",
    "manufacturing": "b2b",
    "wholesale": "b2b",
    "distributor": "b2b",
    "agency": "b2b",
    "marketing agency": "b2b",
    "advertising agency": "b2b",
    "it services": "b2b",
    "managed services": "b2b",
    "b2b_services": "b2b",
    "marketing_agency": "b2b",
    "freelance": "b2b",

    # subscription
    "gym": "subscription",
    "fitness studio": "subscription",
    "crossfit": "subscription",
    "yoga studio": "subscription",
    "yoga": "subscription",
    "pilates studio": "subscription",
    "streaming service": "subscription",
    "meal kit": "subscription",
    "subscription box": "subscription",
    "membership club": "subscription",
    "coworking space": "subscription",
    "wine club": "subscription",
    "book club": "subscription",

    # retail
    "retail": "retail",
    "store": "retail",
    "shop": "retail",
    "boutique": "retail",
    "bookstore": "retail",
    "hardware store": "retail",
    "pet store": "retail",
    "grocery store": "retail",
    "grocery": "retail",
    "supermarket": "retail",
    "convenience store": "retail",
    "pharmacy": "retail",
    "electronics store": "retail",
    "furniture store": "retail",
    "clothing store": "retail",
    "thrift store": "retail",
    "gift shop": "retail",
    "toy store": "retail",
    "clothing": "retail",
    "bookshop": "retail",
    "gift_shop": "retail",
    "sports": "retail",
    "electronics": "retail",
    "toy_shop": "retail",
    "pet_shop": "retail",
    "sporting goods": "retail",
    "garden center": "retail",
    "liquor store": "retail",
    "jewelry store": "retail",
    "optical shop": "retail",

    # hospitality
    "hotel": "hospitality",
    "hostel": "hospitality",
    "motel": "hospitality",
    "bed and breakfast": "hospitality",
    "b&b": "hospitality",
    "resort": "hospitality",
    "vacation rental": "hospitality",
    "airbnb": "hospitality",
    "tour operator": "hospitality",
    "travel agency": "hospitality",
    "campground": "hospitality",
    "campsite": "hospitality",
    "tour_operator": "hospitality",
    "activity_centre": "hospitality",
    "glamping": "hospitality",

    # healthcare
    "clinic": "healthcare",
    "dental": "healthcare",
    "dentist": "healthcare",
    "veterinary": "healthcare",
    "vet": "healthcare",
    "physiotherapy": "healthcare",
    "physical therapy": "healthcare",
    "chiropractor": "healthcare",
    "optometrist": "healthcare",
    "dermatologist": "healthcare",
    "therapist": "healthcare",
    "counselor": "healthcare",
    "psychologist": "healthcare",
    "psychiatrist": "healthcare",
    "urgent care": "healthcare",
    "medical practice": "healthcare",
    "hospital": "healthcare",
    "healthcare_clinic": "healthcare",

    # education
    "school": "education",
    "tutoring": "education",
    "tutor": "education",
    "bootcamp": "education",
    "coding bootcamp": "education",
    "online course": "education",
    "training center": "education",
    "driving school": "education",
    "language school": "education",
    "music school": "education",
    "dance school": "education",
    "martial arts": "education",
    "university": "education",
    "college": "education",
    "preschool": "education",
    "test prep": "education",
    "coaching": "education",
    "education": "education",
    "childcare": "education",
    "driving_school": "education",
    "tutoring": "education",
    "language_school": "education",
    "music_school": "education",
    "coding_bootcamp": "education",

    # professional_services
    "accounting": "professional_services",
    "accountant": "professional_services",
    "bookkeeping": "professional_services",
    "tax preparation": "professional_services",
    "law firm": "professional_services",
    "lawyer": "professional_services",
    "attorney": "professional_services",
    "legal services": "professional_services",
    "financial advisor": "professional_services",
    "financial planning": "professional_services",
    "insurance": "professional_services",
    "insurance agent": "professional_services",
    "legal": "professional_services",
    "accountant": "professional_services",
    "real estate": "professional_services",
    "real estate agent": "professional_services",
    "architecture firm": "professional_services",
    "architect": "professional_services",
    "interior design": "professional_services",
    "graphic design": "professional_services",
    "web design": "professional_services",
    "notary": "professional_services",
    "surveyor": "professional_services",

    # entertainment
    "cinema": "entertainment",
    "movie theater": "entertainment",
    "theater": "entertainment",
    "theatre": "entertainment",
    "arcade": "entertainment",
    "escape room": "entertainment",
    "bowling alley": "entertainment",
    "bowling": "entertainment",
    "trampoline park": "entertainment",
    "amusement park": "entertainment",
    "theme park": "entertainment",
    "zoo": "entertainment",
    "aquarium": "entertainment",
    "museum": "entertainment",
    "gallery": "entertainment",
    "nightclub": "entertainment",
    "comedy club": "entertainment",
    "concert venue": "entertainment",
    "event venue": "entertainment",
    "karaoke": "entertainment",
    "mini golf": "entertainment",
    "laser tag": "entertainment",
    "go kart": "entertainment",
    "water park": "entertainment",
    "playground": "entertainment",
    # Catch-all
    "other": "physical_service",
}


def _resolve_category(business_type: str) -> str:
    """Resolve a business type string to an industry category.

    Uses exact match first, then case-insensitive match, then substring
    matching against known types. Falls back to 'physical_service'.
    """
    if not business_type:
        return "physical_service"

    normalized = business_type.strip().lower()

    # Exact match
    if normalized in BUSINESS_TYPE_TO_CATEGORY:
        return BUSINESS_TYPE_TO_CATEGORY[normalized]

    # Substring match -- check if any known type is contained in the input
    # or if the input is contained in any known type
    for known_type, category in BUSINESS_TYPE_TO_CATEGORY.items():
        if known_type in normalized or normalized in known_type:
            return category

    logger.warning(
        "Unknown business type '%s' -- falling back to physical_service template",
        business_type,
    )
    return "physical_service"


def build_segments(
    adjusted: BiasAdjustedSignals,
    silent: SilentMajorityProfile,
    business: BusinessSnapshot,
    business_type: str | None = None,
) -> CustomerSegmentProfile:
    """Build customer segments from all available signals.

    Segment proportions are calibrated by review signals, demographics,
    and the silent majority estimate. They always sum to 1.0.

    Args:
        adjusted: Bias-corrected review signals.
        silent: Silent majority profile with proportion estimates.
        business: Snapshot of the business profile.
        business_type: Optional override. If not provided, uses business.type.
    """

    resolved_type = business_type or getattr(business, "type", "") or ""
    category = _resolve_category(resolved_type)
    template = INDUSTRY_SEGMENT_TEMPLATES[category]

    logger.info(
        "Building segments for category='%s' (resolved from type='%s')",
        category, resolved_type,
    )

    signals = adjusted.raw_signals
    tourist_ratio = signals.tourist_ratio_estimate

    # -------------------------------------------------------------------
    # Proportion calibration from review signals
    # -------------------------------------------------------------------
    # The template defines 6 segments in a fixed structural order:
    #   [0] silent_regular, [1] silent_occasional, [2] vocal_loyalist,
    #   [3] vocal_critic, [4] transient, [5] price_driven
    #
    # We calibrate proportions using the same signal-based logic regardless
    # of industry, then apply them to the industry-specific template.

    silent_prop = silent.recommended_swarm_proportion  # 0.55-0.70

    # Divide silent majority between the two silent segments
    silent_regular_prop = silent_prop * 0.45   # ~28% of total
    silent_occasional_prop = silent_prop * 0.55  # ~35% of total

    # Vocal segments (from review data)
    vocal_loyalist_prop = 0.05
    vocal_critic_prop = 0.03

    # Transient segment (from tourist/transient ratio estimate)
    transient_prop = min(tourist_ratio * 0.5, 0.25)  # Cap at 25%

    # Price-sensitive segment (from price mention frequency)
    price_driven_prop = 0.08
    if signals.price_mention_frequency > 0.5:
        price_driven_prop = 0.15
    elif signals.price_mention_frequency > 0.3:
        price_driven_prop = 0.12

    # Normalise to sum to 1.0
    raw_proportions = [
        silent_regular_prop,
        silent_occasional_prop,
        vocal_loyalist_prop,
        vocal_critic_prop,
        transient_prop,
        price_driven_prop,
    ]
    total = sum(raw_proportions)
    factor = 1.0 / total

    # -------------------------------------------------------------------
    # Build CustomerSegment instances from the template + proportions
    # -------------------------------------------------------------------
    segments = []
    for i, tmpl in enumerate(template):
        segments.append(
            CustomerSegment(
                name=tmpl["name"],
                description=tmpl["description"],
                estimated_proportion=round(raw_proportions[i] * factor, 3),
                price_sensitivity=tmpl["price_sensitivity"],
                loyalty_likelihood=tmpl["loyalty_likelihood"],
                is_silent_majority=tmpl["is_silent_majority"],
                age_range=tmpl["age_range"],
                income_tier=tmpl["income_tier"],
                visit_frequency=tmpl["engagement_label"],
                key_decision_factors=tmpl["key_decision_factors"],
            )
        )

    # -------------------------------------------------------------------
    # Derived metrics
    # -------------------------------------------------------------------
    dominant = max(segments, key=lambda s: s.estimated_proportion)
    most_price_sensitive = max(
        segments,
        key=lambda s: {
            "low": 1, "low to moderate": 2, "low (until bill arrives)": 2,
            "moderate": 3, "moderate to high": 4, "high": 5,
        }.get(s.price_sensitivity, 3)
    )

    silent_total = sum(
        s.estimated_proportion for s in segments if s.is_silent_majority
    )

    # -------------------------------------------------------------------
    # Plain-English summary (industry-aware)
    # -------------------------------------------------------------------
    summary_parts = [
        f"Most of your customers ({int(silent_total * 100)}%) never leave reviews or public feedback.",
    ]
    if tourist_ratio > 0.3:
        summary_parts.append(
            f"About {int(tourist_ratio * 100)}% of your reviewers appear to be "
            "one-time or transient customers."
        )
    if signals.price_mention_frequency > 0.2:
        summary_parts.append(
            "Price is mentioned frequently in your reviews -- your customers are watching."
        )
    summary = " ".join(summary_parts)

    signals_used = [
        "Google Reviews aggregate patterns",
        "bias correction (Karaman 2021, Han & Anderson 2026)",
    ]
    if business.customer_description:
        signals_used.append("business owner customer description")

    logger.info(
        "Segment profile built: %d segments, category=%s, silent_majority=%.0f%%, dominant=%s",
        len(segments), category, silent_total * 100, dominant.name,
    )

    return CustomerSegmentProfile(
        segments=segments,
        total_estimated_customers=f"~{adjusted.estimated_total_customers_yearly} per year",
        dominant_segment=dominant.name,
        most_price_sensitive_segment=most_price_sensitive.name,
        silent_majority_proportion=round(silent_total, 3),
        signals_used=signals_used,
        confidence_level=adjusted.overall_confidence,
        plain_english_summary=summary,
    )
