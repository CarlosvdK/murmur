"""
Psychological Profile Builder -- assembles a multi-layer behavioral profile
from survey data, Hofstede cultural dimensions, demographic research, and
industry-specific behavioral norms.

This profile flows into persona generation and interview prompts to ground
synthetic customers in research-backed behavioral patterns.

Works for ALL business types -- not industry-specific.
"""

import logging
from dataclasses import dataclass, field

from backend.models.business import BusinessSnapshot

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Industry behavioral norms
# ---------------------------------------------------------------------------

INDUSTRY_NORMS = {
    # -----------------------------------------------------------------------
    # FOOD & DRINK
    # -----------------------------------------------------------------------
    "restaurant": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency",
        "loyalty_driver": "habit_and_convenience",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Customers decide quickly, often based on mood and convenience. "
            "Regulars develop strong habits and resist change to their routine. "
            "Price increases are felt immediately because of high visit frequency."
        ),
    },
    "cafe": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency",
        "loyalty_driver": "habit_and_routine",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Coffee shop loyalty is routine-driven -- many customers visit daily, "
            "making even small price changes highly visible. The drink order becomes "
            "an identity marker; changing it feels personal. Atmosphere and Wi-Fi "
            "availability can matter as much as the product itself."
        ),
    },
    "bar": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "social_context",
        "loyalty_driver": "atmosphere_and_social_ties",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Bar customers are driven by social context more than product quality. "
            "The crowd, music, and vibe determine repeat visits. Price sensitivity "
            "drops significantly in social settings where rounds are bought. Regulars "
            "form strong emotional attachment to 'their' spot."
        ),
    },
    "bakery": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "low",
        "price_sensitivity_driver": "frequency_and_treat_framing",
        "loyalty_driver": "product_quality_and_nostalgia",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Bakery purchases are often framed as small treats, which reduces price "
            "sensitivity per visit. Customers develop deep attachment to specific "
            "items and react strongly if a favorite is removed or changed. Word of "
            "mouth from bringing items to gatherings is a major growth driver."
        ),
    },
    "food_truck": {
        "engagement_model": "per_visit",
        "decision_speed": "very_fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "convenience_and_novelty",
        "loyalty_driver": "location_and_uniqueness",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Food truck customers are opportunity-driven -- they buy because the truck "
            "is there, not because they planned to. Location consistency builds a "
            "following. Social media is disproportionately important for communicating "
            "where the truck will be. Menu simplicity is a feature, not a limitation."
        ),
    },
    "catering": {
        "engagement_model": "per_project",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "budget_and_occasion",
        "loyalty_driver": "reliability_and_past_experience",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Catering decisions carry high social risk -- the buyer's reputation is "
            "on the line at the event. This makes past positive experience the "
            "strongest loyalty factor. Price is evaluated against the total event "
            "budget, not in isolation. Referrals from trusted contacts drive most "
            "new business."
        ),
    },
    "desserts": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "indulgence_framing",
        "loyalty_driver": "product_uniqueness",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Dessert purchases are self-justified as rewards or indulgences, which "
            "suppresses normal price sensitivity. Instagram-worthy presentation drives "
            "trial visits. Customers are novelty-seeking but will return repeatedly "
            "for a signature item they cannot get elsewhere."
        ),
    },
    "fast_food": {
        "engagement_model": "per_visit",
        "decision_speed": "very_fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "value_meal_anchoring",
        "loyalty_driver": "speed_and_consistency",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Fast food customers prioritize speed and predictability above all else. "
            "They are extremely price-anchored to existing value meals and combo "
            "prices. Even small perceived slowdowns in service can trigger switching. "
            "Loyalty apps with deals are effective because this audience is "
            "deal-motivated."
        ),
    },
    "fine_dining": {
        "engagement_model": "per_visit",
        "decision_speed": "slow",
        "switching_cost": "low",
        "price_sensitivity_driver": "occasion_and_status",
        "loyalty_driver": "experience_and_prestige",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Fine dining is occasion-driven, not habitual. Customers research "
            "extensively before booking and price sensitivity is low because the "
            "visit is a planned splurge. Reviews and awards heavily influence "
            "first visits. Consistency of excellence determines repeat patronage, "
            "but visits are infrequent by nature."
        ),
    },
    "juice_bar": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "health_value_framing",
        "loyalty_driver": "health_identity_and_habit",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Juice bar customers frame purchases as health investments, which "
            "supports premium pricing. Loyalty is tied to a health-conscious "
            "identity rather than the product alone. Seasonal ingredient changes "
            "are expected and welcomed. Proximity to gyms or yoga studios creates "
            "natural customer pipelines."
        ),
    },
    # -----------------------------------------------------------------------
    # HEALTH & PERSONAL CARE
    # -----------------------------------------------------------------------
    "barbershop": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "relationship",
        "loyalty_driver": "trust_and_skill",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Personal service creates moderate switching costs. Customers value the "
            "relationship with their barber and the social experience of the visit. "
            "Trust takes time to build and is not easily replaced. Many customers "
            "will follow a specific barber if they move to a new shop."
        ),
    },
    "hair_salon": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "relationship",
        "loyalty_driver": "trust_and_skill",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "High-trust relationship where the stakes feel personal -- a bad haircut "
            "is visible to everyone. Customers are reluctant to switch because "
            "finding a stylist who understands their hair type and preferences takes "
            "multiple visits. Price increases are tolerated more here than in almost "
            "any other per-visit business."
        ),
    },
    "nail_salon": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "frequency_and_comparison",
        "loyalty_driver": "consistency_and_hygiene",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Nail salon customers visit on a regular cycle (every 2-4 weeks), making "
            "them sensitive to cumulative costs. Hygiene perception is a deal-breaker "
            "-- one concern about cleanliness will cause permanent loss. Convenience "
            "of booking and wait times matter more than ambiance."
        ),
    },
    "spa": {
        "engagement_model": "per_session",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "luxury_framing",
        "loyalty_driver": "experience_and_results",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Spa visits are framed as self-care or rewards, reducing price sensitivity. "
            "Customers evaluate the full sensory experience -- ambiance, music, scent "
            "-- not just the treatment outcome. Gift cards drive significant first-time "
            "traffic. Membership models work when positioned as ongoing wellness."
        ),
    },
    "tattoo": {
        "engagement_model": "per_project",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "permanence_and_artistry",
        "loyalty_driver": "artistic_trust",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "The permanent nature of tattoos makes this one of the highest-trust "
            "purchase decisions. Customers research artists extensively through "
            "portfolios and social media. Price is secondary to artistic style match. "
            "Once a client trusts an artist, they will wait weeks for an appointment "
            "rather than go elsewhere."
        ),
    },
    "gym": {
        "engagement_model": "membership",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "perceived_value",
        "loyalty_driver": "habit_and_community",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Subscription model means customers evaluate value monthly but inertia "
            "is strong -- many members pay without attending. High initial motivation "
            "often declines. Community, class schedules, and convenience drive "
            "retention more than equipment quality. January and September see "
            "predictable sign-up surges."
        ),
    },
    "yoga": {
        "engagement_model": "membership_or_class_pack",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "perceived_wellness_value",
        "loyalty_driver": "instructor_attachment_and_community",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Yoga students form strong attachments to specific instructors and "
            "will follow them between studios. The community aspect creates social "
            "switching costs that pure fitness gyms lack. Class schedule alignment "
            "with personal routine is the top practical driver. Premium pricing "
            "is accepted when the space and instruction feel intentional."
        ),
    },
    "personal_trainer": {
        "engagement_model": "recurring_sessions",
        "decision_speed": "moderate",
        "switching_cost": "high",
        "price_sensitivity_driver": "results_and_accountability",
        "loyalty_driver": "personal_relationship_and_results",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "The trainer-client relationship is deeply personal -- the trainer knows "
            "the client's body, limitations, and goals. This creates very high "
            "switching costs. Clients often continue paying even during low-motivation "
            "periods because the accountability itself is the product. Referrals from "
            "visible client transformations drive new business."
        ),
    },
    "meditation_studio": {
        "engagement_model": "membership_or_class_pack",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "spiritual_value_framing",
        "loyalty_driver": "teacher_and_community",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Meditation studio customers are on a personal growth journey and are "
            "willing to pay premium prices when the practice feels transformative. "
            "Competition from free apps is real but in-person community is the "
            "differentiator. Drop-off rates are high in the first month; those who "
            "stay beyond 90 days become very loyal."
        ),
    },
    "physio": {
        "engagement_model": "per_session",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "insurance_and_pain",
        "loyalty_driver": "trust_and_treatment_continuity",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Physiotherapy patients are in pain, which creates urgency but also "
            "makes them vulnerable and trust-dependent. Continuity of care matters "
            "because the therapist understands their injury history. Insurance "
            "coverage dramatically affects price sensitivity. Patients who see "
            "results become strong referral sources."
        ),
    },
    "chiropractor": {
        "engagement_model": "recurring_sessions",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_belief",
        "loyalty_driver": "perceived_effectiveness_and_trust",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Chiropractic patients often commit to ongoing treatment plans, creating "
            "recurring revenue patterns. Belief in the treatment approach is a "
            "prerequisite -- skeptics will not convert. Once a patient attributes "
            "relief to their chiropractor, loyalty is very strong. Insurance "
            "coverage and plan limits shape visit frequency."
        ),
    },
    # -----------------------------------------------------------------------
    # RETAIL
    # -----------------------------------------------------------------------
    "grocery": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency_and_basket",
        "loyalty_driver": "convenience_and_price",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Grocery shopping is habitual and location-driven. Customers are very "
            "price-aware on staple items they buy weekly but less so on occasional "
            "treats. Store layout familiarity creates a subtle switching cost -- "
            "customers dislike relearning where things are."
        ),
    },
    "clothing": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "brand_and_style",
        "loyalty_driver": "brand_identity",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Fashion purchases are emotionally driven and tied to self-image. Brand "
            "loyalty exists but customers are always open to alternatives. Sales and "
            "promotions drive significant behavior changes. Sizing consistency across "
            "visits builds quiet loyalty that customers rarely articulate."
        ),
    },
    "bookshop": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "online_comparison",
        "loyalty_driver": "curation_and_community",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Independent bookshops compete against online giants on experience, not "
            "price. Customers who shop here are making a values-based choice to "
            "support local. Staff recommendations and curated selections are the "
            "core differentiator. Events and author signings build community loyalty "
            "that transcends transactional relationships."
        ),
    },
    "gift_shop": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "occasion_and_uniqueness",
        "loyalty_driver": "product_uniqueness_and_convenience",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Gift shop purchases are occasion-driven and often last-minute, which "
            "reduces price sensitivity because the buyer is solving an urgent need. "
            "Unique, hard-to-find items justify premium pricing. Repeat customers "
            "return when they trust the shop will have something appropriate for "
            "any occasion."
        ),
    },
    "florist": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "occasion_and_emotion",
        "loyalty_driver": "quality_and_reliability",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Floral purchases are emotionally loaded -- the buyer is expressing love, "
            "grief, celebration, or apology. This emotional context suppresses price "
            "sensitivity. Reliability for delivery (especially for events) builds "
            "strong loyalty. One failed delivery on an important occasion causes "
            "permanent loss."
        ),
    },
    "electronics": {
        "engagement_model": "per_transaction",
        "decision_speed": "slow",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "comparison_and_specs",
        "loyalty_driver": "expertise_and_after_sales",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Electronics buyers research extensively online before purchasing. Price "
            "comparison is effortless and expected. Small retailers compete on "
            "in-person expertise, honest recommendations, and after-sales support. "
            "Customers who feel they were given trustworthy advice become vocal "
            "advocates."
        ),
    },
    "pet_shop": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "emotional_bond_with_pet",
        "loyalty_driver": "product_trust_and_pet_knowledge",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Pet owners spend emotionally, not rationally -- they will pay premium "
            "prices for anything perceived as better for their animal. Staff who "
            "remember pet names and dietary needs build outsized loyalty. Subscription "
            "models for recurring supplies (food, litter) are highly effective once "
            "established."
        ),
    },
    "furniture": {
        "engagement_model": "per_transaction",
        "decision_speed": "slow",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "budget_and_longevity",
        "loyalty_driver": "quality_and_delivery_experience",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Furniture purchases are infrequent and high-consideration. Customers "
            "spend weeks or months deciding. The in-store experience (seeing and "
            "touching) remains critical despite online competition. Delivery and "
            "assembly experience shapes the lasting impression more than the sales "
            "interaction."
        ),
    },
    "jewelry": {
        "engagement_model": "per_transaction",
        "decision_speed": "slow",
        "switching_cost": "low",
        "price_sensitivity_driver": "occasion_and_perceived_value",
        "loyalty_driver": "trust_and_craftsmanship",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Jewelry purchases are high-emotion, high-stakes decisions often tied "
            "to milestones (engagement, anniversary, graduation). Trust in quality "
            "and fair pricing is paramount because most buyers cannot independently "
            "assess gemstone or metal value. A positive experience creates lifetime "
            "loyalty for all future milestone purchases."
        ),
    },
    "thrift_store": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "treasure_hunt_mentality",
        "loyalty_driver": "inventory_turnover_and_values",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Thrift shoppers are motivated by the thrill of unexpected finds, not "
            "specific product needs. Frequent inventory turnover is essential -- "
            "customers stop coming if they see the same items repeatedly. Many "
            "customers are values-driven (sustainability, anti-consumerism) and this "
            "identity reinforces loyalty to the concept, not just the store."
        ),
    },
    "hardware": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "project_budget",
        "loyalty_driver": "expertise_and_inventory_depth",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Hardware store customers often arrive mid-project with an urgent, "
            "specific need. Staff expertise in helping solve problems is the primary "
            "differentiator against big-box stores. Having the obscure part in stock "
            "when the customer needs it creates disproportionate loyalty. Weekend "
            "warriors and contractors have completely different needs and behaviors."
        ),
    },
    "pharmacy": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_necessity",
        "loyalty_driver": "convenience_and_pharmacist_trust",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Pharmacy customers are tied by prescription transfers, which create a "
            "moderate switching cost. Convenience (location, hours, drive-through) "
            "is the top loyalty driver. Trust in the pharmacist for advice on "
            "over-the-counter products supplements the doctor relationship. Insurance "
            "network membership can force or prevent switching entirely."
        ),
    },
    "optical": {
        "engagement_model": "per_visit",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_frame_cost",
        "loyalty_driver": "exam_quality_and_selection",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Optical customers visit infrequently (every 1-2 years) but spend "
            "significantly per visit. Insurance coverage heavily determines where "
            "they go. The combination of clinical exam quality and frame selection "
            "is unique to this industry. Online frame competitors are a growing "
            "threat for the retail side but not the clinical side."
        ),
    },
    "shoe_store": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "style_and_season",
        "loyalty_driver": "fit_expertise_and_selection",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Shoe purchases bridge fashion and function. Customers who find a store "
            "that consistently stocks their size and width develop quiet loyalty. "
            "The try-on experience remains a significant advantage over online. "
            "Seasonal buying patterns (back-to-school, spring) create predictable "
            "traffic surges."
        ),
    },
    "sports": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "performance_needs_and_budget",
        "loyalty_driver": "expertise_and_brand_selection",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Sports equipment buyers range from casual to serious athletes with "
            "very different price tolerances. Knowledgeable staff who can recommend "
            "appropriate gear for skill level build strong loyalty. Seasonal sports "
            "create cyclical demand. Team and league affiliations drive bulk "
            "purchasing opportunities."
        ),
    },
    "toy_shop": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "gift_occasion_and_child_demand",
        "loyalty_driver": "curation_and_experience",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Toy shop purchases are driven by two different buyers: children who "
            "want everything and adults who want appropriate, quality gifts. The "
            "in-store play experience is the core differentiator against online. "
            "Birthday party seasons and holidays create extreme demand spikes. "
            "Staff who can recommend age-appropriate items earn parental trust."
        ),
    },
    # -----------------------------------------------------------------------
    # SERVICES
    # -----------------------------------------------------------------------
    "auto": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "trust_and_necessity",
        "loyalty_driver": "honesty_and_competence",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Auto repair is a trust-critical industry because most customers cannot "
            "verify the work independently. Fear of being overcharged or sold "
            "unnecessary repairs is the dominant emotion. A mechanic who explains "
            "clearly and charges fairly earns fierce, long-term loyalty. Customers "
            "will drive past closer shops to reach a trusted mechanic."
        ),
    },
    "dry_cleaning": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "low",
        "price_sensitivity_driver": "frequency_and_convenience",
        "loyalty_driver": "convenience_and_reliability",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Dry cleaning is a purely functional purchase driven by convenience "
            "and proximity. Quality is expected as baseline -- customers only notice "
            "it when something goes wrong. Damaging a garment is catastrophic for "
            "loyalty. Pick-up and delivery services can dramatically shift the "
            "competitive landscape."
        ),
    },
    "photography": {
        "engagement_model": "per_project",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "occasion_importance",
        "loyalty_driver": "portfolio_and_personal_connection",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Photography clients hire for irreplaceable moments (weddings, births, "
            "senior portraits). The stakes are high because the moment cannot be "
            "recreated if the photographer fails. Portfolio style must match client "
            "taste. Personal rapport during the shoot determines satisfaction as "
            "much as the final images."
        ),
    },
    "printing": {
        "engagement_model": "per_transaction",
        "decision_speed": "fast",
        "switching_cost": "low",
        "price_sensitivity_driver": "volume_and_deadline",
        "loyalty_driver": "turnaround_speed_and_quality",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Print shop customers often arrive under deadline pressure, which "
            "reduces price sensitivity. Meeting deadlines reliably is the single "
            "strongest loyalty driver. Small business clients who find a reliable "
            "printer stop comparison shopping entirely. Color accuracy and finishing "
            "quality matter to a subset of customers who will pay significantly more."
        ),
    },
    "accountant": {
        "engagement_model": "recurring",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "complexity_and_trust",
        "loyalty_driver": "trust_and_proactive_advice",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Accountants hold sensitive financial information, creating high switching "
            "costs. Clients value proactive advice that saves them money, not just "
            "compliance work. The relationship often begins at tax season but deepens "
            "into year-round advisory. Clients rarely switch unless they feel "
            "neglected or discover a costly error."
        ),
    },
    "legal": {
        "engagement_model": "per_project_or_retainer",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "stakes_and_specialization",
        "loyalty_driver": "trust_and_competence",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Legal clients are buying peace of mind during stressful situations. "
            "Specialization matters enormously -- a great divorce lawyer is useless "
            "for a business contract. Communication responsiveness is the most "
            "common complaint in the industry. Clients who feel their lawyer is "
            "genuinely invested in their outcome become lifelong referral sources."
        ),
    },
    "consulting": {
        "engagement_model": "per_project_or_retainer",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "expertise_value",
        "loyalty_driver": "trust_and_results",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Consulting relationships are built on trust and track record. Clients "
            "are reluctant to switch because onboarding a new consultant requires "
            "sharing institutional context that took time to build. Price is "
            "secondary to demonstrated expertise. Results attribution is often "
            "ambiguous, making relationship quality the true retention driver."
        ),
    },
    "freelance": {
        "engagement_model": "per_project",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "budget_and_perceived_skill",
        "loyalty_driver": "reliability_and_communication",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Freelance clients value reliability above raw talent -- delivering on "
            "time and communicating proactively creates outsized loyalty. The market "
            "is perceived as risky by clients who have been burned by no-shows or "
            "missed deadlines. Portfolio and referrals are essential for winning "
            "initial trust. Scope creep is the most common source of friction."
        ),
    },
    "marketing_agency": {
        "engagement_model": "retainer",
        "decision_speed": "slow",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "roi_measurement",
        "loyalty_driver": "measurable_results_and_proactivity",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Marketing agency clients struggle to attribute results, making the "
            "relationship vulnerable to budget cuts during downturns. Agencies that "
            "proactively report on metrics and propose new ideas retain clients longer. "
            "The onboarding cost of teaching a new agency about the brand creates "
            "meaningful switching friction."
        ),
    },
    "cleaning": {
        "engagement_model": "recurring",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "frequency_and_scope",
        "loyalty_driver": "trust_and_consistency",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Cleaning service customers let providers into their private spaces, "
            "making trust the foundation of the relationship. Consistency of quality "
            "across visits matters more than one exceptional clean. Customers are "
            "reluctant to search for replacements because vetting someone new for "
            "trustworthiness is effortful and uncomfortable."
        ),
    },
    "tutoring": {
        "engagement_model": "recurring_sessions",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "child_outcomes",
        "loyalty_driver": "student_rapport_and_results",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Parents are buying outcomes for their children, which makes them less "
            "price-sensitive than the dollar amount suggests. The tutor-student "
            "rapport takes time to build and is the primary switching cost. Results "
            "are often delayed (next test, next report card), requiring trust during "
            "the interim. Word of mouth from other parents is the dominant "
            "acquisition channel."
        ),
    },
    "plumbing": {
        "engagement_model": "per_project",
        "decision_speed": "fast_when_urgent",
        "switching_cost": "low",
        "price_sensitivity_driver": "urgency_and_comparison",
        "loyalty_driver": "responsiveness_and_fairness",
        "typical_decision_style": "urgent_or_deliberate",
        "key_behavioral_note": (
            "Plumbing customers fall into two categories: emergency (pipe burst, no "
            "hot water) and planned (renovation, upgrade). Emergency customers will "
            "pay almost anything for immediate response. Planned customers compare "
            "multiple quotes. A plumber who is honest about pricing and shows up "
            "when promised earns a permanent spot in the customer's contact list."
        ),
    },
    "electrical": {
        "engagement_model": "per_project",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "project_scope_and_safety",
        "loyalty_driver": "competence_and_trustworthiness",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Electrical work carries safety implications that make customers "
            "prioritize licensed, insured professionals over price. Customers cannot "
            "verify quality of work hidden in walls, so trust in the electrician's "
            "integrity is paramount. Repeat business comes from the same homeowners "
            "over decades as their property needs evolve."
        ),
    },
    "landscaping": {
        "engagement_model": "recurring",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "neighborhood_comparison",
        "loyalty_driver": "reliability_and_visual_results",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Landscaping results are visible to neighbors, adding social pressure "
            "to the purchase decision. Reliability of showing up on schedule matters "
            "as much as the quality of work. Seasonal contracts create natural "
            "retention. Customers compare their yard to neighbors', making "
            "neighborhood density a growth lever."
        ),
    },
    "pest_control": {
        "engagement_model": "per_visit_or_contract",
        "decision_speed": "fast_when_urgent",
        "switching_cost": "low",
        "price_sensitivity_driver": "urgency_and_disgust",
        "loyalty_driver": "effectiveness_and_prevention",
        "typical_decision_style": "urgent",
        "key_behavioral_note": (
            "Pest control customers are often in a state of distress and will pay "
            "premium prices for immediate resolution. The emotional reaction "
            "(disgust, fear, embarrassment) overrides normal price sensitivity. "
            "Converting one-time emergency calls into preventive contracts is the "
            "key business model challenge. Discretion matters -- customers do not "
            "want neighbors to know."
        ),
    },
    "moving_company": {
        "engagement_model": "per_project",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "quote_comparison",
        "loyalty_driver": "care_and_punctuality",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Moving is one of the most stressful life events, and customers entrust "
            "all their possessions to the company. Damage to belongings during the "
            "move creates intense negative reactions. Most customers only need the "
            "service once every few years, making referrals the primary growth "
            "channel. Online reviews carry exceptional weight in this industry."
        ),
    },
    "insurance": {
        "engagement_model": "recurring",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "annual_premium_comparison",
        "loyalty_driver": "claims_experience_and_agent_trust",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Insurance is a grudge purchase -- customers resent paying for something "
            "they hope never to use. Loyalty is tested at the single moment that "
            "matters: the claims experience. Agents who maintain personal "
            "relationships and proactively review coverage build retention that "
            "online-only competitors cannot match."
        ),
    },
    "financial_advisor": {
        "engagement_model": "recurring",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "wealth_level_and_fee_transparency",
        "loyalty_driver": "trust_and_perceived_competence",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Financial advisory relationships involve sharing intimate details about "
            "wealth, goals, and fears. This creates very high switching costs rooted "
            "in emotional vulnerability, not just account transfer logistics. Clients "
            "evaluate their advisor during market downturns -- those who communicate "
            "calmly and proactively during crises retain clients for decades."
        ),
    },
    "real_estate": {
        "engagement_model": "per_transaction",
        "decision_speed": "slow",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "commission_and_outcome",
        "loyalty_driver": "market_knowledge_and_responsiveness",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Real estate transactions are the largest financial decisions most people "
            "make. Clients expect near-constant availability and responsiveness. "
            "The agent's local market knowledge and negotiation skills are the "
            "perceived value. Transactions are infrequent, so referrals and repeat "
            "business from the same client years later are the growth model."
        ),
    },
    # -----------------------------------------------------------------------
    # TECHNOLOGY
    # -----------------------------------------------------------------------
    "saas": {
        "engagement_model": "subscription",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "roi_and_alternatives",
        "loyalty_driver": "integration_and_workflow",
        "typical_decision_style": "deliberate_committee",
        "key_behavioral_note": (
            "Software decisions involve evaluating ROI, integration effort, and "
            "team adoption. Switching costs are high due to data migration and "
            "workflow disruption. Price sensitivity is measured against value "
            "delivered, not absolute cost. Decisions may involve multiple "
            "stakeholders and trial periods are expected."
        ),
    },
    "ecommerce": {
        "engagement_model": "per_transaction",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "comparison_shopping",
        "loyalty_driver": "experience_and_trust",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Online shoppers compare prices instantly across competitors. Loyalty "
            "is driven by trust, delivery speed, and return policies. Impulse "
            "purchases are common but cart abandonment is high. Email and retargeting "
            "recover significant revenue that would otherwise be lost."
        ),
    },
    "app": {
        "engagement_model": "subscription_or_freemium",
        "decision_speed": "fast",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "perceived_value",
        "loyalty_driver": "habit_and_data_lock_in",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "App users decide in seconds whether to continue or uninstall. Free "
            "alternatives are always one search away. Habit formation in the first "
            "week is critical for retention. Data stored in the app (history, "
            "preferences, content) creates moderate switching costs over time."
        ),
    },
    "it_services": {
        "engagement_model": "contract_or_retainer",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "downtime_cost",
        "loyalty_driver": "reliability_and_response_time",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "IT service clients measure value by uptime and response speed during "
            "outages. The provider accumulates deep knowledge of the client's systems, "
            "creating high switching costs. Proactive monitoring and preventing issues "
            "before they occur is valued more than reactive fix speed. Trust with "
            "sensitive data access is foundational."
        ),
    },
    "web_design": {
        "engagement_model": "per_project",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "scope_and_comparison",
        "loyalty_driver": "design_quality_and_communication",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Web design clients often struggle to articulate what they want, making "
            "communication and iterative process management as important as design "
            "skill. Clients compare portfolios extensively before choosing. Ongoing "
            "maintenance creates recurring revenue but is often undervalued by clients "
            "until something breaks."
        ),
    },
    "hosting": {
        "engagement_model": "subscription",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "usage_and_alternatives",
        "loyalty_driver": "uptime_and_support",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Hosting customers tolerate moderate prices as long as uptime is "
            "near-perfect. Migration to a new host is technically complex, creating "
            "real switching costs. Support quality during emergencies determines "
            "loyalty. Most customers only evaluate alternatives after experiencing "
            "a significant outage or billing surprise."
        ),
    },
    "cybersecurity": {
        "engagement_model": "contract_or_subscription",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "risk_and_compliance",
        "loyalty_driver": "expertise_and_incident_response",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "Cybersecurity purchases are driven by fear of breach and compliance "
            "requirements, not aspirational benefits. Clients struggle to evaluate "
            "quality because the best outcome is nothing happening. A single "
            "successful incident response can cement a relationship for years. "
            "Regulatory changes drive purchasing cycles."
        ),
    },
    "data_analytics": {
        "engagement_model": "subscription_or_project",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "roi_and_data_dependency",
        "loyalty_driver": "integration_depth_and_insights_quality",
        "typical_decision_style": "deliberate_committee",
        "key_behavioral_note": (
            "Analytics platforms become embedded in decision-making processes, "
            "creating very high switching costs. Historical data and custom "
            "dashboards make migration painful. Clients evaluate based on whether "
            "the tool actually changed decisions, not just produced reports. "
            "Onboarding complexity means churn is concentrated in the first 90 days."
        ),
    },
    # -----------------------------------------------------------------------
    # B2B
    # -----------------------------------------------------------------------
    "b2b_services": {
        "engagement_model": "contract",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "budget_and_roi",
        "loyalty_driver": "relationship_and_reliability",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "B2B decisions involve procurement processes, budget approvals, and "
            "multiple decision-makers. Relationships matter enormously. Switching "
            "requires re-evaluating vendors, which is time-consuming and risky. "
            "Price is evaluated against business impact, not personal budget."
        ),
    },
    "logistics": {
        "engagement_model": "contract",
        "decision_speed": "slow",
        "switching_cost": "very_high",
        "price_sensitivity_driver": "total_cost_of_operations",
        "loyalty_driver": "reliability_and_integration",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "Logistics decisions are operational and affect the entire supply chain. "
            "Switching providers is extremely disruptive and risks service gaps. "
            "Reliability and on-time delivery matter more than price. Contracts "
            "are long-term and renegotiated rather than replaced."
        ),
    },
    "wholesale": {
        "engagement_model": "contract_or_recurring",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "margin_pressure",
        "loyalty_driver": "reliability_and_terms",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Wholesale buyers are margin-conscious and compare prices actively "
            "but value reliable supply and favorable payment terms. Minimum order "
            "quantities and credit terms create relationship stickiness. Stockouts "
            "from a supplier cause disproportionate damage because the buyer's own "
            "customers are affected."
        ),
    },
    "manufacturing": {
        "engagement_model": "contract",
        "decision_speed": "slow",
        "switching_cost": "very_high",
        "price_sensitivity_driver": "unit_cost_and_volume",
        "loyalty_driver": "quality_consistency_and_capacity",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "Manufacturing partnerships involve tooling investments, quality "
            "certifications, and supply chain integration that make switching "
            "extremely expensive. Consistent quality across large production runs "
            "is the fundamental expectation. Communication about delays or issues "
            "is valued nearly as much as preventing them."
        ),
    },
    "staffing": {
        "engagement_model": "contract_or_per_placement",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "margin_and_quality_of_candidates",
        "loyalty_driver": "candidate_quality_and_fill_speed",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Staffing clients measure value by the quality and retention of placed "
            "candidates. A single bad placement damages trust significantly. Fill "
            "speed matters because open positions cost money daily. Clients develop "
            "loyalty to specific recruiters who understand their culture and needs "
            "rather than to the staffing firm itself."
        ),
    },
    "commercial_cleaning": {
        "engagement_model": "contract",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "square_footage_and_budget",
        "loyalty_driver": "consistency_and_trustworthiness",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Commercial cleaning contracts are won on price but retained on "
            "consistency. After-hours access to facilities requires trust. Cleaning "
            "quality is only noticed when it drops -- invisible when done well. "
            "Contract renewal decisions often come down to whether any complaints "
            "were received during the term."
        ),
    },
    "fleet_management": {
        "engagement_model": "contract",
        "decision_speed": "slow",
        "switching_cost": "very_high",
        "price_sensitivity_driver": "total_cost_of_ownership",
        "loyalty_driver": "system_integration_and_uptime",
        "typical_decision_style": "committee",
        "key_behavioral_note": (
            "Fleet management solutions integrate with operations, GPS, maintenance "
            "schedules, and compliance systems. Switching requires retraining drivers "
            "and staff, migrating vehicle data, and risking operational disruption. "
            "Clients evaluate total cost of ownership over multi-year periods. "
            "Downtime in tracking systems has immediate operational consequences."
        ),
    },
    # -----------------------------------------------------------------------
    # HOSPITALITY
    # -----------------------------------------------------------------------
    "hotel": {
        "engagement_model": "per_stay",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "comparison_and_occasion",
        "loyalty_driver": "loyalty_program_and_experience",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Hotel guests compare prices across platforms effortlessly. Loyalty "
            "programs create some stickiness but most guests prioritize price and "
            "location. Business travelers are less price-sensitive than leisure "
            "travelers but more demanding about consistency and amenities."
        ),
    },
    "hostel": {
        "engagement_model": "per_stay",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "budget_constraint",
        "loyalty_driver": "social_atmosphere_and_cleanliness",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Hostel guests are overwhelmingly price-driven and comparison shop "
            "aggressively. The social atmosphere and common areas differentiate "
            "beyond price. Cleanliness and safety are baseline expectations that, "
            "if unmet, generate devastating online reviews. Repeat business is "
            "rare since guests are typically traveling, but recommendations to "
            "other travelers are the growth engine."
        ),
    },
    "campsite": {
        "engagement_model": "per_stay",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "seasonal_and_amenity_based",
        "loyalty_driver": "natural_setting_and_facilities",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Campsite guests are drawn by location and natural surroundings, which "
            "cannot be replicated by competitors. Facilities (showers, electricity, "
            "Wi-Fi) are increasingly expected. Families who find a campsite they love "
            "return annually, creating reliable repeat business. Weather and season "
            "dominate demand patterns."
        ),
    },
    "tour_operator": {
        "engagement_model": "per_booking",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "trip_budget_and_comparison",
        "loyalty_driver": "guide_quality_and_unique_experiences",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Tour customers are buying memories, not logistics. The guide's personality "
            "and knowledge often determine the entire experience rating. Online reviews "
            "carry enormous weight because the purchase cannot be evaluated beforehand. "
            "Group dynamics on the tour affect individual satisfaction in unpredictable "
            "ways."
        ),
    },
    "activity_centre": {
        "engagement_model": "per_visit_or_booking",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "group_size_and_occasion",
        "loyalty_driver": "fun_factor_and_safety",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Activity centre customers are typically booking for groups (families, "
            "parties, team events), making the group organizer the key decision-maker "
            "while others experience it. Safety perception is non-negotiable. The "
            "experience must be shareable on social media to drive organic growth. "
            "Birthday parties and corporate events create predictable booking patterns."
        ),
    },
    "airbnb": {
        "engagement_model": "per_stay",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "comparison_and_group_size",
        "loyalty_driver": "host_communication_and_accuracy",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Short-term rental guests compare across platforms and listings "
            "simultaneously. The listing photos and description set expectations -- "
            "any gap between promise and reality generates strongly negative reviews. "
            "Host responsiveness before and during the stay is the controllable "
            "loyalty factor. Superhosts build followings that partially insulate "
            "against platform competition."
        ),
    },
    "event_venue": {
        "engagement_model": "per_booking",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "total_event_budget",
        "loyalty_driver": "reliability_and_coordination",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Event venue bookings are high-stakes because the client's reputation "
            "depends on the event going smoothly. Site visits are essential -- "
            "clients need to physically see and feel the space. Availability on "
            "desired dates creates artificial scarcity that supports pricing. "
            "Venue coordinators who handle logistics proactively reduce client "
            "anxiety and earn referrals."
        ),
    },
    "wedding_venue": {
        "engagement_model": "per_booking",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "wedding_budget_and_emotion",
        "loyalty_driver": "emotional_connection_and_coordination",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Wedding venue decisions are among the most emotionally charged purchases "
            "a person makes. The couple envisions their entire day around the space, "
            "making switching after booking psychologically difficult. Price sensitivity "
            "is distorted by the 'once in a lifetime' framing. Vendor coordination "
            "capability and flexibility on customization are key differentiators."
        ),
    },
    # -----------------------------------------------------------------------
    # HEALTHCARE
    # -----------------------------------------------------------------------
    "healthcare_clinic": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "insurance_and_trust",
        "loyalty_driver": "trust_and_continuity",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Healthcare decisions are trust-intensive. Patients value continuity of "
            "care and are reluctant to switch providers because their medical history "
            "and provider familiarity are not easily transferred. Price sensitivity "
            "depends heavily on insurance coverage."
        ),
    },
    "dental": {
        "engagement_model": "per_visit",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_anxiety",
        "loyalty_driver": "trust_and_comfort",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Dental patients are anxiety-driven. Finding a dentist they trust and "
            "feel comfortable with is a high-effort decision. Once settled, they "
            "rarely switch unless forced to. Gentle chairside manner and pain "
            "management matter as much as clinical competence."
        ),
    },
    "veterinary": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "emotional_bond_and_insurance",
        "loyalty_driver": "compassion_and_competence",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Pet owners are emotionally invested and will spend beyond rational "
            "limits when their animal is sick. The vet who demonstrates genuine "
            "care for the animal earns fierce loyalty. End-of-life care experiences "
            "either cement lifetime loyalty or cause permanent loss. Having the "
            "pet's full medical history at one practice creates real switching costs."
        ),
    },
    "mental_health": {
        "engagement_model": "recurring_sessions",
        "decision_speed": "slow",
        "switching_cost": "very_high",
        "price_sensitivity_driver": "insurance_and_perceived_necessity",
        "loyalty_driver": "therapeutic_alliance",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "The therapeutic alliance (trust between therapist and client) takes "
            "months to build and is the single strongest predictor of outcomes. "
            "This creates the highest switching cost of any service industry -- "
            "starting over with a new therapist means re-disclosing painful history. "
            "Stigma still affects initial engagement. Insurance limitations often "
            "force unwanted switches."
        ),
    },
    "optometry": {
        "engagement_model": "per_visit",
        "decision_speed": "slow",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_frame_cost",
        "loyalty_driver": "exam_thoroughness_and_selection",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Optometry combines clinical care with retail (frames and lenses), "
            "creating a unique dual value proposition. Patients visit infrequently "
            "(every 1-2 years) but spend significantly per visit. Insurance panels "
            "heavily determine patient flow. The clinical relationship creates "
            "loyalty that insulates the retail side from online competition."
        ),
    },
    "dermatology": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "insurance_and_cosmetic_vs_medical",
        "loyalty_driver": "results_and_availability",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Dermatology patients split into medical (insurance-covered) and cosmetic "
            "(self-pay) with very different price sensitivities. Cosmetic patients "
            "are results-driven and willing to pay premium prices for visible "
            "improvements. Wait times for appointments are notoriously long, so "
            "availability is a competitive advantage. Before/after results drive "
            "cosmetic referrals."
        ),
    },
    "fertility_clinic": {
        "engagement_model": "per_cycle_or_program",
        "decision_speed": "slow",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "desperation_and_insurance",
        "loyalty_driver": "success_rates_and_emotional_support",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Fertility patients are in an emotionally vulnerable state where the "
            "desire for a child overrides normal financial decision-making. Published "
            "success rates drive initial choice, but the emotional support and "
            "communication during failed cycles determine whether patients stay or "
            "switch. The financial burden is enormous for uninsured patients, but "
            "price is rarely the reason for switching."
        ),
    },
    # -----------------------------------------------------------------------
    # EDUCATION & LEARNING
    # -----------------------------------------------------------------------
    "education": {
        "engagement_model": "subscription_or_term",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "outcome_value_and_alternatives",
        "loyalty_driver": "teaching_quality_and_credential_value",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Education purchases are investments in future outcomes, which makes "
            "the decision slow and highly researched. Once enrolled, switching costs "
            "are high due to credit transfer issues and social ties. Brand reputation "
            "and alumni outcomes matter more than current experience for initial "
            "choice. Parent vs student motivations often conflict."
        ),
    },
    "childcare": {
        "engagement_model": "recurring",
        "decision_speed": "slow",
        "switching_cost": "very_high",
        "price_sensitivity_driver": "budget_and_quality_anxiety",
        "loyalty_driver": "trust_and_child_attachment",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Childcare is arguably the highest-trust purchase a parent makes -- they "
            "are leaving their child with someone else daily. Once a child is settled "
            "and attached to caregivers, switching is traumatic for parent and child "
            "alike. Waitlists create artificial demand. Communication about the "
            "child's day is valued almost as much as the care itself."
        ),
    },
    "driving_school": {
        "engagement_model": "per_session_or_package",
        "decision_speed": "moderate",
        "switching_cost": "low_to_moderate",
        "price_sensitivity_driver": "package_comparison",
        "loyalty_driver": "instructor_patience_and_pass_rate",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Driving school students are anxious learners who need patience and "
            "encouragement. Advertised pass rates heavily influence initial choice. "
            "The instructor's personality match with the student determines whether "
            "lessons feel productive or terrifying. Word of mouth among age-peer "
            "groups (teens, immigrant communities) is the primary acquisition channel."
        ),
    },
    "language_school": {
        "engagement_model": "term_or_subscription",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "duration_and_credential",
        "loyalty_driver": "progress_perception_and_community",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Language learners need to perceive progress to continue paying, but "
            "real fluency takes years. The social bonds formed in class groups create "
            "meaningful switching costs. Competition from apps is real for beginners "
            "but the classroom advantage grows at intermediate and advanced levels. "
            "Motivation peaks at enrollment and requires active maintenance."
        ),
    },
    "music_school": {
        "engagement_model": "recurring_sessions",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "lesson_frequency_and_instrument",
        "loyalty_driver": "teacher_rapport_and_progress",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Music instruction loyalty is almost entirely about the teacher-student "
            "relationship. Students (or their parents) will follow a good teacher "
            "to a new location. Progress is slow and non-linear, requiring the "
            "teacher to maintain motivation through plateaus. Recitals and "
            "performance opportunities are retention tools, not just events."
        ),
    },
    "dance_studio": {
        "engagement_model": "membership_or_class_pack",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "class_frequency",
        "loyalty_driver": "community_and_instructor",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Dance studio loyalty is built through community -- students form "
            "friendships and performance groups that create strong social switching "
            "costs. The instructor's teaching style and choreography preferences "
            "attract specific student types. Showcase events and competitions create "
            "commitment cycles that extend retention."
        ),
    },
    "martial_arts": {
        "engagement_model": "membership",
        "decision_speed": "moderate",
        "switching_cost": "moderate_to_high",
        "price_sensitivity_driver": "perceived_value_and_commitment",
        "loyalty_driver": "instructor_respect_and_belt_progression",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Martial arts schools benefit from built-in progression systems (belts, "
            "ranks) that create psychological investment -- students do not want to "
            "start over at a new school. The instructor-student relationship carries "
            "a cultural respect dimension unique to this industry. Children's programs "
            "drive the majority of revenue for most schools."
        ),
    },
    "coding_bootcamp": {
        "engagement_model": "per_program",
        "decision_speed": "slow",
        "switching_cost": "high",
        "price_sensitivity_driver": "career_roi",
        "loyalty_driver": "job_placement_outcomes",
        "typical_decision_style": "very_deliberate",
        "key_behavioral_note": (
            "Coding bootcamp students are making a career bet with significant "
            "financial and time investment. Job placement rates and salary outcomes "
            "are the primary decision criteria. The cohort experience creates strong "
            "alumni networks. Students are extremely vocal online about their "
            "experience, making review management critical."
        ),
    },
    # -----------------------------------------------------------------------
    # ENTERTAINMENT
    # -----------------------------------------------------------------------
    "cinema": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency_and_alternatives",
        "loyalty_driver": "convenience_and_experience",
        "typical_decision_style": "impulsive_to_moderate",
        "key_behavioral_note": (
            "Cinema attendance is driven by specific film releases, not venue "
            "loyalty. Between blockbusters, attendance drops sharply. Premium "
            "formats (IMAX, recliner seats) command price premiums from specific "
            "segments. Concession pricing is a major pain point but customers pay "
            "it anyway due to the captive environment."
        ),
    },
    "bowling": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "group_activity_budget",
        "loyalty_driver": "atmosphere_and_group_suitability",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Bowling alleys serve as group social venues more than sport facilities. "
            "The decision to visit is usually made by one person on behalf of a "
            "group. Food, drinks, and music quality matter as much as lane "
            "conditions for casual visitors. League bowlers are a small but "
            "highly loyal and profitable segment."
        ),
    },
    "arcade": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "entertainment_budget",
        "loyalty_driver": "game_selection_and_novelty",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Arcade customers (often families or friend groups) are buying time and "
            "experiences, not specific games. New game rotations drive repeat visits. "
            "Prize redemption systems create engagement loops, especially with "
            "children. Token/card systems obscure spending, which increases per-visit "
            "revenue but can create parental backlash."
        ),
    },
    "escape_room": {
        "engagement_model": "per_visit",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "group_size_and_occasion",
        "loyalty_driver": "puzzle_quality_and_theming",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Escape rooms have an inherent repeat-visit limitation -- once a room "
            "is solved, the customer cannot do it again. New room launches are "
            "essential for return visits. Corporate team-building and birthday "
            "parties are major revenue streams. The booking is almost always made "
            "by one person for a group, making that organizer the actual customer."
        ),
    },
    "mini_golf": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "family_entertainment_budget",
        "loyalty_driver": "course_quality_and_atmosphere",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Mini golf is a family and date activity where the social experience "
            "matters more than the course itself. Weather dependency creates "
            "unpredictable demand unless the course is indoor. Add-on revenue "
            "(food, drinks, adjacent attractions) often exceeds golf revenue. "
            "The course must photograph well for social media to drive discovery."
        ),
    },
    "theme_park": {
        "engagement_model": "per_visit_or_season_pass",
        "decision_speed": "moderate",
        "switching_cost": "low",
        "price_sensitivity_driver": "family_budget_and_alternatives",
        "loyalty_driver": "ride_quality_and_nostalgia",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Theme park visits are day-long commitments with high total cost (tickets, "
            "food, parking, merchandise). Season passes convert casual visitors into "
            "regulars and dramatically change the value equation. New ride additions "
            "drive attendance spikes. Nostalgia from childhood visits creates "
            "multi-generational loyalty."
        ),
    },
    "museum": {
        "engagement_model": "per_visit_or_membership",
        "decision_speed": "moderate",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "perceived_educational_value",
        "loyalty_driver": "rotating_exhibitions_and_membership",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Museums compete for discretionary time more than money. Rotating "
            "exhibitions drive repeat visits; permanent collections do not. "
            "Membership programs convert enthusiasts into steady revenue. School "
            "groups and family visits are distinct segments with different needs. "
            "The gift shop often subsidizes admission pricing."
        ),
    },
    "gallery": {
        "engagement_model": "per_visit",
        "decision_speed": "varies",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "collector_vs_browser",
        "loyalty_driver": "artist_curation_and_exclusivity",
        "typical_decision_style": "deliberate_for_purchases",
        "key_behavioral_note": (
            "Art galleries serve two completely different audiences: browsers who "
            "visit for free and collectors who spend substantially. The gallery's "
            "curatorial identity and artist relationships are the core value "
            "proposition for collectors. Opening events are social occasions that "
            "drive attendance and sales. Online viewing rooms expanded reach but "
            "serious collectors still want to see work in person."
        ),
    },
    "nightclub": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "social_context_and_door_price",
        "loyalty_driver": "music_and_social_scene",
        "typical_decision_style": "impulsive",
        "key_behavioral_note": (
            "Nightclub attendance is driven by the specific night (DJ, event, "
            "promotion) rather than venue loyalty. The crowd itself is the product "
            "-- customers want to be around people they find attractive and exciting. "
            "Drink pricing is accepted as premium due to the environment. Social "
            "media presence and FOMO drive attendance more than traditional marketing."
        ),
    },
    "comedy_club": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "performer_and_occasion",
        "loyalty_driver": "lineup_quality_and_atmosphere",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Comedy club attendance is driven by specific performers on the lineup. "
            "The intimate venue atmosphere is a differentiator that streaming cannot "
            "replicate. Two-drink minimums are an industry norm that customers accept "
            "grudgingly. A great show creates word-of-mouth that fills seats for "
            "weeks; a poor show has the opposite effect."
        ),
    },
    # -----------------------------------------------------------------------
    # PROPERTY & FACILITY SERVICES
    # -----------------------------------------------------------------------
    "coworking": {
        "engagement_model": "membership",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "remote_work_budget",
        "loyalty_driver": "community_and_location",
        "typical_decision_style": "deliberate",
        "key_behavioral_note": (
            "Coworking members are buying community and professional environment as "
            "much as desk space. The social network formed at a coworking space "
            "creates switching costs that physical amenities alone cannot. Location "
            "convenience is the top practical driver. Members who make friends at "
            "the space stay far longer than those who keep to themselves."
        ),
    },
    "storage": {
        "engagement_model": "recurring",
        "decision_speed": "moderate",
        "switching_cost": "moderate",
        "price_sensitivity_driver": "unit_size_and_duration",
        "loyalty_driver": "security_and_access_convenience",
        "typical_decision_style": "moderate",
        "key_behavioral_note": (
            "Storage customers intend to rent short-term but often stay for years, "
            "making initial pricing promotions very profitable long-term. The effort "
            "of physically moving stored items creates real switching costs. Security "
            "and clean, dry conditions are baseline expectations. Customers become "
            "surprisingly emotionally attached to the convenience of having the "
            "unit available."
        ),
    },
    "parking": {
        "engagement_model": "per_use_or_monthly",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "daily_commute_cost",
        "loyalty_driver": "location_and_availability",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Parking is a pure commodity where location is nearly the only "
            "differentiator. Monthly contracts create reliable revenue from commuters. "
            "Perceived safety (lighting, cameras, staffing) matters for specific "
            "segments. Dynamic pricing during events can maximize revenue but risks "
            "alienating regular customers who feel gouged."
        ),
    },
    "laundromat": {
        "engagement_model": "per_visit",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency_and_necessity",
        "loyalty_driver": "cleanliness_and_machine_availability",
        "typical_decision_style": "habitual",
        "key_behavioral_note": (
            "Laundromat customers visit because they must, not because they want to. "
            "Cleanliness of the facility directly signals whether the machines will "
            "clean clothes properly. Machine availability at peak times (evenings, "
            "weekends) is the main frustration. Wash-and-fold services convert "
            "time-poor customers into higher-margin recurring clients."
        ),
    },
    "car_wash": {
        "engagement_model": "per_visit_or_membership",
        "decision_speed": "fast",
        "switching_cost": "very_low",
        "price_sensitivity_driver": "frequency_and_vehicle_pride",
        "loyalty_driver": "convenience_and_quality",
        "typical_decision_style": "impulsive_to_habitual",
        "key_behavioral_note": (
            "Car wash customers fall into two groups: occasional visitors triggered "
            "by visible dirt and membership subscribers who wash weekly. Membership "
            "models are extremely profitable because many members under-use them. "
            "Convenience (location on commute route, speed) drives choice. One "
            "scratch or damage incident can destroy the relationship permanently."
        ),
    },
}

