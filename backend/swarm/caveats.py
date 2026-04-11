"""
Caveat Generator -- produces contextual warnings for simulation results.

Draws from A/B testing theory (docs/ab-testing-theory/) to surface
statistically-grounded caveats. Every simulation result must include
at least the baseline caveats (self-selection, not-causation).

This is NOT about being pessimistic -- it's about being honest.
A caveat like "your personas can't simulate the gap between saying
they'd use a loyalty card and actually using it" makes our product
MORE trustworthy, not less.
"""

import re
from dataclasses import dataclass
from typing import List

from backend.models.business import BusinessSnapshot


@dataclass
class Caveat:
    type: str        # Machine-readable category
    title: str       # Short heading for UI
    message: str     # Plain-English explanation
    severity: str    # "info", "warning", "critical"
    source: str      # Which topic/principle this comes from


# Keywords that suggest the user is reacting to extreme recent performance
RTM_TRIGGER_PATTERNS = [
    # General business patterns
    r"sales (have been|are) (down|dropping|terrible|awful|bad|low)",
    r"(terrible|awful|bad|worst|lowest) (month|week|quarter|year|period)",
    r"(lost|losing) customers",
    r"reviews (dropped|fell|tanked|are down|went down)",
    r"(foot traffic|visits|bookings) (down|dropped|declining)",
    r"(best|highest|record|amazing) (month|week|quarter|sales)",
    r"(suddenly|recently) (worse|better|dropped|improved)",
    # SaaS / tech patterns
    r"churn (rate|is) (up|increasing|high|rising)",
    r"MRR (down|dropping|declining)",
    r"DAU (down|declining|dropping)",
    r"ARR (down|declining)",
    r"NPS (dropped|declining|low)",
    r"conversion (rate|is) (down|low|declining)",
    r"CAC (up|increasing|rising)",
    r"LTV (down|declining)",
    r"retention (down|declining|dropping)",
    r"engagement (down|declining|dropping)",
]

# Keywords suggesting novelty/new feature adoption
NOVELTY_PATTERNS = [
    r"(new|launch|introduce|add|start|create) .*(app|feature|product|service|menu item|loyalty|program|card|system)",
    r"(loyalty card|loyalty program|rewards|membership|subscription)",
    r"(mobile app|online ordering|delivery service|website)",
    r"(new|launch|release|ship) .*(feature|update|integration|api|dashboard|module|version|tier|plan)",
    r"(beta|alpha|early access|waitlist)",
    r"(redesign|rebrand|pivot|reposition)",
    r"(new location|new branch|expansion|franchise)",
    r"(hire|staffing|team expansion)",
]

# Keywords suggesting opt-in/adherence-dependent outcomes
ADHERENCE_PATTERNS = [
    r"(loyalty card|loyalty program|rewards|membership|app|sign.?up|subscribe|opt.?in|register)",
    r"(would .* use|would .* sign up|would .* join|would .* download)",
    r"(would .* subscribe|would .* upgrade|would .* renew|would .* onboard)",
    r"(free trial|freemium|demo|pilot|proof of concept)",
    r"(newsletter|email list|notification|push notification)",
    r"(referral|refer a friend|invite|share)",
    r"(training|onboarding|setup|implementation)",
]

# Keywords suggesting price changes
PRICE_PATTERNS = [
    r"(raise|increase|lower|reduce|change) .*(price|cost|fee|rate)",
    r"(more expensive|cheaper|discount|surcharge|markup)",
    r"\d+%",
    r"(subscription|monthly|annual|per seat|per user|per license) .*(price|cost|fee)",
    r"(tier|plan|package) .*(change|update|restructure)",
    r"(free to paid|monetize|paywall)",
    r"(bundle|unbundle|add-on|upsell)",
    r"(contract|renewal|renegotiate)",
]

# Keywords about competitors and competitive positioning
COMPETITION_PATTERNS = [
    r"(competitor|competing|rival|alternative) .*(launch|offer|price|feature|enter|expand)",
    r"(switch|switching|migrate|migrating) to .*(competitor|rival|alternative|another)",
    r"(losing|lost) .*(to|customers to) .*(competitor|rival|another)",
    r"(compete|differentiate|stand out|unique selling|USP|moat|defensib)",
    r"(market share|marketshare) .*(lost|losing|declining|down|shrinking)",
    r"(new entrant|new player|new competitor|copycat|clone)",
    r"(price war|undercutting|undercut|race to bottom)",
    r"(they|competitor|rival) .*(cheaper|better|faster|launched|released|offer)",
]

