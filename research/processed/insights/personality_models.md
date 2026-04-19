# Personality Models -- Key Insights

## Insight from: mccrae1992introduction (Big Five / OCEAN)
**Finding:** Five broad personality traits -- Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism -- capture most stable individual differences in behaviour. The Five-Factor Model is replicated across languages, cultures, and measurement methods.
**Strength:** Very High (most-cited personality framework, hundreds of thousands of citations)
**Application:** Persona diversity without the Big Five tends to collapse into templated archetypes. Explicitly varying OCEAN traits across the swarm produces meaningfully different reactions to the same question.
**Prompt fragment:** "Use OCEAN-inspired trait language in persona generation. Diverse personas require diverse positions on Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism -- not just different demographics."

## Insight from: mehl2006personality
**Finding:** Extraversion predicts word-of-mouth behaviour. High-E personas are 2-3x more likely to tell others about an experience (positive or negative) than low-E personas of similar satisfaction.
**Strength:** High (*Journal of Personality and Social Psychology*)
**Application:** When simulating viral or referral behaviour, Extraversion is a stronger predictor than satisfaction level. A high-E moderately-satisfied persona generates more mentions than a low-E very-satisfied persona.
**Prompt fragment:** "Word-of-mouth is an Extraversion function, not a satisfaction function. High-E personas talk about businesses 2-3x more than low-E personas of the same satisfaction."

## Insight from: roberts2007power
**Finding:** Conscientiousness is the single strongest personality predictor of life outcomes: health, longevity, income, relationship stability, and financial prudence. In consumer contexts, C predicts budget adherence, delayed gratification, subscription cancellation discipline, and research-before-purchase behaviour.
**Strength:** Very High (Roberts et al. meta-analysis; foundational)
**Application:** High-C personas exhibit less hyperbolic discounting (~30-40% less steep), resist impulse purchases, and cancel forgotten subscriptions. Low-C personas are the opposite: impulse-driven, subscription-hoarders, less price-comparison behaviour.
**Prompt fragment:** "Conscientiousness is the strongest consumer predictor. High-C: budgets, research, cancels subscriptions. Low-C: impulse buys, auto-renews, rarely cancels."

## Insight from: costa1992neo
**Finding:** Neuroticism amplifies emotional reactions in both directions and is the main driver of complaint behaviour. High-N personas rate the same experience more negatively than low-N personas and are more likely to post negative reviews.
**Strength:** High (*Neo-PI-R*, widely validated)
**Application:** The negative-review population overrepresents high-N customers. Aggregate review scores are pulled negative by disproportionate high-N participation. When calibrating review bias, factor this in -- it is part of why silent-majority correction matters.
**Prompt fragment:** "Negative reviewers overrepresent high-Neuroticism customers. High-N reactions are amplified (both positive and negative) -- not just unhappier, but more intense in either direction."

## Insight from: deyoung2013openness
**Finding:** Openness predicts novelty-seeking and willingness to try new products, services, or formats. High-O personas are early adopters; low-O personas stick with what they know and resist novelty.
**Strength:** High (DeYoung; widely replicated in marketing research)
**Application:** When simulating reactions to new features, new menu items, redesigns, or rebrands, Openness is the trait that swings the most. Low-O-heavy customer bases reject novelty even if it is objectively better.
**Prompt fragment:** "Openness is the novelty trait. High-O personas accept new formats eagerly; low-O personas actively resist novelty and prefer the familiar even when it is worse."

## Insight from: graziano2007agreeableness
**Finding:** Agreeableness predicts compliance with social norms and willingness to accept unfavourable terms to maintain harmony. High-A personas under-report dissatisfaction in person but follow through on private defection (switching silently without complaint).
**Strength:** High (Graziano; consumer complaint literature)
**Application:** High-A personas are the classic "silent leavers" -- they rate polite surveys positive and then stop visiting. This is a major driver of the Murmur silent-majority story: high-A customers are underrepresented in complaints and overrepresented in silent defection.
**Prompt fragment:** "High-Agreeableness personas are silent leavers: they will not complain, will rate politely, and will defect without warning. This is the silent-majority signature in many businesses."

## Insight from: john2008paradigm
**Finding:** Big Five traits are stable but contextually expressed. The same persona shows different behaviour at work vs. at home, with family vs. strangers, in high-stakes vs. low-stakes decisions. Trait level sets the range; context drives the specific behaviour.
**Strength:** Very High (*Handbook of Personality*, meta-syntheses)
**Application:** Persona generation should set OCEAN levels once but allow context-specific expression. A high-C persona can be impulsive about small comfort purchases while being disciplined about large investments.
**Prompt fragment:** "Traits are stable but contextually expressed. Set OCEAN levels once, then vary how they express across different decision contexts (small vs. large stakes, social vs. solo, familiar vs. novel)."

## Insight from: lucas2000extraversion
**Finding:** Extraversion-Introversion predicts which channels customers engage through. High-E customers prefer in-person, phone, video; low-E customers prefer text, self-service, async. The same product sold through the "wrong" channel for the customer's E-level converts substantially worse.
**Strength:** High (Lucas; replicated in digital channel research)
**Application:** When simulating channel changes (e.g., removing phone support, pushing chat-only, adding in-store kiosks), the impact depends heavily on the customer base's Extraversion distribution. Low-E-heavy bases welcome self-service; high-E-heavy bases resent it.
**Prompt fragment:** "Channel preference is an Extraversion function. High-E personas want human channels; low-E personas want self-service. A channel change hits one side harder than the other."
