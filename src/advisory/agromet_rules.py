"""
ICAR & IMD GKMS Compliant Agronomic Rule Engine.

Deterministic rule evaluations for:
1. Nitrogen & Fertilizer Application Timing (preventing leaching and runoff pollution)
2. Harvest & Post-Harvest Operations (drying, threshing, storage protection)
3. Severe Weather & Lodging Hazards (tying canes, windbreak protection)
4. Thermal Stress Hazards (Heatwaves, Cold waves, Frost)
"""

from typing import Dict, List, Any

class AgrometRuleEngine:
    @staticmethod
    def evaluate_general_agromet_rules(
        weather: Dict[str, float],
        crop_name: str = "General",
        stage_name: str = "General"
    ) -> List[Dict[str, Any]]:
        advisories = []

        rainfall_mm = float(weather.get("rainfall_mm", 0.0))
        rain_prob = float(weather.get("rainfall_probability_pct", 10.0))
        tmax = float(weather.get("tmax_c", 30.0))
        tmin = float(weather.get("tmin_c", 20.0))
        wind_speed = float(weather.get("wind_speed_kmh", 10.0))
        rh_max = float(weather.get("rh_max_pct", 70.0))

        # 1. Fertilizer & Urea Top-Dressing Rule
        if rainfall_mm >= 20.0 or (rain_prob >= 75.0 and rainfall_mm >= 10.0):
            advisories.append({
                "category": "FERTILIZER_APPLICATION",
                "severity": "CRITICAL",
                "headline": "Postpone Urea & Top-Dress Fertilizer Application",
                "details": f"Substantial rainfall ({rainfall_mm:.1f} mm) is forecast. Applying nitrogenous fertilizer now will cause heavy nitrate leaching into ground water and surface runoff loss.",
                "action": "Delay top-dressing until 24 hours after soil drains."
            })
        elif 5.0 <= rainfall_mm < 20.0 and rain_prob > 50.0:
            advisories.append({
                "category": "FERTILIZER_APPLICATION",
                "severity": "MODERATE",
                "headline": "Caution with Fertilizer Application",
                "details": "Moderate rain anticipated. Incorporate fertilizer into soil rather than broadcasting on surface.",
                "action": "Band placement or fertigation through drip preferred."
            })

        # 2. Harvest & Post-Harvest Safety Rule
        if rainfall_mm >= 5.0 or rain_prob >= 60.0:
            advisories.append({
                "category": "HARVEST_PROTECTION",
                "severity": "HIGH",
                "headline": "Protect Harvested Produce and Suspend Threshing",
                "details": "Incoming rain will moisten produce, causing grain mold, aflatoxin contamination, or germination.",
                "action": "Cover harvested piles with tarpaulins or shift into ventilated sheds immediately."
            })
        elif rainfall_mm == 0.0 and rain_prob < 20.0 and rh_max < 65.0:
            advisories.append({
                "category": "HARVEST_PROTECTION",
                "severity": "FAVORABLE",
                "headline": "Optimal Window for Harvesting, Threshing & Sun Drying",
                "details": "Dry atmosphere and bright sunshine provide safe conditions for harvesting and grain moisture reduction.",
                "action": "Accelerate threshing and sun-drying operations."
            })

        # 3. Wind & Lodging Hazard
        if wind_speed >= 28.0:
            advisories.append({
                "category": "WIND_LODGING_HAZARD",
                "severity": "CRITICAL",
                "headline": "Severe Wind Gusts - High Crop Lodging Hazard",
                "details": f"Squally winds reaching {wind_speed:.1f} km/h can lodge tall crops (Sugarcane, Banana, Maize, Sorghum).",
                "action": "Provide mechanical propping, tie 3-4 sugarcane clumps together (trash-twisting), and clear drainage channels."
            })
        elif wind_speed >= 18.0:
            advisories.append({
                "category": "WIND_LODGING_HAZARD",
                "severity": "MODERATE",
                "headline": "Breezy Conditions - Support Vulnerable Crops",
                "details": f"Wind speeds around {wind_speed:.1f} km/h may dislodge blossoms or fruit bunches.",
                "action": "Ensure staking for horticultural trellises (Tomato, Grapes)."
            })

        # 4. Thermal Hazards: Heat Wave / Frost
        if tmax >= 40.0:
            advisories.append({
                "category": "HEAT_STRESS",
                "severity": "CRITICAL",
                "headline": "Severe Heat Stress / Heatwave Alert",
                "details": f"Daytime temperature peaking at {tmax:.1f}°C. Severe pollen sterility in flowering crops and scorching on fruit.",
                "action": "Provide micro-sprinkler misting during 12:00-3:00 PM; mulching with organic residue to conserve root-zone moisture."
            })
        elif tmax >= 36.0:
            advisories.append({
                "category": "HEAT_STRESS",
                "severity": "HIGH",
                "headline": "Elevated Temperatures Alert",
                "details": f"High temperatures ({tmax:.1f}°C) accelerate soil water evaporation.",
                "action": "Frequent light irrigations during early morning or evening hours."
            })

        if tmin <= 4.0:
            advisories.append({
                "category": "FROST_HAZARD",
                "severity": "CRITICAL",
                "headline": "Ground Frost / Extreme Cold Hazard",
                "details": f"Night minimum temperature plunging to {tmin:.1f}°C. Severe frost risk for tender horticultural crops and young orchards.",
                "action": "Apply night irrigation to raise soil thermal mass; generate smoke mulches along windward field boundaries."
            })
        elif tmin <= 8.0:
            advisories.append({
                "category": "COLD_STRESS",
                "severity": "MODERATE",
                "headline": "Cold Wave / Chilling Injury Warning",
                "details": f"Night temperature dropping to {tmin:.1f}°C. Vegetative growth slowdown.",
                "action": "Irrigate lightly in late afternoon to maintain root temperature."
            })

        return advisories
