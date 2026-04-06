# Known A/B Test Results for Backtesting

These are real, published A/B test results we can use to validate our swarm engine. For each case, we define the business context, what was tested, and what actually happened.

**Scoring column** is left blank until we run each case through the swarm.

---

## 1. Booking.com — Urgency Messaging

**Source**: Booking.com engineering blog / CXL Institute case studies
**What was tested**: Showing "Only 2 rooms left!" urgency messages on hotel listings vs. no urgency messaging
**Real result**: Urgency messaging increased conversions significantly. Booking.com kept it permanently.
**Why it won**: Scarcity triggers action. Customers who were on the fence booked immediately rather than "thinking about it."

**Murmur input**:
- Business type: Hotel booking platform / small hotel
- Question: "Should we show customers a message saying 'Only a few rooms left!' when availability is low?"
- Expected: Swarm should predict increased bookings but may flag that some customers find it manipulative

**Score**: _pending_

---

## 2. Netflix — Artwork Personalization

**Source**: Netflix Tech Blog, "Artwork Personalization at Netflix" (2017)
**What was tested**: Showing personalized thumbnail artwork for each title based on user preferences vs. a single default thumbnail
**Real result**: Personalized artwork significantly increased engagement and play rates.
**Why it won**: People are drawn to imagery that reflects their interests — a rom-com fan sees the romantic still, an action fan sees the explosion.

**Murmur input**:
- Business type: Small streaming service or DVD rental shop
- Question: "Should we customize which cover image we show for each movie based on what we know about the customer?"
- Expected: Positive, but personas may flag the "creepiness" factor of personalization

**Score**: _pending_

---

## 3. HubSpot — Removing Navigation from Landing Pages

**Source**: HubSpot Marketing Blog
**What was tested**: Removing the site navigation menu from landing pages vs. keeping it
**Real result**: Removing navigation increased conversion rates by up to 28% on some pages.
**Why it won**: Fewer distractions = more focus on the call-to-action. Visitors couldn't wander away to other pages.

**Murmur input**:
- Business type: Small business with a website offering a free consultation
- Question: "On our 'Book a Free Consultation' page, should we remove all other navigation links so customers can only book or leave?"
- Expected: Mixed — some personas will feel "trapped" but the focused ones will convert

**Score**: _pending_

---

## 4. Etsy — Free Shipping Threshold

**Source**: Etsy Seller Handbook / public earnings calls discussing free shipping initiative (2019)
**What was tested**: Offering free shipping on orders over $35 vs. no free shipping guarantee
**Real result**: Items with free shipping guarantees had significantly higher conversion rates. Etsy made it a platform-wide push.
**Why it won**: Shipping costs are the #1 reason for cart abandonment. A clear threshold motivates customers to add more items.

**Murmur input**:
- Business type: Small online craft store
- Question: "Should we offer free shipping on orders over $35, or keep our current flat $5 shipping rate?"
- Variant A: Free shipping over $35
- Variant B: Flat $5 shipping
- Expected: Swarm should pick A, with reasoning about cart behavior

**Score**: _pending_

---

## 5. Obama 2008 Campaign — Button Text

**Source**: Optimizely case study / Dan Siroker's talks
**What was tested**: "Sign Up" vs. "Learn More" as the call-to-action button text on the campaign website
**Real result**: "Learn More" outperformed "Sign Up" by 18.6% in email signups.
**Why it won**: Lower commitment language reduces friction. People are more willing to "learn" than to "sign up."

**Murmur input**:
- Business type: Local business with a website offering a newsletter
- Question: "On our website, should our main button say 'Sign Up for Updates' or 'Learn More About Us'?"
- Variant A: "Sign Up for Updates"
- Variant B: "Learn More About Us"
- Expected: Swarm should pick B, reasoning about commitment aversion

**Score**: _pending_

---

## 6. Airbnb — Professional Photography

**Source**: First Round Review / Airbnb growth team talks
**What was tested**: Offering free professional photography for listings vs. host-taken photos only
**Real result**: Listings with professional photos got 2-3x more bookings.
**Why it won**: High-quality photos build trust and make spaces look more appealing. Photography was the single biggest factor in booking decisions.

