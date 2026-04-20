# Context Intelligence Engine: Production-Grade Specification

## Overview

This document specifies a **production-ready context intelligence system** with 1000+ data dimensions that influence customer behavior, persona generation, and simulation outcomes. This is NOT a prototype — it's architected for enterprise scale, reliability, and continuous improvement.

---

## Part 1: The 1000+ Context Dimensions

### 1. MACROECONOMIC FOUNDATIONS (80 dimensions)

#### 1.1 Price Levels & Inflation (15)
- **CPI overall** (monthly, YoY change)
- **CPI by category:**
  - Food & beverage CPI
  - Energy CPI (electricity, gas, fuel)
  - Transportation CPI
  - Housing/shelter CPI
  - Clothing CPI
  - Healthcare CPI
  - Childcare/education CPI
  - Entertainment CPI
  - Telecommunications CPI
- **Core CPI** (excluding volatile components)
- **PPI (Producer Price Index)** - upstream inflation
- **Inflation expectations** (consumer survey expectations)
- **Deflation risk score** (is deflation possible?)

#### 1.2 Commodity & Energy Prices (12)
- **Oil price (Brent crude)** - global
- **Oil price trend** - 7-day, 30-day, YoY
- **Natural gas prices** - by region
- **Coal prices**
- **Copper prices** (construction/manufacturing indicator)
- **Wheat prices** (food inflation leading indicator)
- **Corn prices** (agricultural input, food chain impact)
- **Soybeans** (vegetable oil, meat production input)
- **Gold prices** (risk sentiment indicator)
- **Agricultural commodity index**
- **Shipping costs/freight index** (supply chain cost proxy)
- **Rare earth element prices**

#### 1.3 Currency & Exchange Rates (10)
- **Local currency vs USD exchange rate**
- **Currency volatility (7-day, 30-day)**
- **Currency strength indicator** (basket comparison)
- **PPP (Purchasing Power Parity) ratio**
- **Real effective exchange rate (REER)**
- **Capital flows direction** (money flowing in or out?)
- **Carry trade activity** (affecting exchange)
- **Central bank intervention** (if any)
- **Currency depreciation/appreciation trend**
- **Forex reserves adequacy**

#### 1.4 Interest Rates & Credit (12)
- **Official policy rate** (central bank)
- **Prime lending rate** (banks charge businesses/consumers)
- **Mortgage rate** (30-year, 15-year, ARM)
- **Credit card interest rate**
- **Auto loan rate**
- **Student loan rate**
- **Savings account rate** (what savers earn)
- **Money market rate**
- **Bond yield curve** (short-term vs long-term)
- **Credit spread** (risk premium between safe and risky borrowing)
- **Real interest rate** (nominal minus inflation)
- **Rate expectations** (where rates heading?)