# Map business types to their industry norm key.
# Every type maps to its own norm if one exists, or to the closest match.
INDUSTRY_TYPE_MAP = {
    # Food & Drink
    "restaurant": "restaurant",
    "cafe": "cafe",
    "bar": "bar",
    "bakery": "bakery",
    "food_truck": "food_truck",
    "catering": "catering",
    "desserts": "desserts",
    "fast_food": "fast_food",
    "fine_dining": "fine_dining",
    "juice_bar": "juice_bar",
    "coffee_shop": "cafe",
    "pizzeria": "restaurant",
    "brewery": "bar",
    "winery": "bar",
    "deli": "bakery",
    "ice_cream": "desserts",
    "smoothie": "juice_bar",
    "bubble_tea": "juice_bar",
    # Health & Personal Care
    "gym": "gym",
    "yoga": "yoga",
    "spa": "spa",
    "barbershop": "barbershop",
    "hair_salon": "hair_salon",
    "nail_salon": "nail_salon",
    "tattoo": "tattoo",
    "physio": "physio",
    "chiropractor": "chiropractor",
    "personal_trainer": "personal_trainer",
    "meditation_studio": "meditation_studio",
    "pilates": "yoga",
    "crossfit": "gym",
    "boxing_gym": "gym",
    "massage": "spa",
    "acupuncture": "physio",
    "beauty_salon": "hair_salon",
    "waxing": "nail_salon",
    "tanning": "spa",
    # Retail
    "grocery": "grocery",
    "clothing": "clothing",
    "bookshop": "bookshop",
    "gift_shop": "gift_shop",
    "florist": "florist",
    "sports": "sports",
    "electronics": "electronics",
    "toy_shop": "toy_shop",
    "pet_shop": "pet_shop",
    "furniture": "furniture",
    "jewelry": "jewelry",
    "thrift_store": "thrift_store",
    "hardware": "hardware",
    "pharmacy": "pharmacy",
    "optical": "optical",
    "shoe_store": "shoe_store",
    "vintage": "thrift_store",
    "antiques": "thrift_store",
    "art_supplies": "bookshop",
    "stationery": "gift_shop",
    "wine_shop": "grocery",
    "liquor_store": "grocery",
    "garden_centre": "hardware",
    "home_decor": "furniture",
    "mattress": "furniture",
    "appliance": "electronics",
    "phone_repair": "electronics",
    "bike_shop": "sports",
    "outdoor_gear": "sports",
    "supplement_store": "pharmacy",
    "vape_shop": "grocery",
    "record_store": "bookshop",
    "fabric_store": "gift_shop",
    "craft_store": "gift_shop",
    "bridal_shop": "clothing",
    "kids_clothing": "clothing",
    "consignment": "thrift_store",
    # Services
    "auto": "auto",
    "dry_cleaning": "dry_cleaning",
    "photography": "photography",
    "printing": "printing",
    "accountant": "accountant",
    "legal": "legal",
    "consulting": "consulting",
    "freelance": "freelance",
    "marketing_agency": "marketing_agency",
    "cleaning": "cleaning",
    "tutoring": "tutoring",
    "plumbing": "plumbing",
    "electrical": "electrical",
    "landscaping": "landscaping",
    "pest_control": "pest_control",
    "moving_company": "moving_company",
    "insurance": "insurance",
    "financial_advisor": "financial_advisor",
    "real_estate": "real_estate",
    "hvac": "plumbing",
    "roofing": "electrical",
    "painting": "landscaping",
    "locksmith": "plumbing",
    "handyman": "plumbing",
    "tailor": "dry_cleaning",
    "cobbler": "dry_cleaning",
    "notary": "legal",
    "tax_preparer": "accountant",
    "bookkeeper": "accountant",
    "pr_agency": "marketing_agency",
    "seo_agency": "marketing_agency",
    "design_agency": "marketing_agency",
    "recruitment": "staffing",
    "career_coaching": "consulting",
    "life_coaching": "consulting",
    "dog_walking": "cleaning",
    "pet_grooming": "barbershop",
    "pet_boarding": "childcare",
    "dog_training": "tutoring",
    "event_planning": "catering",
    "interior_design": "consulting",
    "architecture": "consulting",
    "surveyor": "consulting",
    "travel_agency": "tour_operator",
    # Technology
    "saas": "saas",
    "ecommerce": "ecommerce",
    "app": "app",
    "it_services": "it_services",
    "web_design": "web_design",
    "hosting": "hosting",
    "cybersecurity": "cybersecurity",
    "data_analytics": "data_analytics",
    "cloud_services": "hosting",
    "managed_services": "it_services",
    "devops": "it_services",
    "ai_services": "saas",
    "marketplace": "ecommerce",
    "fintech": "saas",
    "edtech": "saas",
    "healthtech": "saas",
    "game_studio": "app",
    # B2B
    "b2b_services": "b2b_services",
    "logistics": "logistics",
    "wholesale": "wholesale",
    "manufacturing": "manufacturing",
    "staffing": "staffing",
    "commercial_cleaning": "commercial_cleaning",
    "fleet_management": "fleet_management",
    "supply_chain": "logistics",
    "freight": "logistics",
    "warehousing": "logistics",
    "packaging": "manufacturing",
    "industrial_equipment": "manufacturing",
    "office_supplies": "wholesale",
    "business_consulting": "consulting",
    "management_consulting": "consulting",
    # Hospitality
    "hotel": "hotel",
    "hostel": "hostel",
    "campsite": "campsite",
    "tour_operator": "tour_operator",
    "activity_centre": "activity_centre",
    "airbnb": "airbnb",
    "event_venue": "event_venue",
    "wedding_venue": "wedding_venue",
    "bed_and_breakfast": "airbnb",
    "resort": "hotel",
    "motel": "hotel",
    "vacation_rental": "airbnb",
    "glamping": "campsite",
    "conference_centre": "event_venue",
    "banquet_hall": "event_venue",
    "rv_park": "campsite",
    # Healthcare
    "healthcare_clinic": "healthcare_clinic",
    "dental": "dental",
    "veterinary": "veterinary",
    "mental_health": "mental_health",
    "optometry": "optometry",
    "dermatology": "dermatology",
    "fertility_clinic": "fertility_clinic",
    "orthodontist": "dental",
    "pediatrician": "healthcare_clinic",
    "urgent_care": "healthcare_clinic",
    "physical_therapy": "physio",
    "occupational_therapy": "physio",
    "speech_therapy": "physio",
    "psychiatrist": "mental_health",
    "psychologist": "mental_health",
    "counselor": "mental_health",
    "podiatrist": "healthcare_clinic",
    "allergist": "healthcare_clinic",
    "cardiologist": "healthcare_clinic",
    "ob_gyn": "healthcare_clinic",
    "plastic_surgery": "dermatology",
    "cosmetic_clinic": "dermatology",
    "hearing_aid": "optical",
    "dental_lab": "dental",
    # Education & Learning
    "education": "education",
    "childcare": "childcare",
    "driving_school": "driving_school",
    "language_school": "language_school",
    "music_school": "music_school",
    "dance_studio": "dance_studio",
    "martial_arts": "martial_arts",
    "coding_bootcamp": "coding_bootcamp",
    "daycare": "childcare",
    "preschool": "childcare",
    "after_school": "childcare",
    "montessori": "childcare",
    "art_school": "music_school",
    "acting_school": "dance_studio",
    "swim_school": "driving_school",
    "test_prep": "tutoring",
    "online_course": "education",
    "university": "education",
    "trade_school": "coding_bootcamp",
    "cooking_class": "language_school",
    # Entertainment
    "cinema": "cinema",
    "bowling": "bowling",
    "arcade": "arcade",
    "escape_room": "escape_room",
    "mini_golf": "mini_golf",
    "theme_park": "theme_park",
    "museum": "museum",
    "gallery": "gallery",
    "nightclub": "nightclub",
    "comedy_club": "comedy_club",
    "karaoke": "nightclub",
    "laser_tag": "arcade",
    "trampoline_park": "arcade",
    "go_kart": "activity_centre",
    "zoo": "theme_park",
    "aquarium": "museum",
    "planetarium": "museum",
    "water_park": "theme_park",
    "amusement_park": "theme_park",
    "concert_venue": "comedy_club",
    "theater": "comedy_club",
    "live_music": "nightclub",
    "pool_hall": "bowling",
    "board_game_cafe": "bowling",
    "axe_throwing": "escape_room",
    "rock_climbing": "activity_centre",
    "skating_rink": "bowling",
    "paintball": "activity_centre",
    # Property & Facility Services
    "coworking": "coworking",
    "storage": "storage",
    "parking": "parking",
    "laundromat": "laundromat",
    "car_wash": "car_wash",
    "mailbox_rental": "storage",
    "self_storage": "storage",
    "valet": "parking",
    "garage": "parking",
    "coin_laundry": "laundromat",
    # Fallback
    "other": "restaurant",
}


