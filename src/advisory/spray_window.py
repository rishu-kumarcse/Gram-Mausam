"""
Agrochemical Spray Window Feasibility Analyzer.

Determines whether chemical or foliar spraying operations are safe and effective.
Criteria evaluated:
1. Wash-off Risk: Rainfall probability and anticipated precipitation within 12-24h.
2. Droplet Drift Risk: Wind speed exceeding drift limit (drift into neighbor crops or water bodies).
3. Evaporative Loss: Extremely low relative humidity or scorching heat causing droplet crystallization before absorption.
4. Leaf Scorching Risk: Extreme ambient temperatures causing phytotoxicity.
"""

from typing import Dict, Any

class SprayWindowAdvisor:
    @staticmethod
    def evaluate_spray_conditions(weather: Dict[str, float]) -> Dict[str, Any]:
        wind_speed = float(weather.get("wind_speed_kmh", 10.0))
        rain_prob = float(weather.get("rainfall_probability_pct", 10.0))
        rainfall_mm = float(weather.get("rainfall_mm", 0.0))
        tmax = float(weather.get("tmax_c", 30.0))
        rh_min = float(weather.get("rh_min_pct", 50.0))

        flags = []
        action = "GO" # GO | CAUTION | AVOID

        # 1. Rainfall / Wash-off evaluation
        if rainfall_mm >= 2.5 or rain_prob >= 50.0:
            action = "AVOID"
            flags.append(f"Severe wash-off hazard: {rainfall_mm:.1f} mm rain / {rain_prob:.0f}% probability expected. Spraying will waste chemical.")
        elif rainfall_mm > 0.5 or rain_prob >= 25.0:
            if action != "AVOID":
                action = "CAUTION"
            flags.append(f"Moderate wash-off risk: {rain_prob:.0f}% chance of rain. Use rain-fast spreader sticker.")

        # 2. Wind Speed / Drift evaluation
        if wind_speed >= 18.0:
            action = "AVOID"
            flags.append(f"Severe droplet drift hazard: Wind speed {wind_speed:.1f} km/h exceeds maximum permissible 15 km/h threshold.")
        elif wind_speed >= 12.0:
            if action != "AVOID":
                action = "CAUTION"
            flags.append(f"Breezy conditions ({wind_speed:.1f} km/h): Keep spray nozzle close to crop canopy; avoid dusting.")

        # 3. Evaporation / Scorching evaluation
        if tmax >= 36.0:
            if action != "AVOID":
                action = "CAUTION"
            flags.append(f"High temperature ({tmax:.1f}°C): Restrict spraying strictly to early morning (6-9 AM) or late evening (4-6 PM) to avoid leaf scorch.")
        
        if rh_min < 30.0:
            flags.append("Very dry air (RH < 30%): Spray droplets may evaporate rapidly before cuticle penetration.")

        if action == "GO":
            summary = "Optimal spraying conditions. Clear skies, mild winds, and negligible wash-off risk."
            best_time = "Early morning (7:00 AM - 10:30 AM) or Late afternoon (4:00 PM - 6:00 PM)"
        elif action == "CAUTION":
            summary = "Marginal spraying conditions. Proceed only if urgent pest outbreak with recommended precautions."
            best_time = "Strictly during calm early morning hours (6:00 AM - 8:30 AM)"
        else:
            summary = "Unsafe for chemical spraying. Postpone operations until wind abates and rain threat passes."
            best_time = "Postpone application"

        return {
            "status": action, # GO | CAUTION | AVOID
            "summary": summary,
            "best_window": best_time,
            "hazards": flags,
            "wind_speed_kmh": wind_speed,
            "rain_prob_pct": rain_prob
        }