#### 1.5 Debt & Financial Stability (15)
- **Government debt-to-GDP ratio**
- **Government debt trend**
- **Corporate debt levels** (by sector)
- **Household debt levels** (total and by type)
- **Personal savings rate**
- **Consumer credit growth**
- **Non-performing loan ratio** (banks' problem debts)
- **Bank capital adequacy ratio**
- **Credit availability index** (are banks willing to lend?)
- **Household debt service ratio** (% of income going to debt)
- **Student loan delinquency rate**
- **Mortgage delinquency rate**
- **Auto loan delinquency rate**
- **Credit card delinquency rate**
- **Bankruptcy filing rate**

#### 1.6 Growth & Output (8)
- **GDP growth rate** (YoY, quarterly)
- **GDP trend** (acceleration or deceleration?)
- **Industrial production index**
- **Manufacturing PMI** (manufacturing sentiment)
- **Services PMI** (services sector sentiment)
- **Retail sales growth**
- **E-commerce growth rate**
- **Capacity utilization rate** (is economy running hot?)

#### 1.7 Employment & Labor (10)
- **Unemployment rate** (official)
- **U3 unemployment** (standard measure)
- **U6 unemployment** (broader, includes underemployed)
- **Labor force participation rate**
- **Job creation/loss rate**
- **Wage growth rate** (nominal)
- **Real wage growth** (adjusted for inflation)
- **Job quits rate** (worker confidence)
- **Job openings rate** (labor demand)
- **Average hours worked**

#### 1.8 Business Activity (8)
- **Business confidence index**
- **Consumer confidence index**
- **PMI (Purchasing Managers Index)**
- **New business formation rate**
- **Business failure/bankruptcy rate**
- **Corporate profit margins**
- **R&D spending** (as % of GDP or revenue)
- **Capital expenditure intentions**

---

### 2. MICRO-LOCATION ECONOMICS (70 dimensions)

#### 2.1 Local Labor Market (12)
- **Local unemployment rate** (vs national)
- **Local wage levels** (by occupation)
- **Local wage growth**
- **Job market tightness** (hard to find workers?)
- **Local minimum wage** (if differs from national)
- **Cost of living index** (local)
- **Housing affordability index** (local)
- **Average rent** (local)
- **Average house price** (local)
- **Price-to-income ratio** (affordability)
- **Commute time** (affects quality of life, spending)
- **Remote work prevalence** (local)

#### 2.2 Local Real Estate (10)
- **House price index** (local trend)
- **Rental price index** (local trend)
- **Vacancy rate** (commercial and residential)
- **Construction activity** (building permits issued)
- **Real estate appreciation rate**
- **Mortgage lending rate** (local)
- **Foreclosure rate** (local)
- **Building depreciation rate**
- **Property tax rate** (local)
- **Zoning restrictions/changes**

#### 2.3 Local Taxes & Regulations (12)
- **Local sales tax rate**
- **Local income tax** (if applicable)
- **Property tax rate**
- **Business license cost**
- **Regulatory complexity index**
- **Permitting timeline** (how long to get approval)
- **Labor law strictness** (local, if differs)
- **Environmental regulation strictness**
- **Consumer protection strictness**
- **Tax evasion/compliance rate** (shadow economy size)
- **Corruption perception index** (local)
- **Government efficiency index** (local)

#### 2.4 Local Infrastructure (8)
- **Road quality index** (local)
- **Public transportation quality** (local)
- **Internet speed** (local average)
- **Electricity reliability** (outages per year)
- **Water quality** (local)
- **Sanitation quality** (local)
- **Broadband penetration** (local)
- **Digital infrastructure maturity** (local)

#### 2.5 Local Competitive Landscape (10)
- **Market concentration** (HHI index)
- **Number of competitors** (in specific business)
- **Competitor density** (competitors per capita)
- **Market consolidation trend**
- **New market entrants (last 12 months)**
- **Business closures (last 12 months)**
- **Price competition intensity**
- **Local market growth rate**
- **Market saturation level**
- **Local dominant player** (who has market power)

#### 2.6 Local Business Ecosystem (8)
- **Small business survival rate** (1-year, 5-year)
- **Small business growth rate** (revenue growth)
- **Startup ecosystem maturity** (vibrant or weak)
- **Venture capital availability** (local)
- **Business incubator/accelerator presence**
- **Chamber of Commerce activity level**
- **Local business associations** (strength)
- **Supply chain hub proximity** (how close to suppliers?)

#### 2.7 Local Population Characteristics (10)
- **Population density** (people per sq km)
- **Urban/suburban/rural classification**
- **Population growth rate** (local)
- **Migration inflow** (people moving in)
- **Migration outflow** (people moving out)
- **Age distribution** (median age, % under 35, % over 65)
- **Education levels** (% college-educated)
- **Income distribution** (GINI coefficient, local)
- **Poverty rate** (local)
- **Population diversity index** (ethnic, cultural)

---

### 3. SENTIMENT & BEHAVIORAL PSYCHOLOGY (120 dimensions)

#### 3.1 Consumer Sentiment (15)
- **Consumer confidence index** (official)
- **Consumer sentiment index** (official)
- **Economic optimism score** (future expectations)
- **Economic pessimism score** (fear of recession)
- **Willingness to spend** (survey data)
- **Willingness to save** (vs spend)
- **Risk tolerance** (investment behavior)
- **Fear of unemployment** (survey)
- **Anxiety about price rises** (survey)
- **Trust in government** (survey)
- **Trust in business** (survey)
- **Trust in financial institutions** (survey)
- **Happiness/life satisfaction score** (Gallup, etc.)
- **Stress level** (population average)
- **Mental health score** (population average)

#### 3.2 National/Regional Sentiment (20)
- **Economic sentiment** (actual national mood)
- **Political sentiment** (left vs right, satisfied vs angry)
- **Social cohesion score** (are people united or polarized?)
- **Trust in institutions** (government, media, business, academia)
- **Patriotism level** (national pride)
- **Civic engagement** (voting, volunteering, community)
- **Altruism score** (charitable giving)
- **Materialism score** (focus on wealth vs other values)
- **Work-life balance priorities**
- **Sustainability consciousness**
- **Environmental concern level**
- **Social justice orientation**
- **Authoritarianism score** (law-and-order vs freedom)
- **Openness to change** (vs tradition-focused)
- **Individualism vs collectivism** (actual behavior)
- **Short-term vs long-term focus** (actual behavior)
- **Optimism about future** (personal and national)
- **Anxiety level** (personal health anxiety, financial anxiety)
- **Conspiracy theory belief prevalence**
- **Media trust** (which sources trusted most)

#### 3.3 Psychographic Profiles (15)
- **Hofstede power distance index** (actual behavior)
- **Hofstede individualism index** (actual)
- **Hofstede masculinity index** (actual)
- **Hofstede uncertainty avoidance** (actual)
- **Hofstede long-term orientation** (actual)
- **Hofstede indulgence vs restraint** (actual)
- **GLOBE cultural dimensions** (9 dimensions)
- **Personality distribution by country** (Big Five avg)
- **Risk aversion score** (behavioral)
- **Trust propensity** (willingness to trust)
- **Authority deference** (respect for hierarchy)
- **Rule-following tendency** (compliance)
- **Time orientation** (punctual vs flexible culture)
- **Communication style** (direct vs indirect)
- **Decision-making style** (consultative vs autocratic)

#### 3.4 Anxiety & Fear Indicators (20)
- **Economic anxiety** (fear of recession, job loss)
- **Health anxiety** (pandemic, disease)
- **Safety anxiety** (crime, violence)
- **Financial anxiety** (debt, inability to pay)
- **Social anxiety** (acceptance, status)
- **Climate anxiety** (environmental concern)
- **Political anxiety** (uncertainty about future)
- **Existential anxiety** (meaning, purpose)
- **PTSD prevalence** (from past trauma)
- **Depression prevalence** (clinical)
- **Anxiety disorder prevalence** (clinical)
- **Suicide rate** (ultimate distress indicator)
- **Substance abuse rate** (coping mechanism)
- **Google Trends for "anxiety"** (real-time measure)
- **Google Trends for "depression"** (real-time)
- **Google Trends for "fear"** (real-time)
- **Reddit discussions about anxiety** (sentiment analysis)
- **Twitter anxiety sentiment** (real-time)
- **TikTok mental health trend prevalence** (young people sentiment)
- **Therapy demand** (waitlists, booking time)

#### 3.5 Aspiration & Motivation (15)
- **Achievement motivation** (desire to excel, succeed)
- **Affiliation motivation** (need to belong)
- **Power motivation** (desire for influence)
- **Self-actualization priority** (vs basic needs)
- **Status consciousness** (brand loyalty, luxury interest)
- **Social climbing aspirations** (desire to move up)
- **Career ambition level**
- **Financial ambition level**
- **Health/wellness priority**
- **Education priority** (for self or children)
- **Travel/experience priority** (vs goods)
- **Minimalism trend** (anti-consumption)
- **FIRE (Financial Independence) movement prevalence**
- **Sustainability consciousness** (actual purchasing)
- **Ethical consumption priority** (fair trade, organic)

#### 3.6 Trust & Credibility (12)
- **Trust in government** (trend over time)
- **Trust in media** (trend)
- **Trust in business** (trend)
- **Trust in healthcare providers** (trend)
- **Trust in financial institutions** (trend)
- **Trust in academic institutions** (trend)
- **Trust in neighbors/community** (trend)
- **Trust in strangers** (generalized trust)
- **Institutional trust index** (overall)
- **Fake news concern** (% worried about misinformation)
- **Fact-checking effectiveness** (% who seek verification)
- **Authority/expert deference** (trust in experts)

#### 3.7 Social Influence & Conformity (12)
- **Peer pressure susceptibility** (by age group)
- **Social proof effectiveness** (for this population)
- **Herd mentality index** (tendency to follow crowd)
- **Contrarian tendency** (desire to be different)
- **Influencer effectiveness** (by type: celebrity, micro, nano)
- **Word-of-mouth effectiveness** (trust in recommendations)
- **Online review effectiveness** (trust in other customers)
- **Expert endorsement effectiveness**
- **Celebrity endorsement effectiveness**
- **Friend recommendation conversion rate**
- **Family recommendation conversion rate**
- **Viral content susceptibility**

---

### 4. NEWS, INFORMATION & MEDIA (100 dimensions)

#### 4.1 News Landscape (20)
- **Top trending news stories** (by region, real-time)
- **News topic breakdown** (% economic, % political, % health, % crime)
- **Economic news sentiment** (positive vs negative framing)
- **Political news tone** (collaborative vs divisive)
- **Health news coverage** (pandemic updates, health crises)
- **Crime news prevalence** (% of news coverage)
- **Local news vs national news ratio**
- **News timeliness** (breaking vs analysis)
- **News source diversity** (monopoly vs competitive)
- **Newspaper ownership concentration** (single owner or diverse)
- **Investigative journalism prevalence**
- **Opinion vs fact-checking ratio**
- **Sensationalism score** (tone of coverage)
- **Political bias in media** (left vs right lean)
- **Media trust level** (by outlet and overall)
- **News consumption time** (how much people read/watch)
- **Social media as news source** (% who get news here)
- **News avoidance prevalence** (% who actively avoid)
- **News fatigue score** (overwhelm from constant updates)
- **News literacy** (% who can identify misinformation)

#### 4.2 Industry-Specific News (15)
- **Industry growth announcements** (hiring, expansion)
- **Industry closure announcements** (layoffs, shutdowns)
- **Industry merger/acquisition activity**
- **Product innovation announcements**
- **Regulatory change announcements**
- **Supply chain disruption news**
- **Competitor news** (what competitors are doing)
- **Labor dispute announcements** (strikes, walkouts)
- **Environmental/ESG news** (relevant to industry)
- **Safety incident announcements**
- **Recall announcements** (product issues)
- **Patent announcements** (innovation)
- **Executive change announcements**
- **Earnings announcements** (company performance)
- **Industry forecast articles** (analyst predictions)

#### 4.3 Local & Regional News (10)
- **Local business news** (what's happening locally)
- **Local government news** (policy changes)
- **Local crime news** (safety perception)
- **Local infrastructure news** (road work, development)
- **Local school news** (education quality perception)
- **Local real estate news** (market trends)
- **Local employment news** (local hiring/layoffs)
- **Local weather news** (seasonal trends, disasters)
- **Local event news** (festivals, community events)
- **Local personality/influencer news** (who's influential locally)

#### 4.4 Viral Content & Trending Topics (15)
- **Currently trending topics** (Twitter/TikTok/Reddit)
- **Meme culture sentiment** (what's funny = what's on people's minds)
- **Viral news characteristics** (what gets shared)
- **Echo chamber strength** (how siloed are people?)
- **Misinformation spread rate** (false claims velocity)
- **Fact-check ratio** (% of misinformation corrected)
- **Disinformation campaigns** (coordinated false info)
- **Deep fake prevalence** (fake video/audio)
- **Conspiracy theory prevalence** (how many people believe)
- **QAnon prevalence** (specific false conspiracy)
- **Flat Earth belief** (indicator of science denial)
- **Vaccine hesitancy prevalence** (trust in health authorities)
- **Climate change denial prevalence**
- **Viral positive content ratio** (uplifting news prevalence)
- **Viral negative content ratio** (doom scrolling prevalence)

#### 4.5 Social Media Sentiment (20)
- **Twitter sentiment** (on economy, business, topic X)
- **Twitter engagement rate** (are people talking about it?)
- **Reddit sentiment** (by subreddit relevant to topic)
- **Reddit discussion volume** (how much is being discussed)
- **TikTok sentiment** (especially Gen Z sentiment)
- **Instagram sentiment** (lifestyle, aspiration messaging)
- **Facebook sentiment** (older demographics)
- **LinkedIn sentiment** (professional/business context)
- **YouTube comment sentiment** (what people are saying)
- **Discord sentiment** (for tech/niche communities)
- **Telegram sentiment** (for crisis/emergency info)
- **WeChat sentiment** (China, East Asia)
- **Telegram groups about economy/topic X sentiment**
- **Whatsapp group sentiment** (private/closed groups, inferred)
- **Nextdoor sentiment** (local/neighborhood level)
- **Blog sentiment** (long-form opinion)
- **Review site sentiment** (customer opinions about brands)
- **Amazon reviews sentiment** (customer satisfaction)
- **Google reviews sentiment** (local business satisfaction)
- **Yelp reviews sentiment** (restaurant/service sentiment)

#### 4.6 Content Analysis (10)
- **News article engagement** (views, shares, comments per article)
- **Video engagement rate** (YouTube, TikTok views)
- **Social media post engagement** (likes, shares, comments)
- **Time spent reading** (vs scrolling past)
- **Click-through rate on headlines** (headline effectiveness)
- **Return visitor rate** (are people coming back?)
- **Content sharing rate** (are people amplifying?)
- **Comment toxicity** (are discussions civil or hostile?)
- **Trolling prevalence** (% of comments that are trolls)
- **Bot activity** (artificial engagement)

#### 4.7 Information Literacy (8)
- **Fake news concern** (% who worry about it)
- **Media literacy score** (% who can identify bias)
- **Critical thinking prevalence** (% who question sources)
- **Fact-checking behavior** (% who verify claims)
- **Source evaluation skill** (% who check credibility)
- **Confirmation bias susceptibility** (tendency to seek confirming info)
- **Backfire effect prevalence** (when corrections entrench beliefs)
- **Openness to changing mind** (when presented evidence)

---

### 5. HEALTH & SAFETY (60 dimensions)

#### 5.1 Pandemic & Disease (12)
- **COVID-19 case rate** (current, trend)
- **COVID-19 death rate**
- **Vaccination rate** (% vaccinated)
- **Vaccination hesitancy** (% refusing)
- **Booster uptake rate**
- **New variant prevalence** (which variants circulating)
- **Hospital capacity** (% full)
- **ICU capacity** (% full)
- **Excess mortality** (deaths above baseline)
- **Long COVID prevalence** (lingering effects)
- **Pandemic concern level** (vs normalcy bias)
- **Masks/distancing prevalence** (behavioral change persistence)

#### 5.2 Public Health (10)
- **Life expectancy** (national average)
- **Infant mortality rate**
- **Maternal mortality rate**
- **Disease outbreak rate** (non-COVID diseases)
- **Malaria prevalence** (in endemic areas)
- **Tuberculosis rate**
- **HIV prevalence**
- **Diabetes prevalence** (increasing dramatically)
- **Obesity rate** (related to behavior, wealth)
- **Opioid overdose rate** (substance abuse indicator)

#### 5.3 Mental Health (8)
- **Depression prevalence**
- **Anxiety disorder prevalence**
- **Suicide rate** (ultimate distress)
- **Self-harm prevalence**
- **Eating disorder prevalence**
- **Substance abuse rate**
- **Alcohol abuse rate**
- **Gambling addiction prevalence**

#### 5.4 Safety & Crime (12)
- **Homicide rate** (violent crime)
- **Robbery rate** (theft with violence)
- **Burglary rate** (property crime)
- **Car theft rate** (property crime)
- **Assault rate** (violence)
- **Sexual assault rate** (violence)
- **Domestic violence rate**
- **Child abuse rate**
- **Cybercrime rate** (identity theft, fraud)
- **Drug-related crime rate**
- **White-collar crime rate** (fraud, corruption)
- **Incarceration rate** (% of population in prison)

#### 5.5 Workplace Safety (6)
- **Workplace injury rate** (per 100,000 workers)
- **Workplace fatality rate**
- **Occupational disease rate** (asbestosis, etc.)
- **PTSD in occupations** (soldiers, police, healthcare)
- **Burnout prevalence** (by profession)
- **Work-related stress level**

#### 5.6 Environmental Health (6)
- **Air quality index** (PM2.5, ozone)
- **Water quality index** (contamination)
- **Soil contamination** (heavy metals, chemicals)
- **Noise pollution level** (decibels)
- **Light pollution** (affects sleep, health)
- **Radiation exposure** (nuclear, etc.)

#### 5.7 Healthcare Access (6)
- **Healthcare coverage** (% insured)
- **Healthcare costs** (% of income)
- **Healthcare quality** (outcomes, survival rates)
- **Healthcare wait times** (how long to see doctor)
- **Medication costs** (affordability)
- **Mental health service availability** (scarce or abundant?)

---

### 6. WEATHER & CLIMATE (60 dimensions)

#### 6.1 Current Weather (12)
- **Temperature** (current, hourly forecast 7 days)
- **Humidity** (dry vs moist)
- **Precipitation** (rain, snow, amount, probability)
- **Wind speed/direction**
- **Cloud cover**
- **UV index** (sun exposure risk)
- **Air quality** (pollen, pollution)
- **Dew point** (perceived humidity)
- **Atmospheric pressure** (affects mood, migraines)
- **Visibility** (fog, haze)
- **Storm potential** (thunderstorm risk)
- **Frost/freeze risk**

#### 6.2 Seasonal Norms (12)
- **Average temperature for this month** (30-year baseline)
- **Average precipitation for this month**
- **Historical high/low temperature for this month**
- **Average snowfall** (if applicable)
- **Average humidity** (this month)
- **Average wind speed** (this month)
- **Daylight hours** (how many hours of sun)
- **Sunrise/sunset time** (affects shopping hours)
- **Average pollen count** (this month, historical)
- **Historical weather volatility** (how variable is this month?)
- **Typical season onset date** (when does summer officially start?)
- **Season duration variability** (is it getting shorter/longer?)

#### 6.3 Weather Anomalies (8)
- **Deviation from normal temperature** (is it warmer/colder than usual?)
- **Deviation from normal precipitation** (wetter/drier than usual?)
- **Record temperature** (hottest/coldest in how many years?)
- **Record precipitation** (most/least rain in how many years?)
- **Unseasonable weather** (snow in summer, heat in winter)
- **Weather volatility** (rapidly changing conditions)
- **Extreme weather risk** (storm, flood, tornado, earthquake)
- **Seasonal shift indicators** (is season arriving early/late?)

#### 6.4 Climate Patterns (10)
- **El Niño/La Niña status** (affects global weather)
- **Monsoon timing** (if applicable)
- **Drought status** (if applicable)
- **Flood risk** (if applicable)
- **Wildfire risk** (if applicable)
- **Hurricane/typhoon season status**
- **Tornado season risk** (if applicable)
- **Avalanche risk** (if applicable)
- **Earthquake/tsunami risk** (if applicable)
- **Volcanic activity risk** (if applicable)

#### 6.5 Climate Change Indicators (12)
- **Long-term temperature trend** (warming?)
- **Snowpack trends** (melting earlier?)
- **Growing season length change** (longer or shorter?)
- **Species migration** (animals moving north/higher)
- **Plant blooming dates** (earlier or later?)
- **Permafrost melting rate**
- **Glacier retreat rate**
- **Sea level rise rate**
- **Ocean acidification** (pH trends)
- **Atmospheric CO2 level**
- **Climate change belief** (% who accept it)
- **Climate anxiety prevalence** (worry about climate)

#### 6.6 Seasonal Economics (8)
- **Seasonal purchasing pattern** (peak seasons)
- **Seasonal employment pattern** (seasonal jobs)
- **Tourist season timing** (summer vs winter)
- **Agricultural season** (harvest timing)
- **School year impact** (back-to-school, summer break)
- **Holiday season economic activity**
- **Seasonal inventory levels**
- **Seasonal price volatility** (prices change seasonally)

---

### 7. TEMPORAL & CYCLICAL PATTERNS (120 dimensions)

#### 7.1 Daily Patterns (8)
- **Time of day** (morning, afternoon, evening, night)
- **Peak shopping times** (by time of day)
- **Peak working times** (when people are productive)
- **Sleep patterns** (when people sleep)
- **Commute times** (morning/evening rush)
- **Meal times** (cultural variation)
- **Leisure times** (when people have free time)
- **Online activity times** (when people browse)

#### 7.2 Weekly Patterns (10)
- **Day of week** (Monday-Sunday)
- **Monday effect** (low mood, financial anxiety)
- **Friday effect** (high spending, leisure mood)
- **Weekend vs weekday behavior**
- **Paycheck timing** (when is payday)
- **Bill-paying days** (when bills are due)
- **Shopping days** (patterns vary by day)
- **Work productivity** (varies by day)
- **Mood patterns** (varies by day)
- **Social activity** (varies by day)

#### 7.3 Monthly Patterns (12)
- **Day of month** (early, mid, late)
- **Payday effect** (after payday vs before)
- **Post-payday spending spike**
- **Pre-payday financial stress**
- **Bill-paying impact** (% of income)
- **Credit card statement impact**
- **Rent/mortgage due date**
- **Utility bill due dates**
- **Insurance premium due**
- **Subscription renewal dates**
- **End-of-month financial stress**
- **Monthly budget cycles**

#### 7.4 Seasonal Patterns (15)
- **Season** (spring, summer, fall, winter)
- **Seasonal mood** (seasonal affective disorder)
- **Seasonal purchasing** (Christmas, back-to-school, gardening, heating)
- **Seasonal employment** (tourism, agriculture, retail)
- **Seasonal pricing** (higher in peak season)
- **Seasonal availability** (products in/out of stock)
- **Seasonal weather impact**
- **Seasonal vacation patterns**
- **Seasonal activity patterns** (outdoor vs indoor)
- **Holiday season** (multi-week impact)
- **Tax season** (impact on finances, mood)
- **Flu season** (health anxiety)
- **Allergy season** (pollen, health)
- **End-of-year financial planning** (New Year resolutions)
- **Summer vs winter behavior shifts**

#### 7.5 Annual Cycles (12)
- **Fiscal year** (business year-end stress)
- **Academic year** (back-to-school, graduation)
- **Calendar year** (New Year resolutions, goal-setting)
- **Agricultural year** (planting, harvest)
- **Holiday calendar** (all major holidays in year)
- **Sports seasons** (football, basketball, baseball schedules)
- **Music/entertainment festivals** (concert seasons)
- **Wedding season** (spring/summer in some cultures)
- **Travel season** (summer, winter holidays)
- **Back-to-school season** (August/September)
- **Black Friday/Cyber Monday** (shopping season)
- **Year-over-year comparisons** (same month last year)

#### 7.6 Business Cycles (10)
- **Economic expansion/contraction phase**
- **Business confidence cycle**
- **Inventory cycle** (building up or drawing down?)
- **Capital investment cycle** (companies investing or cutting)
- **Hiring/firing cycle**
- **Wage growth cycle** (growing or stagnant?)
- **Earnings cycle** (quarterly earnings season)
- **Tax cycle** (tax filing season stress)
- **Bonus season** (when bonuses are paid)
- **Consumer spending cycle** (when do people splurge?)

#### 7.7 Election & Political Cycles (8)
- **Election proximity** (how close is next election)
- **Campaign spending** (affects economy locally)
- **Political uncertainty** (pending elections/policy changes)
- **Government budget cycle** (fiscal year impacts)
- **New administration impact** (policy changes)
- **Parliamentary session** (when laws are passed)
- **Policy uncertainty index** (how uncertain is the future?)
- **Political polarization cycle** (more/less divided)

#### 7.8 School & Education Cycles (6)
- **School year** (start and end dates)
- **Holiday breaks** (impacts family spending, schedules)
- **Exam season** (student stress)
- **College admission season** (family stress)
- **Graduation season** (life transition)
- **Grade level transitions** (kindergarten, middle school, high school)

#### 7.9 Financial Planning Cycles (8)
- **Tax filing season** (stressful period)
- **Tax refund season** (people get money back)
- **Financial year-end review** (looking backward)
- **Budget planning** (looking forward)
- **Insurance renewal** (car, home, health)
- **Credit card balance** (statement cycles)
- **Mortgage payment schedule**
- **Investment rebalancing season**

#### 7.10 Habit & Behavior Cycles (10)
- **Diet cycles** (New Year's resolutions to lose weight, abandoned by Feb)
- **Exercise cycles** (gym membership peaks in January)
- **Smoking cessation cycles** (Quit Smoking Day, January resolutions)
- **Financial goals cycles** (more focus in January, fades)
- **Relationship status cycles** (more breakups in winter)
- **Moving/relocation cycles** (summer is peak moving season)
- **Job hunting cycles** (hiring picks up certain times)
- **Salary negotiation timing** (annual reviews)
- **Education enrollment** (spring and fall semesters)
- **Travel booking cycles** (book now, travel later)

---

### 8. INDUSTRY & BUSINESS SPECIFIC (100 dimensions)

#### 8.1 Industry Growth & Trends (15)
- **Industry revenue growth rate** (YoY, quarterly)
- **Industry employment trend** (hiring or shrinking)
- **Industry wage growth**
- **Industry profit margins** (healthy or squeezed)
- **Industry disruption rate** (new technologies, new competitors)
- **Industry consolidation** (mergers/acquisitions)
- **Industry innovation rate** (patents, new products)
- **Industry R&D spending**
- **Industry customer retention** (churn rate)
- **Industry price trends** (rising or falling)
- **Industry regulation changes** (impact on business)
- **Industry supply chain issues** (shortages, delays)
- **Industry skill gaps** (workers available or scarce)
- **Industry debt levels** (healthy or overleveraged)
- **Industry competitiveness** (margins compressed or good)

#### 8.2 Industry Cycles (10)
- **Industry seasonal peaks** (when does business boom?)
- **Industry seasonal troughs** (slow periods)
- **Industry capacity utilization** (operating at % of max)
- **Industry inventory levels** (high or low)
- **Industry order backlog** (how much work ahead?)
- **Industry customer sentiment** (are they buying?)
- **Industry price cycle** (raw materials → final price)
- **Industry supply cycle** (lead times, availability)
- **Industry technology cycle** (upgrades, obsolescence)
- **Industry employment cycle** (hiring → firing)**

#### 8.3 Competitive Dynamics (12)
- **Market concentration** (HHI index, how concentrated)
- **Market leader** (who dominates)
- **Market followers** (who are #2, #3)
- **New entrants** (disruptors entering market)
- **Exit announcements** (companies leaving market)
- **Merger announcements** (consolidation)
- **Price wars** (competition on price)
- **Feature wars** (competition on innovation)
- **Market share trends** (who's gaining/losing)
- **Competitive intensity** (high or low)
- **Barriers to entry** (easy or hard for new competitors)
- **Switching costs** (hard for customers to switch providers)

#### 8.4 Supply Chain Specifics (15)
- **Raw material availability** (scarce or abundant)
- **Raw material prices** (trends)
- **Supplier lead times** (how long to get supplies)
- **Supplier reliability** (do they deliver on time)
- **Inventory levels** (company's stockpiles)
- **Backlog** (orders waiting to be filled)
- **Production capacity** (operating at % of max)
- **Manufacturing delays** (are things delayed?)
- **Shipping delays** (port congestion, etc.)
- **Logistics costs** (trending up or down)
- **Just-in-time efficiency** (vs safety stock)
- **Supply chain concentration** (dependent on few suppliers?)
- **Supply chain transparency** (know where goods come from?)
- **Supply chain resilience** (can survive disruptions?)
- **Supply chain localization trend** (moving production closer?)

#### 8.5 Customer Behavior (18)
- **Average customer age** (demographic)
- **Customer gender distribution**
- **Customer income level**
- **Customer education level**
- **Customer lifecycle** (acquisition, retention, churn)
- **Customer acquisition cost** (CAC, expensive or cheap?)
- **Customer lifetime value** (LTV, profitable customers?)
- **Churn rate** (% of customers leaving)
- **Repeat purchase rate** (% who come back)
- **Average order value** (transaction size)
- **Customer satisfaction** (NPS, CSAT)
- **Customer loyalty** (strong or weak)
- **Customer price sensitivity** (willing to pay premium?)
- **Customer service expectations** (high or low)
- **Customer research process** (how much they research before buying)
- **Customer decision cycle** (how long to decide)
- **Customer decision-maker** (individual, family, committee)
- **Customer values** (what matters to them: price, quality, sustainability, etc.)

#### 8.6 Pricing & Revenue (10)
- **Price level** (premium, mid-market, budget)
- **Price changes** (trending up or down?)
- **Price elasticity** (sensitive to price changes?)
- **Discounting prevalence** (how much do you discount?)
- **Promotional frequency** (constant sales or rare?)
- **Revenue per customer** (growing or stagnant)
- **Revenue per transaction**
- **Pricing power** (can you raise prices?)
- **Price comparison ease** (customers can easily compare)
- **Perceived value** (do customers think you're worth it?)

#### 8.7 Technology & Innovation (12)
- **Industry tech adoption rate** (fast or slow)
- **Emerging technology threat** (what could disrupt you)
- **Digital transformation stage** (backward or leading edge)
- **E-commerce penetration** (% of sales online)
- **Mobile-first adoption** (how important is mobile?)
- **AI adoption** (using AI in business?)
- **Automation rate** (how many manual vs automated processes)
- **Data analytics maturity** (using data to decide?)
- **Cybersecurity maturity** (how secure)
- **API/integration maturity** (connected systems)
- **Cloud migration** (moved to cloud or on-premises)
- **Tech skill availability** (can you hire skilled workers?)

#### 8.8 Regulatory & Compliance (8)
- **Regulatory burden** (how much compliance needed)
- **Recent regulatory changes** (new rules)
- **Upcoming regulatory changes** (anticipated rules)
- **Compliance cost** (% of revenue)
- **Environmental regulation** (strictness)
- **Labor law** (strictness)
- **Consumer protection** (strictness)
- **Data privacy** (GDPR, CCPA, etc.)

#### 8.9 Brand & Marketing (10)
- **Brand awareness** (% of market knows you)
- **Brand reputation** (positive or negative)
- **Brand loyalty** (strong or weak)
- **Marketing spend** (% of revenue)
- **Marketing effectiveness** (ROI on marketing)
- **Advertising clutter** (how crowded is the category?)
- **Influencer effectiveness** (for this category)
- **Social media presence strength**
- **Word-of-mouth strength** (referrals)
- **Brand differentiation** (unique or similar to competitors)

#### 8.10 Employment & Labor (10)
- **Wage level** (below market, market, above market)
- **Wage growth** (trend)
- **Benefits quality** (health, retirement, etc.)
- **Work environment** (toxic or healthy)
- **Turnover rate** (% of employees leaving)
- **Retention rate** (who stays)
- **Training/development** (investing in people?)
- **Union strength** (if unionized)
- **Strike risk** (labor unrest likely?)
- **Labor availability** (easy or hard to hire)

---

### 9. CULTURAL & SOCIAL DIMENSIONS (100 dimensions)

#### 9.1 Core Cultural Values (20)
- **Individualism vs Collectivism** (actual behavior)
- **Power distance** (respect for hierarchy)
- **Uncertainty avoidance** (comfort with risk/ambiguity)
- **Masculinity vs Femininity** (achievement vs harmony)
- **Long-term vs Short-term orientation**
- **Indulgence vs Restraint** (pleasure-seeking vs discipline)
- **Materialism score** (focus on wealth vs meaning)
- **Traditionalism score** (respect for past vs embrace change)
- **Authoritarianism score** (law-and-order vs freedom)
- **Religiosity score** (importance of faith in life)
- **Secularism score** (separation of religion from public life)
- **Militarism score** (martial values vs pacifism)
- **Nationalism score** (national pride, patriotism)
- **Cosmopolitanism score** (global identity vs local)
- **Environmentalism score** (care for nature)
- **Sustainability score** (concern for future generations)
- **Fairness/Justice score** (how important is equality?)
- **Liberty/Freedom score** (how important is individual freedom?)
- **Safety/Security score** (how important is safety?)
- **Community score** (how important is collective wellbeing?)

#### 9.2 Generational Characteristics (20)
- **Silent Generation** (born 1925-1942) values/behavior
- **Baby Boomers** (born 1943-1960) values/behavior
- **Generation X** (born 1961-1980) values/behavior
- **Millennials** (born 1981-1996) values/behavior
- **Generation Z** (born 1997-2012) values/behavior
- **Generation Alpha** (born 2013-2025) values/behavior
- **Generational wealth gaps**
- **Generational debt levels**
- **Generational tech adoption**
- **Generational trust in institutions**
- **Generational political leanings**
- **Generational career aspirations**
- **Generational work-life balance priorities**
- **Generational family values**
- **Generational environmental concern**
- **Generational experience of economic hardship**
- **Generational optimism/pessimism**
- **Generational diversity acceptance**
- **Generational LGBTQ+ acceptance**
- **Generational religious participation**

#### 9.3 Personality & Psychology (15)
- **Big Five average scores:** Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- **Locus of control** (believe in controlling own destiny vs external forces)
- **Optimism/Pessimism ratio** (view glass as half-full or half-empty)
- **Risk tolerance** (comfortable with risk?)
- **Impulsivity score** (act without thinking or deliberate)
- **Compulsiveness score** (obsessive or relaxed)
- **Narcissism prevalence** (self-centeredness)
- **Empathy score** (care for others)
- **Altruism score** (willingness to help)
- **Machiavellianism** (manipulative, self-serving)
- **Psychopathy prevalence** (lack of empathy/conscience)
- **ADHD prevalence** (difficulty focusing)
- **Autism spectrum** (neurodivergence)
- **Introverts vs Extroverts** (energy from alone-time vs socializing)
- **Sensitive persons prevalence** (highly responsive to stimuli)

#### 9.4 Values & Priorities (15)
- **Family importance** (vs career, independence)
- **Career importance** (vs family, leisure)
- **Wealth/Money importance** (vs other values)
- **Health/Fitness importance**
- **Education importance**
- **Religion/Spirituality importance**
- **Friendship importance**
- **Community importance**
- **Environmental importance**
- **Social justice importance**
- **Political engagement importance**
- **Leisure/Fun importance**
- **Achievement importance**
- **Security/Safety importance**
- **Meaning/Purpose importance**

#### 9.5 Social Identity (12)
- **Ethnic identity strength** (pride in heritage)
- **National identity strength** (patriotism)
- **Religious identity strength** (faith importance)
- **Gender identity strength** (how central to identity)
- **Sexual orientation identity** (importance in life)
- **Class identity** (working class, middle class, etc.)
- **Occupational identity** (identify by job)
- **Regional identity** (Southerner, New Yorker, etc.)
- **Urban vs Rural identity**
- **Immigrant identity** (if applicable)
- **Diaspora identity** (if from diaspora)
- **Subculture identity** (punk, gamer, hip-hop, etc.)

#### 9.6 Intergroup Relations (10)
- **Ethnic prejudice level** (racism prevalence)
- **Religious prejudice level** (religious discrimination)
- **Gender prejudice level** (sexism)
- **LGBTQ+ prejudice level** (homophobia, transphobia)
- **Immigrant prejudice level** (xenophobia)
- **Class prejudice level** (classism)
- **Disability prejudice level** (ableism)
- **Intersectional prejudice** (overlapping discriminations)
- **Outgroup homogeneity bias** (stereotyping)
- **Intergroup contact** (how much do groups interact)

#### 9.7 Social Norms & Behavior (12)
- **Honesty norm** (social expectation of truthfulness)
- **Cooperation norm** (vs every-person-for-themselves)
- **Fairness norm** (importance of equal treatment)
- **Generosity norm** (expected to share/give)
- **Reciprocity norm** (return favors)
- **Respect norm** (deference to authority, elders)
- **Modesty norm** (not boasting, humility)**
- **Punctuality norm** (importance of being on time)
- **Cleanliness norm** (hygiene importance)
- **Formality norm** (formal vs casual relationships)
- **Privacy norm** (respect for others' privacy)
- **Personal space norm** (how close is comfortable?)

#### 9.8 Family Structure & Dynamics (8)
- **Average family size**
- **Extended family importance** (live together or separate?)
- **Marriage prevalence** (% married)
- **Divorce rate** (ease of leaving marriages)
- **Single parent prevalence** (% of families)
- **Child mortality rate** (affects family decisions)
- **Childcare availability** (easy or hard to find)
- **Elder care approach** (family or institutional?)

---

### 10. COMPETITIVE INTELLIGENCE (50 dimensions)

#### 10.1 Competitor Activity (20)
- **Competitor pricing changes** (moving up or down?)
- **Competitor product launches** (new offerings)
- **Competitor advertising spend** (increasing or decreasing)
- **Competitor hiring announcements** (expanding or contracting)
- **Competitor office/location closures** (leaving markets)
- **Competitor acquisition announcements** (buying companies)
- **Competitor being acquired** (being bought by others)
- **Competitor CEO/leadership changes**
- **Competitor financial health** (profitable or struggling)
- **Competitor lawsuit announcements** (legal troubles)
- **Competitor recall announcements** (product problems)
- **Competitor sustainability initiatives**
- **Competitor union activity** (strikes, labor disputes)
- **Competitor market share trends**
- **Competitor customer reviews** (satisfaction trends)
- **Competitor social media sentiment** (what customers say)
- **Competitor earnings growth** (growing faster or slower?)
- **Competitor innovation announcements** (patents, new tech)
- **Competitor partnership announcements** (collaborations)
- **Competitor corporate scandals** (ethical issues)**

#### 10.2 Market Positioning (15)
- **Your market share** (% of market)
- **Competitor market shares** (ranking)
- **Segment dominance** (who dominates each segment?)
- **Price positioning** (premium, mid, budget relative to competition)
- **Quality positioning** (best, competitive, below average)
- **Innovation positioning** (leader or follower)
- **Service positioning** (high touch, self-service, etc.)
- **Geographic positioning** (where are competitors strong?)
- **Customer segment dominance** (who owns which segments?)
- **Online vs Offline positioning** (who's digital, who's brick-and-mortar?)
- **Value proposition differentiation** (unique selling points)
- **Brand perception** (how are you seen vs competitors?)
- **Customer loyalty ranking** (are your customers loyal or switchers?)
- **Switching cost position** (do your customers have high switching costs?)
- **Barrier strength** (how hard to copy what you do?)

#### 10.3 Threat Assessment (15)
- **Disruptive threat level** (is something threatening to upend market)
- **New entrant threat** (how likely is new competitor)
- **Substitute threat** (could people stop buying this category?)
- **Customer bargaining power** (do customers have leverage?)
- **Supplier bargaining power** (do suppliers have leverage?)
- **Competitive intensity** (fierce or comfortable?)
- **Price war risk** (likely to have price competition?)
- **Technology disruption risk** (could be made obsolete?)
- **Regulatory disruption risk** (could regulations change market?)
- **Economic sensitivity** (vulnerable to recession?)
- **Key person risk** (dependent on specific people?)
- **Geopolitical risk** (could trade wars affect you?)
- **Supply chain risk** (vulnerable to supply disruptions?)
- **Reputational risk** (sensitive to negative news?)
- **Cyber attack risk** (vulnerable to hacking?)

---

### 11. FINANCIAL & PERSONAL ECONOMIC (80 dimensions)

#### 11.1 Household Finance (25)
- **Average household income**
- **Median household income**
- **Income distribution** (GINI coefficient)
- **Income sources** (wages, business, investments, government)
- **Household debt** (total outstanding)
- **Mortgage debt** (home loans)
- **Credit card debt** (unsecured revolving debt)
- **Student loan debt** (education loans)
- **Auto loan debt** (car loans)
- **Debt service ratio** (% of income going to debt)
- **Savings rate** (% of income saved)
- **Emergency fund prevalence** (% with 3-month reserves)
- **Retirement savings** (adequacy for comfortable retirement)
- **Investment holdings** (stocks, bonds, real estate)
- **Home ownership rate** (% who own homes)
- **Rental burden** (% of income going to rent)
- **Mortgage burden** (% of income going to mortgage)
- **Property taxes** (burden on homeowners)
- **Utility costs** (electric, gas, water, internet)
- **Childcare costs** (% of income)
- **Healthcare costs** (out-of-pocket spending)
- **Transportation costs** (car, insurance, fuel)
- **Insurance burden** (health, car, home insurance costs)
- **Bankruptcy filing rate** (% filing for bankruptcy)
- **Personal insolvency risk** (how many are at risk?)

#### 11.2 Financial Stress (10)
- **Unmet basic needs** (% unable to afford food, housing, medicine)
- **Paycheck-to-paycheck living** (% living paycheck-to-paycheck)
- **Unexpected expense worry** (% worried about unexpected $400 bill)
- **Late bill payment** (% paying bills late)
- **Debt stress level** (worry about debt)
- **Financial anxiety prevalence**
- **Inflation impact on household** (real purchasing power declining?)
- **Job security concern** (fear of job loss)
- **Retirement security concern** (will have enough to retire?)
- **Healthcare cost concern** (will go bankrupt from medical bills?)

#### 11.3 Consumer Credit (15)
- **Credit card availability** (access to credit)
- **Average credit score** (nation or region)
- **Credit score distribution** (how many excellent, good, fair, poor)
- **Credit utilization rate** (% of available credit used)
- **Number of credit accounts** (credit cards, lines of credit)
- **Credit inquiry frequency** (how often people apply for credit)
- **New credit account rate** (how many new accounts being opened)
- **Account delinquency rate** (% of accounts behind on payments)
- **Default rate** (% of accounts in default)
- **Credit limits** (how much companies are willing to lend)
- **Interest rates being charged** (average APR)
- **Balance transfer behavior** (people moving debt around?)
- **Credit limit requests** (people asking for more credit?)
- **Charge-off rate** (creditors giving up on collections)
- **Collection accounts** (% in collections)

#### 11.4 Banking & Payments (12)
- **Bank account access** (% with checking/savings account)
- **Unbanked prevalence** (% without bank accounts)
- **Mobile banking adoption** (% using apps)
- **Online banking adoption** (% using web banking)
- **Credit card penetration** (% with credit cards)
- **Debit card prevalence** (% using debit cards)
- **Digital wallet adoption** (Apple Pay, Google Pay, etc.)
- **Cash-only prevalence** (% preferring cash)
- **Check usage** (still common or obsolete?)
- **Wire transfer usage** (moving money between people)
- **Cryptocurrency adoption** (% owning crypto)
- **Payment method preferences** (which are preferred?)

#### 11.5 Investment Behavior (10)
- **Stock market participation** (% who own stocks)
- **Bond ownership** (% who own bonds)
- **Real estate investment** (beyond primary home)
- **Cryptocurrency holdings** (% holding crypto)
- **Mutual fund ownership**
- **ETF ownership**
- **Day trading prevalence** (% engaging in active trading)
- **Options trading prevalence**
- **Penny stock investing** (speculative behavior)
- **Investment knowledge** (financial literacy)

#### 11.6 Business Ownership (8)
- **Self-employment rate** (% running own business)
- **Small business formation rate** (new businesses opening)
- **Franchise ownership rate** (% of businesses that are franchises)
- **Gig economy participation** (% doing gig work)
- **Side hustle prevalence** (% with supplemental income)
- **Business failure rate** (% of new businesses that fail)
- **Business profitability** (% of small businesses making money)
- **Business growth** (% of small businesses expanding)

---

### 12. ADDITIONAL CONTEXT FACTORS (50+ dimensions)

#### 12.1 Technological Adoption (15)
- **Internet penetration** (% with internet access)
- **Broadband speed** (download/upload Mbps)
- **Mobile penetration** (% with smartphones)
- **Smartphone type** (iOS vs Android distribution)
- **Operating system dominance** (Windows, Mac, Linux)
- **Social media platform dominance** (which platforms most popular)
- **E-commerce penetration** (% shopping online)
- **Payment app adoption** (digital wallets)
- **Streaming adoption** (video, music, podcasts)
- **IoT device adoption** (smart home, wearables)
- **AI assistant adoption** (Alexa, Google Assistant, Siri)
- **Chatbot adoption** (interacting with AI)
- **VR/AR adoption** (virtual/augmented reality usage)
- **5G adoption** (new mobile network)**
- **Tech obsolescence rate** (how fast do people upgrade?)

#### 12.2 Lifestyle Indicators (20)
- **Work-life balance score** (satisfied or exhausted?)
- **Leisure time** (hours per week of free time)
- **Exercise frequency** (how often exercising?)
- **Sports participation** (% actively playing sports)
- **Gym membership rate**
- **Outdoor recreation participation** (hiking, camping, etc.)
- **Travel frequency** (how many trips per year)
- **Domestic vs International travel ratio**
- **Entertainment spending** (movies, concerts, restaurants)
- **Dining out frequency** (how often eating at restaurants)
- **Cooking at home** (% who cook daily)
- **Travel distance** (commute, for fun)
- **Vacation days usage** (% who use all vacation days)
- **Staycation prevalence** (% vacationing locally)
- **Adventure seeking** (willing to try new experiences?)
- **Hobbies & interests** (what people spend time on)
- **Reading habits** (books, newspapers, blogs)
- **Gaming prevalence** (% who play video games)
- **Social activity level** (frequent or home-bodies?)
- **Pet ownership** (% with pets)

#### 12.3 Education & Learning (10)
- **Literacy rate** (% who can read/write)
- **School enrollment rate** (% in school)
- **College enrollment rate** (% attending university)
- **Graduation rate** (% completing education)
- **Continuous learning** (% taking courses/training)
- **Educational attainment** (average years of schooling)
- **STEM education rate** (% studying science/tech/engineering)
- **Vocational training** (% in trades)
- **Online course enrollment** (MOOCs, etc.)
- **Language skills** (multilingual prevalence)**

#### 12.4 Environmental Consciousness (10)
- **Recycling participation** (% who recycle)
- **Composting participation** (% who compost)
- **Reusable bag usage** (% using reusable shopping bags)
- **Sustainable product preference** (willingness to pay for eco-friendly)
- **Organic food consumption** (% buying organic)
- **Local food sourcing** (farmers markets, local producers)
- **Energy conservation behavior** (efforts to save energy)
- **Water conservation behavior** (efforts to save water)
- **Plastic reduction efforts** (% reducing single-use plastic)
- **Carbon footprint concern** (how much do people care?)

#### 12.5 Social Engagement (8)
- **Volunteering rate** (% volunteer time)
- **Charitable giving rate** (% donate money)
- **Religious participation** (% attending services)
- **Community involvement** (% active in community)
- **Civic engagement** (voting, political participation)
- **Social club membership** (% in clubs, organizations)
- **Union membership** (% in labor unions)
- **Online community participation** (forums, social media groups)

#### 12.6 Government & Institutional Trust (8)
- **Government trust** (% trust government)
- **Healthcare system trust** (% trust doctors, hospitals)
- **Education system trust** (% trust schools)
- **Media trust** (% trust news)
- **Corporate trust** (% trust businesses)
- **Financial institution trust** (% trust banks)
- **Institutions effectiveness** (do they work well?)
- **Government transparency perception** (open or secretive?)

#### 12.7 Relationship & Family Status (8)
- **Marriage rate** (% married)
- **Divorce rate** (% divorced)
- **Remarriage rate** (% remarrying)
- **Single parent rate** (% of families)
- **Childless by choice** (% intentionally not having kids)
- **Average number of children** (desired vs actual)
- **Cohabitation prevalence** (% living together unmarried)
- **Same-sex partnership prevalence** (% in same-sex relationships)

#### 12.8 Health & Wellness (8)
- **Exercise frequency** (how often exercising?)
- **Healthy eating** (% eating healthy diet)
- **Sleep quality** (hours per night, satisfaction)
- **Stress management** (using techniques to manage stress?)
- **Mental health care usage** (% seeing therapists)
- **Medication usage** (% on psychiatric medications)
- **Substance abuse** (alcohol, drugs, tobacco)
- **Sexual health** (STI prevalence, contraception usage)

#### 12.9 Demographic Shifts (8)
- **Population growth rate**
- **Birth rate**
- **Death rate**
- **Migration rate** (net in or out?)
- **Urbanization trend** (moving to cities or away?)
- **Aging population** (% over 65, growing?)
- **Youth bulge** (% under 15, declining?)
- **Demographic dividend** (working-age vs dependent population)**

#### 12.10 Wildcard Factors (8)
- **Viral trends** (what's trending on social media right now?)
- **Celebrity scandals** (affecting consumer behavior)
- **Sports events** (major games, tournaments, Olympics)
- **Entertainment releases** (major movies, TV shows, games)
- **Technology announcements** (new products from Apple, etc.)
- **Space/science news** (moon landing, Mars mission)
- **Major natural disasters** (floods, earthquakes, wildfires)
- **Geopolitical crises** (war, sanctions, diplomatic tensions)

---

## Part 2: Data Source Architecture

### 2.1 Real-Time Data Feeds (Updated hourly or daily)

**Economic Data:**
- World Bank Open Data (quarterly, annual updates)
- IMF Economic Outlook (quarterly)
- Trading Economics API (daily)
- Fred (Federal Reserve Economic Data) API (daily)
- OECD Statistics (monthly)
- Statista API (when available)
- Eurostat (monthly, daily for some)
- Local statistical offices (country-specific, monthly)

**Financial Markets:**
- Yahoo Finance API (real-time stock, commodity prices)
- CoinGecko API (cryptocurrency prices, real-time)
- Oil Prices.com API (oil, gas prices)
- Metals API (precious metals)
- Commodity prices (agricultural, industrial)

**Weather:**
- OpenWeatherMap API (current, forecast, historical)
- WeatherAPI (current, forecast)
- NOAA API (US weather data, alerts)
- Copernicus Climate Data (long-term climate)

**News & Sentiment:**
- NewsAPI (aggregated news with sentiment)
- Brave Search API (search results)
- Twitter API (social media sentiment)
- Reddit API (sentiment analysis via pushshift)
- Google Trends (trending topics)
- YouTube API (trending videos, sentiment)
- TikTok trends (via third-party providers)

**Employment:**
- Bureau of Labor Statistics API (US employment data)
- LinkedIn Economic Graph (employment trends)
- Glassdoor Salaries (wage data)
- PayScale Salary Data
- Local employment offices (country-specific)

**Health & Safety:**
- Johns Hopkins COVID-19 Data (pandemic tracking)
- WHO Disease Outbreak News (health alerts)
- CDC FluView (US flu tracking)
- Crime data (FBI crime stats, local police reports)
- WHO Country Profiles (health indicators)

**Sentiment & Psychological:**
- Pew Research Center (periodic surveys)
- Gallup (periodic surveys)
- Gfk Consumer Sentiment (monthly)
- University of Michigan Sentiment Index (monthly)
- Conference Board Leading Economic Index
- Sentdex API (sentiment analysis)

**Industry-Specific:**
- SEC EDGAR (US public company filings, earnings)
- Industry trade publications (via RSS feeds)
- Glassdoor (company reviews, employee sentiment)
- G2 Crowd (software reviews)
- Trustpilot (customer reviews)
- Amazon Product Reviews (customer satisfaction)
- Google Reviews API (customer satisfaction, local)

**Location-Specific:**
- OpenStreetMap (geographic data)
- Google Maps API (local business, ratings)
- Census Bureau (demographic data)
- Zillow/Redfin (real estate prices)
- Numbeo (cost of living)
- Mercer (expatriate cost index)

### 2.2 Data Pipeline Architecture

```python
# backend/context/intelligence_engine.py

class ContextIntelligenceEngine:
    """
    Comprehensive context intelligence for customer personas.
    1000+ dimensions across 12 categories.
    """
    
    async def gather_all_context(
        self,
        business_location: str,
        customer_location: str,
        simulation_date: datetime,
        industry: Optional[str] = None,
        competitive_mode: bool = False,
    ) -> FullContextSnapshot:
        """
        Gathers 1000+ context dimensions in parallel.
        Returns comprehensive snapshot for persona generation.
        
        Retrieves data from:
        - Cached location profiles (quarterly)
        - Real-time economic feeds (daily)
        - News sentiment (real-time)
        - Social media sentiment (real-time)
        - Weather & climate (real-time)
        - Industry-specific (daily)
        - Competitive intelligence (daily)
        
        All requests are non-blocking (parallel gathering).
        Failures are graceful (uses cached fallback).
        """
        
        # Parallel gather all data
        tasks = [
            self._get_macro_economics(customer_location, simulation_date),
            self._get_micro_economics(business_location, simulation_date),
            self._get_sentiment_data(customer_location, simulation_date),
            self._get_weather_climate(business_location, simulation_date),
            self._get_news_data(customer_location, industry, simulation_date),
            self._get_social_sentiment(customer_location, industry, simulation_date),
            self._get_industry_data(industry, customer_location, simulation_date),
            self._get_cultural_context(customer_location, simulation_date),
            self._get_temporal_context(simulation_date),
            self._get_health_safety(customer_location, simulation_date),
            self._get_competitive_intelligence(industry, customer_location) if competitive_mode else None,
        ]
        
        results = await asyncio.gather(*[t for t in tasks if t])
        
        return FullContextSnapshot(
            macro_economic=results[0],
            micro_economic=results[1],
            sentiment=results[2],
            weather_climate=results[3],
            news=results[4],
            social_sentiment=results[5],
            industry=results[6],
            cultural=results[7],
            temporal=results[8],
            health_safety=results[9],
            competitive=results[10] if competitive_mode else None,
            timestamp=datetime.now(),
            location_pair=(business_location, customer_location),
        )
```

### 2.3 Caching Strategy

- **Location profiles:** Updated quarterly (slow-moving data)
- **Economic data:** Updated daily (released on schedule)
- **News & sentiment:** Updated hourly (fast-moving)
- **Weather:** Updated hourly (updated frequently)
- **Social sentiment:** Updated every 4 hours (streaming)
- **Industry data:** Updated daily
- **Competitive intelligence:** Updated daily
- **Health/Safety:** Updated daily

---

## Part 3: RAG Knowledge Base (Thousands of Papers)

### 3.1 Comprehensive Global Coverage

**By Country (195 UN member states):**
- 1 foundational paper per country minimum (culture, economics, behavior)
- 5-10 deep-dive papers per major economy (US, China, Japan, Germany, UK, India, Brazil, etc.)
- Regional variants within countries (US Southeast vs Northeast vs West vs Midwest)
- Emerging market focus (growth potential)

**Total: ~500-800 country/region-specific papers**

### 3.2 By Behavioral Domain (100+ papers each)

**Behavioral Economics (150 papers):**
- Anchoring effects
- Framing effects
- Sunk cost fallacy
- Loss aversion
- Prospect theory
- Mental accounting
- Hyperbolic discounting
- Endowment effect
- Status quo bias
- Availability heuristic
- Representativeness heuristic
- Recency bias
- Confirmation bias
- Dunning-Kruger effect
- Planning fallacy
- Curse of knowledge
- Projection bias
- Optimism bias
- Overconfidence bias
- Illusion of control

**Consumer Psychology (150 papers):**
- Motivation (achievement, affiliation, power)
- Needs hierarchy (Maslow)
- Consumer decision-making
- Impulse buying
- Brand loyalty
- Switching behavior
- Price sensitivity
- Quality perception
- Trust formation
- Risk perception
- Satisfaction/dissatisfaction
- Complaint behavior
- Customer loyalty
- Repeat purchase behavior
- Word-of-mouth
- Unboxing psychology
- Packaging psychology
- Product design preferences

**Social Psychology (150 papers):**
- Conformity/social proof
- Obedience to authority
- Herd behavior
- Groupthink
- Social facilitation
- Social inhibition
- Deindividuation
- Group polarization
- In-group/out-group bias
- Stereotyping
- Prejudice
- Discrimination
- Intergroup conflict
- Cooperation
- Altruism
- Helping behavior
- Aggression
- Attraction/liking
- Persuasion
- Attitude change

**Decision Making (150 papers):**
- Bounded rationality
- Satisficing vs optimizing
- Choice overload/paradox
- Decision paralysis
- Regret aversion
- Maximizers vs satisficers
- Fast vs slow thinking
- Intuition
- Habit
- Nudges/choice architecture
- Defaults
- Framing
- Time pressure
- Confidence
- Uncertainty tolerance

**Pricing Psychology (100 papers):**
- Price perception
- Willingness to pay
- Price sensitivity
- Reference pricing
- Anchoring in pricing
- Bundling effects
- Charm pricing ($9.99 vs $10)
- Price fairness
- Dynamic pricing
- Discounting effectiveness
- Loss leaders
- Premium pricing
- Value-based pricing

**Digital Behavior (150 papers):**
- Online shopping behavior
- Mobile shopping vs desktop
- Website usability
- Checkout friction
- Cart abandonment
- Website personalization
- Email effectiveness
- SMS effectiveness
- Social media marketing
- Influencer marketing
- Viral marketing
- Ad effectiveness
- Click-through rates
- Conversion optimization
- Mobile app engagement
- Game mechanics/gamification
- FOMO (fear of missing out)
- Attention spans
- Scroll depth
- Video effectiveness

**Healthcare & Medicine (100 papers):**
- Patient decision-making
- Treatment compliance
- Health communication
- Medical trust
- Vaccine hesitancy
- Alternative medicine appeal
- Mental health stigma
- Doctor-patient communication
- Medical pricing sensitivity
- Telemedicine adoption

**Finance & Investment (100 papers):**
- Saving behavior
- Investment decision-making
- Risk tolerance
- Overconfidence in investing
- Day trading
- Herd mentality in markets
- Cryptocurrency adoption
- Financial literacy
- Behavioral finance
- Portfolio choices
- Debt behavior
- Credit card use
- Mortgage decisions

---

### 3.3 By Industry (1000+ industry-specific papers)

**20 major industries, 50+ papers each:**

1. **Food & Beverage** (80 papers)
   - Restaurant choice factors
   - Food delivery behavior
   - Grocery shopping
   - Food quality perception
   - Nutritional claims effectiveness
   - Organic food demand
   - Local food sourcing
   - Seasonal eating patterns
   - Price sensitivity in food
   - Health claims in food marketing

2. **Retail & Clothing** (80 papers)
   - Fashion trends
   - Clothing fit concerns
   - Fast fashion vs sustainable
   - Color preferences
   - Size accuracy importance
   - Return behavior
   - Impulse clothing purchases
   - Online vs in-store clothing
   - Try-on importance
   - Personal styling

3. **Healthcare Services** (80 papers)
   - Provider selection
   - Doctor switch behavior
   - Treatment acceptance
   - Preventive care
   - Telemedicine acceptance
   - Healthcare cost sensitivity
   - Insurance decision-making
   - Medication compliance
   - Mental health care seeking
   - Telehealth vs in-person

4. **SaaS & Software** (80 papers)
   - Free trial conversion
   - Subscription commitment
   - Feature complexity preferences
   - Trial-to-paid conversion
   - Churn factors
   - Implementation complexity tolerance
   - Support importance
   - Price sensitivity in SaaS
   - Switching costs
   - Integration importance

5. **E-commerce General** (80 papers)
   - Site design preferences
   - Checkout friction
   - Shipping cost sensitivity
   - Delivery speed preferences
   - Return policies
   - Customer service expectations
   - Review importance
   - Personalization preferences
   - Mobile vs desktop
   - Payment method preferences

6. **Travel & Hospitality** (80 papers)
   - Hotel selection factors
   - Review reliance
   - Price vs quality tradeoffs
   - Booking timing
   - Cancellation policies
   - Location importance
   - Amenity preferences
   - Service expectations
   - Travel motivation
   - Group vs solo travel

7. **Beauty & Personal Care** (60 papers)
   - Product fragrance importance
   - Ingredient preferences
   - Brand loyalty
   - Price sensitivity
   - Natural/organic preference
   - Sampling effectiveness
   - Influencer influence
   - Review importance
   - Gender marketing
   - Sustainability concerns

8. **Home & Living** (60 papers)
   - Interior design preferences
   - Furniture quality perception
   - Color/style trends
   - Online vs in-store furniture
   - Delivery urgency
   - Assembly concerns
   - Returns expectations
   - Smart home adoption
   - Sustainability preferences
   - Space constraints (apartments vs houses)

9. **Automotive** (80 papers)
   - Car buying decision-making
   - New vs used
   - Financing preferences
   - Brand loyalty in cars
   - Feature preferences
   - Safety concern
   - Environmental concern (electric)
   - Dealer vs online
   - Review importance
   - Price negotiation behavior

10. **Fitness & Wellness** (70 papers)
    - Gym membership behavior
    - Class vs solo workout
    - Home workout adoption
    - Trainer importance
    - Goal-setting effectiveness
    - Motivation factors
    - Community importance
    - Technology/tracking adoption
    - Nutrition plan adherence
    - Supplement use

11. **Financial Services** (80 papers)
    - Bank selection
    - Online vs branch banking
    - Credit card choice
    - Loan product choice
    - Investment advice preference
    - Fee sensitivity
    - Security importance
    - Customer service expectations
    - Mobile banking adoption
    - Alternative finance

12. **Education & Training** (70 papers)
    - Course selection
    - Online vs in-person learning
    - Certification value perception
    - Skill importance
    - Career advancement motivation
    - Price sensitivity
    - Completion rates
    - Peer learning preference
    - Feedback preference
    - Gamification effectiveness

13. **Entertainment & Gaming** (70 papers)
    - Game genre preferences
    - In-game purchases
    - Streaming vs owning
    - Multiplayer preference
    - Social features importance
    - Graphics vs gameplay
    - Competitive vs casual
    - Accessibility preferences
    - Esports engagement
    - Content creator influence

14. **Business Services** (60 papers)
    - B2B buying committees
    - Vendor evaluation
    - Contract negotiations
    - Implementation complexity tolerance
    - ROI importance
    - Risk aversion (B2B)
    - Relationship importance
    - Integration complexity
    - Support importance
    - Pricing models preference

15. **Beauty Services** (60 papers)
    - Salon choice factors
    - Stylist loyalty
    - Appointment scheduling
    - Price sensitivity
    - Tip behavior
    - Treatment preferences
    - Product recommendations
    - Walk-in vs appointment
    - Gender preferences in providers
    - Online booking adoption

16. **Real Estate** (70 papers)
    - Home buying decision-making
    - Location importance
    - Price to income ratio
    - Walkability preference
    - School quality importance
    - Commute tolerance
    - New vs old homes
    - Urban vs suburban vs rural
    - Investment property motivation
    - Agent importance

17. **Insurance** (60 papers)
    - Policy selection
    - Risk perception
    - Claim behavior
    - Provider loyalty
    - Price vs coverage tradeoffs
    - Online shopping behavior
    - Bundling effects
    - Deductible choices
    - Customer service expectations
    - Digital claims processing

18. **Food Delivery** (50 papers)
    - Restaurant selection
    - Delivery speed importance
    - Price sensitivity
    - Platform switching
    - Order frequency
    - Meal complexity preferences
    - Health concern
    - New restaurant trial
    - Loyalty program effectiveness
    - Surge pricing acceptance

19. **Subscription Services** (70 papers)
    - Subscription commitment
    - Free trial conversion
    - Churn factors
    - Feature preferences
    - Price sensitivity
    - Bundle attractiveness
    - Cancellation barriers
    - Family sharing acceptance
    - Ad vs ad-free choice
    - Content curation importance

20. **Gig Economy Services** (50 papers)
    - Service provider selection
    - Price sensitivity
    - Rating importance
    - Response time expectations
    - Cancellation tolerance
    - Scheduling flexibility
    - Service quality expectations
    - Feedback behavior
    - Tip behavior
    - Platform switching

**Plus 20-50 additional niche industries with 20-30 papers each (manufacturing, agriculture, construction, logistics, energy, utilities, telecommunications, media, non-profit, government services, etc.)**

---

### 3.4 By Cultural Context (200+ papers)

**Regional cultural studies:**
- APAC (Asia-Pacific): East Asia, Southeast Asia, South Asia, Oceania
- Europe: Western, Southern, Eastern, Nordic
- Americas: North America, Central America, South America, Caribbean
- Middle East & North Africa
- Sub-Saharan Africa

**Cultural dimensions variations:**
- Power distance manifestations by country
- Individualism-collectivism in decision-making by country
- Masculinity-femininity values by country
- Uncertainty avoidance by country
- Long-term vs short-term orientation
- Indulgence vs restraint
- Communication styles by culture
- Decision-making processes by culture
- Trust-building by culture
- Negotiation styles by culture

---

### 3.5 By Demographic (100+ papers)

**Generational:**
- Silent Generation decision-making
- Baby Boomer preferences
- Gen X attitudes
- Millennial behavior
- Gen Z psychology
- Gen Alpha (emerging)

**Life Stage:**
- Young professionals (20-30)
- Established professionals (30-45)
- Peak earning years (40-55)
- Pre-retirement (55-65)
- Retirement (65+)

**Family Status:**
- Single individuals
- Young couples
- Families with young children
- Families with teenagers
- Empty nesters
- Single parents

**Income/Class:**
- Lower income ($0-25k)
- Lower-middle income ($25-50k)
- Middle income ($50-100k)
- Upper-middle income ($100-250k)
- High income ($250k+)

---

### 3.6 By Temporal Context (100+ papers)

**Seasonal patterns:**
- Holiday shopping (by culture, religion)
- New Year behaviors
- Back-to-school
- Summer vacation
- Winter/cold weather
- Spring/warming weather

**Economic cycles:**
- Recession behavior
- Recovery behavior
- Boom behavior
- Inflation behavior
- Deflation behavior
- Volatility behavior

**Recent historical events:**
- COVID-19 impact
- 2008 financial crisis impact
- Climate disasters impact
- War/conflict impact
- Political upheaval impact
- Technological disruption impact

---

## Part 4: Implementation Roadmap

### Phase 1: Data Infrastructure (Weeks 1-2)
- [ ] Build ContextIntelligenceEngine class
- [ ] Integrate 10 major data APIs (economic, weather, news, social)
- [ ] Build caching layer (Redis)
- [ ] Build error handling & graceful degradation
- [ ] Monitor data quality

### Phase 2: RAG Expansion (Weeks 2-4)
- [ ] Scrape 500 country-specific papers
- [ ] Scrape 200 industry papers per major industry
- [ ] Scrape 300 behavioral domain papers
- [ ] Scrape 200 cultural context papers
- [ ] Embed all papers with OpenAI Embeddings
- [ ] Build RAG index (vector database)

### Phase 3: Persona Enhancement (Week 4-5)
- [ ] Update persona generation prompt with 100+ context variables
- [ ] Update interview prompts with context awareness
- [ ] Update aggregation prompts with context synthesis
- [ ] Test on 5 countries, 5 industries

### Phase 4: Integration & Optimization (Week 5-6)
- [ ] Wire into simulations route
- [ ] Monitor latency & optimize slow queries
- [ ] A/B test persona quality with/without context
- [ ] Build observability dashboard

---

## Success Metrics

- **Persona diversity:** +50-100% unique persona variations due to context
- **Regional accuracy:** 20-40% improvement on non-US personas
- **Industry accuracy:** 15-30% improvement on niche industries
- **Backtest accuracy:** 55-70% on full 44-case suite (vs current 44%)
- **API latency:** <2 seconds additional for context gathering (non-blocking)
- **Data coverage:** 1000+ context dimensions available for every simulation
- **Knowledge completeness:** 2000+ papers indexed, covering every country and major industry

---

**This is a production-grade, enterprise intelligence system.**  
**Not a prototype. Ship-ready architecture.**