# ---------------------------------------------------------------------------
# Demographic behavioral research
# ---------------------------------------------------------------------------

AGE_BEHAVIORAL_PROFILES = {
    "18-24": {
        "impulsivity": "high",
        "loyalty": "low",
        "price_sensitivity": "high",
        "digital_expectation": "very_high",
        "change_openness": "high",
        "social_proof_reliance": "very_high",
        "note": (
            "Young adults are digitally native, highly influenced by social proof "
            "and peer behavior. They switch easily, are price-conscious but will "
            "pay for status/experience. Highly responsive to trends and novelty."
        ),
    },
    "25-34": {
        "impulsivity": "moderate_to_high",
        "loyalty": "moderate",
        "price_sensitivity": "moderate",
        "digital_expectation": "high",
        "change_openness": "moderate_to_high",
        "social_proof_reliance": "high",
        "note": (
            "Early career professionals balancing aspiration with budget. Building "
            "brand preferences but still exploring. Value convenience and quality. "
            "Comfortable with technology."
        ),
    },
    "35-44": {
        "impulsivity": "moderate",
        "loyalty": "moderate_to_high",
        "price_sensitivity": "moderate",
        "digital_expectation": "moderate_to_high",
        "change_openness": "moderate",
        "social_proof_reliance": "moderate",
        "note": (
            "Established preferences, growing brand loyalty. Often family-oriented, "
            "which affects spending priorities. Value reliability and consistency. "
            "Less swayed by trends, more by proven quality."
        ),
    },
    "45-54": {
        "impulsivity": "low_to_moderate",
        "loyalty": "high",
        "price_sensitivity": "moderate",
        "digital_expectation": "moderate",
        "change_openness": "low_to_moderate",
        "social_proof_reliance": "low_to_moderate",
        "note": (
            "Strong established habits and brand preferences. Resist change unless "
            "clearly beneficial. Value personal service and relationships. Peak "
            "earning years but cautious about unnecessary spending."
        ),
    },
    "55-64": {
        "impulsivity": "low",
        "loyalty": "very_high",
        "price_sensitivity": "moderate_to_high",
        "digital_expectation": "low_to_moderate",
        "change_openness": "low",
        "social_proof_reliance": "low",
        "note": (
            "Strong status quo bias. Very loyal to established routines and "
            "businesses. May resist digital-first changes. Value personal interaction "
            "and familiar experiences. Price-aware as retirement approaches."
        ),
    },
    "65+": {
        "impulsivity": "very_low",
        "loyalty": "very_high",
        "price_sensitivity": "high",
        "digital_expectation": "low",
        "change_openness": "very_low",
        "social_proof_reliance": "low",
        "note": (
            "Strongest status quo bias. Extremely loyal to known businesses. Fixed "
            "income increases price sensitivity. May struggle with technology-driven "
            "changes. Value personal relationships and familiarity above all."
        ),
    },
}