**Murmur input**:
- Business type: Small vacation rental / Airbnb host
- Question: "Should I invest in professional photos for my rental listing, or are my phone photos good enough?"
- Expected: Strong consensus toward professional photos, especially from first-time-visitor personas

**Score**: _pending_

---

## 7. Amazon — One-Click Checkout

**Source**: Widely documented; Brad Stone's "The Everything Store"
**What was tested**: One-click purchasing vs. standard multi-step checkout
**Real result**: One-click massively increased purchase completion rates. Amazon patented it.
**Why it won**: Every additional step in checkout is a chance for the customer to reconsider. Removing friction removes abandonment.

**Murmur input**:
- Business type: Small online store
- Question: "Should we let returning customers buy with a single click using their saved payment info, or keep our current 3-step checkout?"
- Expected: Most personas prefer convenience, but some may flag security concerns

**Score**: _pending_

---

## 8. Basecamp (37signals) — Long-Form vs. Short-Form Landing Page

**Source**: Signal v. Noise blog / conversion optimization case studies
**What was tested**: A long, detailed landing page explaining Basecamp's features vs. a short, minimalist page with just headline + signup
**Real result**: The long-form page increased signups by 37.5%.
**Why it won**: For a product that requires understanding (project management), more information helped visitors self-qualify and build confidence.

**Murmur input**:
- Business type: Small SaaS / local service with a website
- Question: "Should our main page be a short, clean design with just our tagline and a 'Get Started' button, or a longer page that explains what we do in detail?"
- Variant A: Short and minimal
- Variant B: Long and detailed
- Expected: Depends on business type — this is a good "it depends" case for calibration

**Score**: _pending_

---

## 9. Walmart — Page Load Speed

**Source**: Walmart Labs engineering blog / web performance case studies
**What was tested**: Impact of page load time on conversion (every 1 second improvement)
**Real result**: For every 1 second improvement in page load time, conversions increased by up to 2%.
**Why it won**: Slow pages frustrate users. Mobile users especially abandon slow sites.

**Murmur input**:
- Business type: Small e-commerce store
- Question: "Our website takes 5 seconds to load. If we invested in making it load in 2 seconds, would customers buy more?"
- Expected: This tests whether the swarm can reason about UX/technical factors. Personas should mention frustration with slow loading.

**Score**: _pending_

---

## 10. Groove — Personal vs. Corporate Tone in Emails

**Source**: Groove HQ blog (Alex Turnbull's growth series)
**What was tested**: Sending onboarding emails with a personal, conversational tone (from the CEO) vs. a polished corporate tone
**Real result**: Personal emails had 2x higher response rates and significantly better retention.
**Why it won**: Small business customers value authenticity and personal connection. Corporate-sounding emails from a small company feel dishonest.

**Murmur input**:
- Business type: Small SaaS or local service business
- Question: "Should our customer emails come from me personally (casual tone, my name) or from the company (professional tone, company name)?"
- Variant A: Personal tone from owner
- Variant B: Professional corporate tone
- Expected: Strong win for A, especially with small-business-loyal personas

**Score**: _pending_

---

## Holdout Cases (DO NOT tune prompts against these)

Cases 8, 9, and 10 are designated holdout cases. We will not look at these results when iterating on prompts. They are reserved for final validation only.

## Summary Table

| # | Company | Test | Expected Winner | Swarm Prediction | Score |
|---|---------|------|----------------|-----------------|-------|
| 1 | Booking.com | Urgency messaging | With urgency | _pending_ | _pending_ |
| 2 | Netflix | Personalized artwork | Personalized | _pending_ | _pending_ |
| 3 | HubSpot | Remove landing page nav | Remove nav | _pending_ | _pending_ |
| 4 | Etsy | Free shipping threshold | Free shipping | _pending_ | _pending_ |
| 5 | Obama Campaign | Button text | "Learn More" | _pending_ | _pending_ |
| 6 | Airbnb | Professional photos | Professional | _pending_ | _pending_ |
| 7 | Amazon | One-click checkout | One-click | _pending_ | _pending_ |
| 8 | Basecamp | Long vs short landing page | Long-form | _pending_ | _pending_ |
| 9 | Walmart | Page load speed | Faster = more sales | _pending_ | _pending_ |
| 10 | Groove | Personal vs corporate email | Personal | _pending_ | _pending_ |
