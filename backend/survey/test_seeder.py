"""
TestSeeder -- generates realistic test data from the schema definition.

Used in tests AND for demo/onboarding. Seed data always matches the current schema.
"""

import random
from backend.survey.schema_loader import get_schema


class TestSeeder:

    def __init__(self, target: str = "workspace"):
        self.schema = get_schema()
        self.target = target

    def generate(self, profile: str = "default", overrides: dict = None) -> dict:
        data = self._profiles().get(profile, self._random_data())
        if overrides:
            data.update(overrides)
        return data

    def _profiles(self) -> dict[str, dict]:
        return {
            "spanish_restaurant": {
                "name": "La Tasca de Miguel",
                "type": "restaurant",
                "description": "Family-run tapas restaurant in the Eixample district. Known for fresh seafood and traditional Catalan dishes.",
                "location": "Barcelona, Spain",
                "location_country": "ES",
                "location_city": "Barcelona",
                "customer_description": "Mostly local office workers aged 30-55, regulars who come for lunch. Very loyal but price conscious.",
                "years_open": "3-10",
                "business_role": "habit",
                "visit_frequency": "weekly",
                "busy_days": ["mon", "tue", "wed", "thu"],
                "busy_times": ["lunchtime"],
                "customer_value_drivers": ["atmosphere", "personal_touch", "quality"],
                "regular_proportion": "solid_base",
                "area_demographics": ["business"],
                "competitor_count": "three_five",
                "area_feel": "community",
            },
            "uk_barbershop": {
                "name": "Sharp & Sons",
                "type": "barbershop",
                "description": "Traditional barbershop in suburban Manchester. Haircuts, beard trims, and hot towel shaves.",
                "location": "Manchester, UK",
                "location_country": "GB",
                "location_city": "Manchester",
                "customer_description": "Men aged 20-50, mix of students and professionals. Most come monthly.",
                "years_open": "1-3",
                "business_role": "treat",
                "visit_frequency": "monthly",
                "customer_value_drivers": ["personal_touch", "consistency", "specific_product"],
                "regular_proportion": "mostly_regulars",
                "area_demographics": ["residential"],
                "competitor_count": "one_two",
                "area_feel": "community",
            },
            "dutch_retailer": {
                "name": "De Winkel",
                "type": "clothing",
                "description": "Independent clothing boutique in Amsterdam's Jordaan district. Curated European brands.",
                "location": "Amsterdam, Netherlands",
                "location_country": "NL",
                "location_city": "Amsterdam",
                "years_open": "10+",
                "visit_frequency": "occasional",
                "area_demographics": ["shopping", "tourist"],
                "competitor_count": "six_plus",
                "area_feel": "destination",
            },
        }

    def _random_data(self) -> dict:
        data = {}
        for field in self.schema.fields_for_target(self.target):
            if field.options:
                flat = self._flat_options(field)
                if flat:
                    if field.type in ("chips", "multi_select"):
                        data[field.id] = random.sample(flat, k=min(2, len(flat)))
                    else:
                        data[field.id] = random.choice(flat)
            elif field.type == "number":
                data[field.id] = random.randint(0, 100)
            elif field.type == "boolean":
                data[field.id] = random.choice([True, False])
        return data

    def schema_coverage_report(self, data: dict) -> dict:
        fields = self.schema.fields_for_target(self.target)
        populated = [f.id for f in fields if data.get(f.id) not in [None, [], ""]]
        missing = [f.id for f in fields if data.get(f.id) in [None, [], ""]]
        return {
            "total_fields": len(fields),
            "populated": len(populated),
            "missing": missing,
            "coverage_pct": round(len(populated) / len(fields) * 100) if fields else 0,
        }

    def _flat_options(self, field) -> list:
        values = []
        for opt in field.options:
            if "items" in opt:
                values.extend(i["value"] for i in opt["items"])
            elif "value" in opt:
                values.append(opt["value"])
        return values