INCOME_BEHAVIORAL_PROFILES = {
    "budget": {
        "price_sensitivity": "very_high",
        "value_orientation": "price_first",
        "switching_trigger": "any_price_increase",
        "note": (
            "Every price change is felt immediately. Customers actively seek "
            "alternatives and compare prices. Loyalty exists only when the business "
            "is the cheapest viable option."
        ),
    },
    "lower_middle": {
        "price_sensitivity": "high",
        "value_orientation": "value_for_money",
        "switching_trigger": "perceived_unfairness",
        "note": (
            "Price-aware but willing to pay slightly more for quality or convenience. "
            "React strongly to perceived unfairness. Moderate brand loyalty when "
            "value proposition is clear."
        ),
    },
    "middle": {
        "price_sensitivity": "moderate",
        "value_orientation": "balanced",
        "switching_trigger": "quality_decline_or_major_price_jump",
        "note": (
            "Balance quality, convenience, and price. Tolerate moderate price increases "
            "if quality is maintained. Willing to try alternatives but not actively "
            "seeking them."
        ),
    },
    "upper_middle": {
        "price_sensitivity": "low_to_moderate",
        "value_orientation": "quality_first",
        "switching_trigger": "quality_or_experience_decline",
        "note": (
            "Price is secondary to quality and experience. Will pay a premium for "
            "superior service. More sensitive to quality decline than price increases. "
            "Value exclusivity and differentiation."
        ),
    },
    "affluent": {
        "price_sensitivity": "low",
        "value_orientation": "experience_and_status",
        "switching_trigger": "status_or_experience_mismatch",
        "note": (
            "Price is not a decision factor. Value exclusivity, superior experience, "
            "and personal recognition. May actually view price increases positively "
            "if they signal quality. Switch when a brand no longer matches their "
            "self-image."
        ),
    },
    "mixed": {
        "price_sensitivity": "varied",
        "value_orientation": "segment_dependent",
        "switching_trigger": "varies",
        "note": (
            "Mixed income base means different customers react very differently to "
            "the same change. Price increases may retain affluent customers while "
            "losing budget-conscious ones. Segmented analysis is essential."
        ),
    },
}


