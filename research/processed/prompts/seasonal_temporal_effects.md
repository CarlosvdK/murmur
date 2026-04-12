# Seasonal & Temporal Effects: Calibration Instructions

When simulating customer behavior, account for the time dimension. Consumer decisions are not stable across hours, days, seasons, or calendar events. These temporal patterns are systematic and well-documented -- ignoring them produces unrealistic simulations.

## Seasonal Demand Patterns (Miron, "The Economics of Seasonal Cycles," MIT Press, 1996)

Consumer spending follows predictable seasonal cycles with amplitude of 15-30% above and below annual averages depending on category. Retail peaks in Q4 (holiday season accounts for 20-30% of annual retail revenue). Service businesses (restaurants, salons, fitness) show category-specific seasonality: restaurants peak in summer and December, gyms peak in January (30-40% of new memberships) and trough in summer, and salons peak before major holidays and prom/wedding season.

When simulating: adjust persona spending propensity and visit frequency based on the time of year the simulation targets. A January gym promotion should assume elevated new-member interest but also high churn risk (50-60% of January sign-ups cancel by March). A summer restaurant question should assume higher foot traffic but also more competition for discretionary dining spend.

## Day-of-Week Effects on Consumer Behavior (Berger & Fitzsimons, "Dogs on the Street, Pumas on Your Feet: How Cues in the Environment Influence Product Evaluation and Choice," Journal of Marketing Research, 2008)

Environmental cues prime purchasing behavior by day of week. Berger & Fitzsimons demonstrated that incidental exposure to related concepts (e.g., the color orange on Halloween) increased selection of conceptually related products by 15-25%. Retail spending follows weekly cycles: Saturday is the highest-volume day (18-22% of weekly sales), Monday is the lowest (8-12%), and Friday shows elevated impulse purchasing (+15-20% above weekday average).

When simulating: if the simulation specifies a day of week or time context, adjust persona behavior accordingly. Weekend personas should show more leisure-oriented, browsing, and impulse behavior. Weekday personas should show more goal-directed, efficient purchasing patterns.

## Time-of-Day Decision Making (Baumeister, Vohs, & Tice, "The Strength Model of Self-Control," Current Directions in Psychological Science, 2007; Danziger, Levav, & Avnaim-Pesso, "Extraneous Factors in Judicial Decisions," Proceedings of the National Academy of Sciences, 2011)

Decision quality degrades throughout the day as cognitive resources deplete. In Danziger et al.'s study of 1,112 parole decisions, favorable rulings dropped from 65% after a meal break to nearly 0% just before the next break. In consumer contexts, impulse purchases increase by 20-30% in late afternoon and evening compared to morning. Self-control depletion also increases preference for default options and reduces comparison shopping effort.

When simulating: personas making decisions in the evening or after a long day should show increased impulsivity, reduced price sensitivity, greater reliance on defaults, and lower effort in evaluating alternatives. Morning personas should be more deliberate and price-conscious. This effect is strongest for discretionary purchases and weakest for habitual, routine buying.

## Holiday and Event Spending Psychology (Waldfogel, "The Deadweight Loss of Christmas," American Economic Review, 1993)

Gift purchases systematically destroy 10-33% of their value -- recipients value gifts at 65-90 cents per dollar spent. This occurs because givers lack full information about recipient preferences. Despite this inefficiency, holiday spending is socially compulsory: 85-95% of consumers participate in holiday gift-giving regardless of financial stress. Holiday spending is also heavily front-loaded by higher-income consumers and back-loaded (last-minute) by lower-income consumers.

When simulating: personas during holiday periods should show elevated spending with reduced price sensitivity (willingness to pay 15-25% premium for convenience and availability). Gift-buying personas should exhibit preference for "safe" choices (popular brands, gift cards) over personalized selections, especially when buying for acquaintances vs. close relationships.

## Weather Effects on Consumer Spending (Murray, Di Muro, Finn, & Popkowski Leszczyc, "The Effect of Weather on Consumer Spending," Journal of Retailing and Consumer Services, 2010; Busse, Pope, Pope, & Silva-Risso, "The Psychological Effect of Weather on Car Purchases," Quarterly Journal of Economics, 2015)

Sunshine increases general spending by 5-12% through mood elevation. Murray et al. found sunny days increase willingness to pay for both hedonic and utilitarian products, but the effect is 2x stronger for hedonic goods. In Busse et al.'s study of 40 million car transactions, convertible sales increased 25% on sunny days and 4WD sales increased 15% on snowy days -- buyers over-projected current weather conditions onto future utility.

When simulating: if weather context is available, adjust persona mood and purchasing patterns accordingly. Rainy/cold weather should increase demand for comfort goods and delivery services while decreasing foot traffic to physical locations by 10-20%. Personas should project current conditions forward -- a simulation set during a heat wave should show personas overvaluing cooling-related features and undervaluing winter-related ones.
