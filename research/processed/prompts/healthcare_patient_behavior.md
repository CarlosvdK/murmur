# Healthcare & Patient Behavior: Calibration Instructions

When simulating patient and healthcare consumer behavior, apply the following research-backed patterns. Healthcare decisions involve heightened emotion, asymmetric information, and strong trust dynamics that differ fundamentally from retail purchasing.

## Patient Satisfaction Drivers (Cleary & McNeil, "Patient Satisfaction as an Indicator of Quality of Care," Inquiry, 1988; Sitzia & Wood, "Patient Satisfaction: A Review of Issues and Concepts," Social Science & Medicine, 1997)

Patient satisfaction is driven more by interpersonal factors than clinical outcomes. In Cleary & McNeil's review, the top predictors were: communication quality (r = 0.65), perceived empathy (r = 0.55), wait time (r = -0.45), and physical environment (r = 0.30). Clinical competence ranked lower -- not because it is unimportant, but because patients lack the expertise to evaluate it and instead use proxies.

Sitzia & Wood found that satisfaction scores are skewed positive: 80-90% of patients report being "satisfied" or "very satisfied" regardless of objective quality differences. Dissatisfaction is typically triggered by discrete negative events (being ignored, long unexplained waits) rather than gradual quality erosion.

When simulating: personas should evaluate healthcare primarily on communication, wait times, and feeling heard -- not on clinical metrics they cannot assess. Default satisfaction should be high unless a specific negative trigger is present.

## Health Literacy and Decision Making (Berkman, Sheridan, Donahue, Halpern, & Crotty, "Low Health Literacy and Health Outcomes: An Updated Systematic Review," Annals of Internal Medicine, 2011)

Approximately 36% of US adults have basic or below-basic health literacy. Low health literacy is associated with 1.5-3x higher rates of hospitalization, lower medication adherence (40-50% compliance vs. 70-80% for high-literacy patients), and 50% lower likelihood of using preventive services. The effect is strongest among older adults, non-native English speakers, and lower-income populations.

When simulating: a substantial minority of personas should struggle to understand medical instructions, medication regimens, and insurance information. These personas are not less intelligent -- they lack domain-specific vocabulary and framework. They rely more heavily on provider recommendations and social networks for health decisions.

## Doctor-Patient Communication (Stewart, "Effective Physician-Patient Communication and Health Outcomes: A Review," Canadian Medical Association Journal, 1995; Ha & Longnecker, "Doctor-Patient Communication: A Review," Ochsner Journal, 2010)

Stewart's meta-analysis found that effective physician communication improves patient outcomes across multiple measures: symptom resolution improved by 25-30%, pain management improved by 20%, and emotional health improved by 15-20%. The average physician interrupts patients within 18-23 seconds of the patient beginning to speak.

When simulating: personas who feel their provider listened to them and explained things clearly should show higher treatment adherence (by 30-40%), greater willingness to return, and stronger word-of-mouth recommendation. Personas who felt rushed or unheard should show significantly lower adherence and higher likelihood of switching providers.

## Appointment Scheduling and No-Shows (Gupta & Denton, "Appointment Scheduling in Health Care: Challenges and Opportunities," IIE Transactions, 2008; Daggy, Lawley, Willis, & Thayer, "Using No-Show Modeling to Improve Clinic Performance," Health Informatics Journal, 2010)

Medical appointment no-show rates range from 15-30% across practice types, with higher rates in primary care (23-34%) than specialty care (12-18%). Key predictors: lead time (appointments booked >2 weeks out have 2x the no-show rate), prior no-show history (strongest single predictor, 3-4x risk), age (younger patients no-show more), and transportation access.

When simulating: personas should exhibit realistic no-show behavior scaled to their demographics and circumstances. Reminder interventions (text/call) reduce no-shows by 25-40%. Personas with longer wait-to-appointment times should show higher cancellation and no-show probability.

## Patient Choice of Provider (Victoor, Delnoij, Westert, & Rademakers, "Determinants of Patient Choice of Healthcare Providers: A Scoping Review," BMC Health Services Research, 2012)

Patients choose providers based on: proximity/convenience (cited by 50-70%), physician reputation/recommendation (40-60%), insurance acceptance (30-50%), and online reviews (15-30%, rising sharply among younger demographics). Only 12-25% of patients actively compare providers before choosing -- the majority rely on defaults (nearest provider, referral from current provider, family recommendation).

When simulating: most personas should choose healthcare providers through passive channels (proximity, referral, insurance network) rather than active comparison shopping. Only high-education, high-engagement personas should exhibit systematic provider comparison behavior.

## Telemedicine Adoption (Kruse, Karem, Shifflett, Vegi, Ravi, & Brooks, "Evaluating Barriers to Adopting Telemedicine Worldwide: A Systematic Review," Journal of Telemedicine and Telecare, 2017)

Telemedicine adoption barriers include: technology literacy (cited in 75% of studies), perceived impersonality (50%), concerns about examination quality (45%), and privacy concerns (30%). Adoption is highest for follow-up visits (60-70% acceptance) and lowest for initial consultations (20-30% acceptance). Age is the strongest demographic predictor: adults under 45 accept telemedicine at 2-3x the rate of adults over 65.

When simulating: personas should show age- and tech-literacy-dependent acceptance of telehealth options. Even accepting personas should express some preference for in-person visits for new conditions, complex issues, or situations requiring physical examination. Post-pandemic familiarity has shifted baseline acceptance upward by approximately 15-20 percentage points across all demographics.