# ---------------------------------------------------------------------------
# Profile builder
# ---------------------------------------------------------------------------

@dataclass
class PsychologicalProfile:
    """Multi-layer behavioral profile assembled from survey + research."""
    cultural_layer: dict = field(default_factory=dict)
    demographic_layer: dict = field(default_factory=dict)
    industry_layer: dict = field(default_factory=dict)
    behavioral_layer: dict = field(default_factory=dict)
    summary: str = ""
    confidence: str = "low"


def build_profile(
    business: BusinessSnapshot,
    country_code: str = "",
) -> PsychologicalProfile:
    """Build a multi-layer psychological profile for simulation.

    Layers:
    1. Cultural (Hofstede dimensions if country known)
    2. Demographic (age/income behavioral research)
    3. Industry (business-type behavioral norms)
    4. Behavioral (composite predictions)

    Returns a PsychologicalProfile with a plain-English summary
    suitable for injection into prompts.
    """
    profile = PsychologicalProfile()
    summary_parts = []
    confidence_score = 0

    # --- Layer 1: Cultural ---
    try:
        from research.rag_library import get_country_profile, get_persona_cultural_modifier
        country = country_code or (business.location or "").split(",")[-1].strip()
        cultural = get_country_profile(country)
        if cultural:
            profile.cultural_layer = cultural
            modifier = get_persona_cultural_modifier(country)
            if modifier:
                summary_parts.append(f"CULTURAL CONTEXT:\n{modifier}")
                confidence_score += 2
    except Exception as e:
        logger.warning("Cultural layer failed (non-fatal): %s", e)

    # --- Layer 2: Demographic ---
    demo_parts = []

    if business.customer_age_distribution:
        age_notes = []
        for bracket in business.customer_age_distribution:
            age_profile = AGE_BEHAVIORAL_PROFILES.get(bracket)
            if age_profile:
                age_notes.append(f"Age {bracket}: {age_profile['note']}")
        if age_notes:
            profile.demographic_layer["age_profiles"] = age_notes
            demo_parts.append("AGE BEHAVIOR:\n" + "\n".join(age_notes))
            confidence_score += 2

    if business.customer_income_bracket:
        income = INCOME_BEHAVIORAL_PROFILES.get(business.customer_income_bracket)
        if income:
            profile.demographic_layer["income_profile"] = income
            demo_parts.append(
                f"INCOME BEHAVIOR ({business.customer_income_bracket}):\n{income['note']}"
            )
            confidence_score += 2

    if business.customer_gender_split and business.customer_gender_split != "unknown":
        profile.demographic_layer["gender_split"] = business.customer_gender_split

    if business.local_vs_visitor_ratio:
        profile.demographic_layer["local_visitor"] = business.local_vs_visitor_ratio
        if business.local_vs_visitor_ratio == "all_online":
            demo_parts.append(
                "CHANNEL: All online -- no physical location. Personas should interact "
                "digitally, not in-person. Switching costs are lower online."
            )
        elif business.local_vs_visitor_ratio == "mostly_visitors":
            demo_parts.append(
                "CUSTOMER BASE: Mostly new or one-time customers. Low baseline loyalty. "
                "First impressions and discovery channels matter more than retention."
            )

    if business.digital_savviness:
        profile.demographic_layer["digital_savviness"] = business.digital_savviness

    if demo_parts:
        summary_parts.append("\n\n".join(demo_parts))

    # --- Layer 3: Industry ---
    norm_key = INDUSTRY_TYPE_MAP.get(business.type) or INDUSTRY_TYPE_MAP.get("other", "restaurant")
    norms = INDUSTRY_NORMS.get(norm_key)
    if norms:
        profile.industry_layer = norms
        industry_text = (
            f"INDUSTRY BEHAVIORAL NORMS ({business.type}):\n"
            f"Engagement model: {norms['engagement_model']}\n"
            f"Decision speed: {norms['decision_speed']}\n"
            f"Switching cost: {norms['switching_cost']}\n"
            f"Loyalty driver: {norms['loyalty_driver']}\n"
            f"{norms['key_behavioral_note']}"
        )
        summary_parts.append(industry_text)
        confidence_score += 1

    # --- Layer 4: Behavioral composite ---
    behavioral = {}

    # Composite price sensitivity
    if business.price_range:
        range_map = {
            "budget": "very_high",
            "mid_range": "moderate",
            "premium": "low_to_moderate",
            "luxury": "low",
        }
        behavioral["price_sensitivity_from_tier"] = range_map.get(
            business.price_range, "moderate"
        )

    if business.average_transaction_value:
        behavioral["baseline_transaction_value"] = business.average_transaction_value

    if norms:
        behavioral["engagement_model"] = norms["engagement_model"]
        behavioral["switching_cost"] = norms["switching_cost"]
        behavioral["decision_style"] = norms["typical_decision_style"]

    profile.behavioral_layer = behavioral

    if business.price_range and business.average_transaction_value:
        summary_parts.append(
            f"PRICING CONTEXT:\n"
            f"Price positioning: {business.price_range}. "
            f"Average transaction: {business.average_transaction_value}. "
            f"Personas should calibrate their price reactions to this baseline."
        )
        confidence_score += 1

    # --- Assemble ---
    profile.summary = "\n\n---\n\n".join(summary_parts) if summary_parts else ""

    if confidence_score >= 5:
        profile.confidence = "high"
    elif confidence_score >= 3:
        profile.confidence = "medium"
    else:
        profile.confidence = "low"

    logger.info(
        "Psychological profile built: %d layers, %d chars, confidence=%s",
        len([p for p in [profile.cultural_layer, profile.demographic_layer,
                         profile.industry_layer, profile.behavioral_layer] if p]),
        len(profile.summary),
        profile.confidence,
    )

    return profile


def build_cultural_profile(country_code: str) -> str:
    """Build a cultural context string for a country.

    Lightweight version of build_profile for twin queries --
    returns only the Hofstede cultural modifier text.
    Returns empty string if country is unknown.
    """
    if not country_code:
        return ""
    try:
        from research.rag_library import get_country_profile, get_persona_cultural_modifier
        cultural = get_country_profile(country_code)
        if not cultural:
            return ""
        modifier = get_persona_cultural_modifier(country_code)
        return modifier or ""
    except Exception as e:
        logger.warning("build_cultural_profile failed (non-fatal): %s", e)
        return ""