# Keywords about new channels or distribution changes
CHANNEL_PATTERNS = [
    r"(online|e-?commerce|web|digital) .*(store|shop|presence|channel|sales)",
    r"(delivery|takeout|take-out|curbside|pickup|pick-up|drive-thru|drive-through)",
    r"(marketplace|amazon|etsy|shopify|uber eats|doordash|grubhub|instacart)",
    r"(social media|instagram|tiktok|facebook|youtube) .*(sell|shop|store|channel)",
    r"(wholesale|B2B|retail|DTC|direct.to.consumer)",
    r"(pop-up|pop up|kiosk|vending|mobile unit|food truck)",
    r"(app store|play store|mobile app|PWA|progressive web app)",
    r"(affiliate|partner|reseller|distributor|broker|agent)",
    r"(open|launch|expand|start) .*(channel|location|branch|market|region|country)",
    r"(omnichannel|multi-?channel|cross-?channel)",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def generate_caveats(
    business: BusinessSnapshot,
    question: str,
    persona_count: int,
    success_count: int,
    variant_a: str | None = None,
    variant_b: str | None = None,
    review_signals: object | None = None,
) -> List[Caveat]:
    """Generate contextual caveats for a simulation result.

    Always includes baseline caveats. Adds contextual ones based on
    the question content, business profile quality, and simulation health.
    """
    caveats: List[Caveat] = []

    # === ALWAYS-ON CAVEATS ===

    # Not causation (Topic 6)
    caveats.append(Caveat(
        type="not_causation",
        title="This is a thinking tool, not a prediction",
        message=(
            "These are simulated reactions from AI-generated personas, not real customers. "
            "Use this to identify concerns you hadn't considered and pressure-test your "
            "thinking -- not as proof that a decision will work."
        ),
        severity="info",
        source="Topic 6: Causation vs Correlation",
    ))

    # Self-selection (Topic 4)
    caveats.append(Caveat(
        type="self_selection",
        title="Real customers choose whether to engage",
        message=(
            "Our personas are asked directly and must respond. In reality, many customers "
            "would simply not notice or not care about this change. The responses here "
            "represent customers who DO have an opinion -- the silent majority may differ."
        ),
        severity="info",
        source="Topic 4: Attrition & Adherence",
    ))

    # === CONTEXTUAL CAVEATS ===

    # Regression to the mean (Topic 5)
    if _matches_any(question, RTM_TRIGGER_PATTERNS):
        caveats.append(Caveat(
            type="rtm_warning",
            title="Extreme performance tends to bounce back on its own",
            message=(
                "It sounds like you're asking because things have been unusually "
                "good or bad recently. Even without any changes, extreme periods "
                "naturally revert toward your normal. Some of the improvement "
                "(or decline) you'd see next would happen regardless of what you decide."
            ),
            severity="warning",
            source="Topic 5: Regression to the Mean",
        ))

    # Novelty effect (Topic 4)
    if _matches_any(question, NOVELTY_PATTERNS):
        caveats.append(Caveat(
            type="novelty_effect",
            title="New things get more attention than they keep",
            message=(
                "When something is new, customers pay more attention to it. "
                "Our personas react to the idea as if hearing it for the first time. "
                "In practice, initial enthusiasm often fades -- real adoption is typically "
                "lower than stated interest."
            ),
            severity="warning",
            source="Topic 4: Novelty Effects",
        ))

    # Adherence gap (Topic 4)
    if _matches_any(question, ADHERENCE_PATTERNS):
        caveats.append(Caveat(
            type="adherence_gap",
            title="Saying they'd use it does not equal actually using it",
            message=(
                "This question involves something customers would need to actively "
                "opt into or use regularly. There's a well-documented gap between "
                "stated intentions and actual behavior. If personas say they'd sign up, "
                "expect real sign-up rates to be significantly lower."
            ),
            severity="warning",
            source="Topic 4: Adherence",
        ))

    # Price sensitivity amplification
    if _matches_any(question, PRICE_PATTERNS):
        caveats.append(Caveat(
            type="price_sensitivity",
            title="Price reactions are often overstated in hypotheticals",
            message=(
                "When asked hypothetically about price changes, people tend to overstate "
                "their sensitivity. In practice, customers who say they'd leave often don't, "
                "and customers who say they'd accept an increase may still complain more. "
                "Treat the direction as informative, but the magnitude with skepticism."
            ),
            severity="info",
            source="Behavioral economics research on hypothetical bias",
        ))

    # Competition caveat
    if _matches_any(question, COMPETITION_PATTERNS):
        caveats.append(Caveat(
            type="competitive_context",
            title="Competitor reactions are hard to simulate",
            message=(
                "Our personas can tell you how they feel about your offering versus "
                "what they know of competitors, but they cannot predict what competitors "
                "will do next. Competitive dynamics are fluid -- a rival could match your "
                "move, undercut you, or ignore you entirely. Treat competitive insights "
                "as a snapshot of current perception, not a strategic forecast."
            ),
            severity="warning",
            source="Competitive strategy limitations in simulation",
        ))

    # Channel caveat
    if _matches_any(question, CHANNEL_PATTERNS):
        caveats.append(Caveat(
            type="channel_adoption",
            title="New channels face discovery and habit barriers",
            message=(
                "Adding a new channel (online, delivery, marketplace) sounds simple, "
                "but customers need to discover it, trust it, and change their habits. "
                "Personas react to the concept in isolation -- they cannot account for "
                "the friction of finding your new channel, learning the interface, or "
                "breaking their current routine. Real adoption curves are slower than "
                "stated interest suggests."
            ),
            severity="warning",
            source="Topic 4: Channel adoption and habit formation",
        ))

    # Small sample warning (Topic 2)
    if persona_count < 12:
        caveats.append(Caveat(
            type="small_sample",
            title="Small persona count -- results less reliable",
            message=(
                f"This simulation used only {persona_count} personas. "
                "With fewer than 12, individual outlier responses have outsized "
                "influence on the overall result. Consider re-running with 15-20 personas."
            ),
            severity="warning",
            source="Topic 2: Sample Size & Precision",
        ))

    # High failure rate
    if persona_count > 0 and success_count < persona_count:
        failure_rate = 1 - (success_count / persona_count)
        if failure_rate > 0.2:
            caveats.append(Caveat(
                type="high_failure_rate",
                title="Some persona interviews failed",
                message=(
                    f"{persona_count - success_count} out of {persona_count} personas "
                    "couldn't be interviewed (API errors). The results are based on "
                    f"the {success_count} that succeeded, which may not be fully representative."
                ),
                severity="warning",
                source="Topic 2: Evaluating Tests",
            ))

    # Profile quality warning (Topic 4 -- shared profile dependency)
    profile_length = len(business.description or "") + len(business.customer_description or "")
    if profile_length < 100:
        caveats.append(Caveat(
            type="profile_quality",
            title="More detail about your business would improve accuracy",
            message=(
                "Your business description is quite brief. All personas are generated "
                "from this description, so vagueness here means vague personas. "
                "Adding details about your typical customers, their habits, and what "
                "they care about would make the simulation much more realistic."
            ),
            severity="warning",
            source="Topic 4: Data Dependence (shared profile bias)",
        ))

    # Cherry-pick warning (always for results with standout voices) (Topic 3)
    caveats.append(Caveat(
        type="cherry_pick_note",
        title="Quoted voices are illustrative, not representative",
        message=(
            "The specific personas quoted in this report were selected to show "
            "the range of reactions, not because they represent the majority. "
            "Don't over-weight a single persona's strong opinion."
        ),
        severity="info",
        source="Topic 3: P-Hacking & Cherry Picking",
    ))

    # === REVIEWER INTELLIGENCE CAVEATS ===

    if review_signals is not None:
        # Silent majority caveat -- ALWAYS shown when reviewer intelligence is used
        caveats.append(Caveat(
            type="silent_majority_note",
            title="Most of your customers never leave reviews",
            message=(
                "The customers who matter most for this decision are the ones "
                "who never post online. We have modelled them based on area "
                "demographics and spending patterns, but this is our best "
                "estimate -- not a measurement. The only way to know for sure "
                "is to test with a small subset of real customers first."
            ),
            severity="warning",
            source="Gao et al. (2015): Vocal Minority and Silent Majority",
        ))

        # Sparse review data
        total_reviews = getattr(review_signals, "total_review_count", 0)
        if total_reviews < 20:
            caveats.append(Caveat(
                type="review_data_sparse",
                title="Very few reviews to work from",
                message=(
                    "The customer picture here is based more on area demographics "
                    "than actual review data. Treat results as especially directional."
                ),
                severity="warning",
                source="Review signal confidence",
            ))

        # Tourist-heavy reviews
        tourist_ratio = getattr(review_signals, "tourist_ratio_estimate", 0)
        if tourist_ratio > 0.5:
            caveats.append(Caveat(
                type="tourist_heavy_reviews",
                title="Over half your reviewers appear to be tourists",
                message=(
                    "Tourists behave very differently from locals when it comes "
                    "to price -- they are often less sensitive but they will not "
                    "return regardless of your decision."
                ),
                severity="info",
                source="Review tourist/local signal analysis",
            ))

        # Price change history
        price_change = getattr(review_signals, "price_change_detected", False)
        if price_change:
            caveats.append(Caveat(
                type="price_change_history",
                title="Your reviews mention a previous price change",
                message=(
                    "We have used this as signal for how your customers responded "
                    "historically -- but every price change lands differently "
                    "depending on timing and context."
                ),
                severity="info",
                source="Review price change signal detection",
            ))

    return caveats
