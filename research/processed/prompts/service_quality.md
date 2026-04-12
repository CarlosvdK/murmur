# Service Quality: Calibration Instructions

When simulating customer reactions to service experiences, apply the following empirically-grounded effects. These are not optional flavor -- they are systematic patterns that real customers exhibit consistently across studies.

## SERVQUAL Dimensions (Parasuraman, Zeithaml & Berry, "SERVQUAL: A Multiple-Item Scale for Measuring Consumer Perceptions of Service Quality," Journal of Retailing, 1988)

Service quality is evaluated across five dimensions: reliability (delivering promised service dependably), assurance (employee knowledge and courtesy inspiring trust), tangibles (physical facilities, equipment, appearance), empathy (caring individualized attention), and responsiveness (willingness to help promptly). Parasuraman et al. found that reliability is consistently the most important dimension across industries, explaining 30-35% of overall service quality perception. When simulating:
- Reliability failures (broken promises, inconsistent service) should produce 2-3x stronger negative reactions than tangible shortcomings (dated decor, plain uniforms).
- Empathy matters most for high-contact services (healthcare, salons, restaurants). Weight it 1.5-2x higher for these contexts.
- Tangibles matter most for first-time customers who lack other quality signals. Repeat customers discount tangibles by 30-40%.
- Responsiveness expectations vary by industry. A persona waiting 30 seconds for fast food perceives the same frustration as waiting 5 minutes at a sit-down restaurant or 24 hours for an email response.

## Customer Effort and Loyalty (Dixon, Freeman & Toman, "Stop Trying to Delight Your Customers," Harvard Business Review, 2010; Dixon, Toman & DeLisi, "The Effortless Experience," Portfolio/Penguin, 2013)

Reducing effort drives loyalty more reliably than exceeding expectations. Dixon et al. found that 96% of customers who experience high-effort service interactions become disloyal, compared to only 9% of those with low-effort experiences. Delight has minimal incremental loyalty impact -- moving from "met expectations" to "exceeded expectations" increases loyalty by only 2-4%. When simulating:
- A high-effort experience (transferred 3+ times, repeating information, multiple contacts to resolve) should produce a 70-80% probability of the persona reducing future patronage.
- Reducing friction (one-call resolution, proactive communication) increases retention by 15-20% but does NOT produce proportional positive word-of-mouth.
- Personas should rarely cite "delight" as a reason for loyalty. Instead, they stay because "it was easy" or "they never gave me a reason to leave."
- High-effort experiences produce 2-3x more negative word-of-mouth than low-effort experiences produce positive word-of-mouth.

## Service Failure and Recovery (Smith, Bolton & Wagner, "A Model of Customer Satisfaction with Service Encounters Involving Failure and Recovery," Journal of Marketing Research, 1999; Maxham & Netemeyer, "A Longitudinal Study of Complaining Customers' Evaluations of Multiple Service Failures and Recovery Efforts," Journal of Marketing, 2002)

How a business responds to failure matters more than the failure itself. Smith et al. found that the combination of speed, apology, and compensation explains 60-75% of recovery satisfaction. Maxham & Netemeyer showed that excellent recovery from a first failure can increase satisfaction above pre-failure levels (the "service recovery paradox"), but this effect disappears entirely after a second failure -- satisfaction drops 40-60% below baseline. When simulating:
- A first-time failure with fast, empathetic recovery should leave the persona at 90-110% of pre-failure satisfaction.
- A second failure, regardless of recovery quality, should drop satisfaction to 40-60% of baseline. The persona now expects failure.
- No recovery attempt after a failure reduces satisfaction by 50-70% and triggers negative word-of-mouth in 60-80% of personas.
- Compensation should match the failure type: process failures need speed and apology; outcome failures need tangible compensation (discount, replacement).

## Wait Time and Queue Management (Taylor, "Waiting for Service: The Relationship Between Delays and Evaluations of Service," Journal of Marketing, 1994; Pruyn & Smidts, "Effects of Waiting on the Satisfaction with the Service," International Journal of Research in Marketing, 1998)

Perceived wait time matters more than actual wait time, and they diverge significantly. Taylor found that unexplained waits feel 2-3x longer than explained waits. Pruyn & Smidts showed that occupied time (reading material, music, visible progress) is perceived as 25-40% shorter than unoccupied time. Satisfaction drops nonlinearly -- the first 5 minutes of unexpected waiting reduce satisfaction by 10-15%, but minutes 10-15 reduce it by an additional 25-30%. When simulating:
- Unoccupied, unexplained waits should produce 2-3x more frustration than occupied, explained waits of the same duration.
- After the persona's expected wait time is exceeded, each additional minute produces accelerating dissatisfaction (nonlinear curve).
- Providing a time estimate, even if imprecise, reduces perceived wait by 20-30%. Uncertainty about duration is the primary stressor.
- High-time-pressure personas (lunch break, appointment after) should exhibit 2-3x higher wait sensitivity than low-pressure personas (browsing on weekend).

## Employee-Customer Interaction Quality (Hartline & Ferrell, "The Management of Customer-Contact Service Employees," Journal of Marketing, 1996; Liao & Chuang, "A Multilevel Investigation of Factors Influencing Employee Service Performance and Customer Outcomes," Academy of Management Journal, 2004)

Frontline employees are the single largest driver of service satisfaction. Hartline & Ferrell found that employee self-efficacy and adaptability explain 35-45% of customer-perceived service quality. Liao & Chuang showed that employee service performance (friendliness, attentiveness, competence) directly predicts customer satisfaction and loyalty, with a one-standard-deviation improvement in employee performance increasing customer satisfaction by 20-30%. When simulating:
- A rude or dismissive employee encounter should reduce overall business satisfaction by 40-60%, regardless of product quality.
- Genuinely warm, attentive service increases willingness to pay by 10-15% and repeat visit probability by 20-25%.
- Consistency matters: one excellent employee surrounded by mediocre ones creates a 30-40% satisfaction variance between visits, which erodes trust.
- High-Agreeableness personas are less likely to complain about poor service but equally likely to stop visiting. Low-Agreeableness personas complain loudly but may still return if the complaint is handled well.

## Subscription and Membership Retention (Bolton, "A Dynamic Model of the Duration of the Customer's Relationship with a Continuous Service Provider," Marketing Science, 1998; Ascarza, Iyengar & Schleicher, "In Pursuit of Enhanced Customer Retention Management," International Journal of Research in Marketing, 2016)

Subscription churn follows predictable patterns. Bolton found that customers' cumulative satisfaction and payment equity (perceived value relative to price) are the strongest churn predictors, with a 1-point drop in satisfaction on a 7-point scale increasing churn probability by 15-20%. Ascarza et al. showed that targeted retention interventions reduce churn by 10-15% on average, but poorly targeted interventions (discounts to already-loyal customers) waste budget with near-zero impact. When simulating:
- Churn risk peaks at subscription months 2-3 and again at months 11-13 (around renewal). Apply a 1.5-2x churn multiplier at these windows.
- A price increase on a subscription should trigger 15-25% churn probability, modulated by tenure: long-tenure subscribers (2+ years) churn at 60-70% of the base rate.
- Proactive outreach to at-risk personas (usage declining, support tickets increasing) reduces churn by 10-15%. Reactive retention offers after cancellation attempt recover only 5-10%.
- Personas who forget they are subscribed and then discover a charge exhibit high anger -- 40-50% will churn immediately and 30% will dispute the charge.

## Net Promoter Score Validity (Reichheld, "The One Number You Need to Grow," Harvard Business Review, 2003; Keiningham, Cooil, Andreassen & Aksoy, "A Longitudinal Examination of Net Promoter and Firm Revenue Growth," Journal of Marketing, 2007)

NPS is widely used but empirically limited. Reichheld claimed NPS was the single best predictor of growth, but Keiningham et al.'s rigorous longitudinal study found NPS is NOT a superior predictor of revenue growth compared to other satisfaction measures -- its predictive power is roughly equivalent to ACSI scores and overall satisfaction ratings. NPS explains only 10-20% of variance in growth rates. When simulating:
- A "promoter" persona (9-10 rating) actually recommends the business to others only 25-35% of the time. Stated intent to recommend overshoots actual behavior by 2-3x.
- "Passive" personas (7-8 rating) are the most volatile -- they are 3-4x more likely to switch to a competitor than promoters but rarely voice complaints.
- "Detractor" personas (0-6 rating) generate 2-4x more word-of-mouth than promoters, and negative WOM is weighted more heavily by recipients.
- Use NPS as a rough temperature check, not a precision instrument. A 5-point swing in NPS for a small business could be noise, not signal.

## Omnichannel Customer Behavior (Verhoef, Kannan & Inman, "From Multi-Channel Retailing to Omni-Channel Retailing," Journal of Retailing, 2015; Neslin, Grewal, Leghorn, Shankar, Teerling, Thomas & Verhoef, "Challenges and Opportunities in Multichannel Customer Management," Journal of Service Research, 2006)

Customers who use multiple channels are substantially more valuable but harder to satisfy. Verhoef et al. found that omnichannel customers spend 15-30% more than single-channel customers. Neslin et al. showed that channel-switching behavior (research online, purchase in-store, or vice versa) is now the dominant pattern for 60-70% of customers, and inconsistencies between channels reduce satisfaction by 25-35%. When simulating:
- Personas should exhibit channel-switching: 60-70% will research on one channel and transact on another.
- Inconsistent pricing, inventory, or experience between channels should produce a 25-35% satisfaction penalty and erode trust.
- Omnichannel personas expect their history to follow them -- having to re-explain a problem when switching channels produces the same frustration as a service failure (40-50% satisfaction drop).
- Younger personas (18-35) are 2x more likely to exhibit channel-switching than older personas (55+), who tend to prefer a single familiar channel.
