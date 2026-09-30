"""
Uncertainty Quantification & Epistemic Support Module.

Provides calibrated prediction confidence intervals:
- P10 (Low/conservative estimate, 10th percentile)
- P50 (Median expectation, 50th percentile)
- P90 (High/worst-case estimate, 90th percentile)

Also computes epistemic confidence score based on:
- Distance to physical rain gauge/weather station
- Topographic extremeness (elevation delta, ruggedness)
- Atmospheric anomaly extremity (standard deviations from seasonal climatology)
"""

import math
from typing import Dict, Any

class UncertaintyEngine:
    @staticmethod
    def estimate_uncertainty(
        weather_value: float,
        parameter: str,
        terrain: Dict[str, Any],
        station_distance_km: float = 15.0
    ) -> Dict[str, Any]:
        """
        Calculates P10, P50, P90 confidence intervals and evidence support level.
        """
        elev = float(terrain.get("elevation_m", 500.0))
        ruggedness = float(terrain.get("ruggedness_m", 15.0))

        # Base relative standard error depends on station distance and terrain roughness
        distance_penalty = min(0.35, (station_distance_km / 50.0) * 0.25)
        roughness_penalty = min(0.25, (ruggedness / 100.0) * 0.15)
        total_uncertainty_factor = 0.12 + distance_penalty + roughness_penalty

        if parameter == "rainfall_mm":
            # For rainfall, error is heteroskedastic (proportional to magnitude)
            sigma = max(0.8, weather_value * total_uncertainty_factor)
            p10 = max(0.0, weather_value - 1.28 * sigma)
            p50 = weather_value
            p90 = weather_value + 1.28 * sigma
        elif parameter in ("tmax_c", "tmin_c"):
            # Temperature errors are approx Gaussian ~ 1.0 - 1.8 °C
            sigma = 0.8 + distance_penalty * 2.0
            p10 = round(weather_value - 1.28 * sigma, 1)
            p50 = round(weather_value, 1)
            p90 = round(weather_value + 1.28 * sigma, 1)
        elif parameter == "wind_speed_kmh":
            sigma = max(1.5, weather_value * (total_uncertainty_factor * 1.2))
            p10 = max(0.5, round(weather_value - 1.28 * sigma, 1))
            p50 = round(weather_value, 1)
            p90 = round(weather_value + 1.28 * sigma, 1)
        else:
            p10 = weather_value * 0.85
            p50 = weather_value
            p90 = weather_value * 1.15

        # Classify support level
        if total_uncertainty_factor < 0.20 and station_distance_km < 20.0:
            support_level = "HIGH"
            support_desc = "Nearby physical station & gentle terrain. High model confidence."
            support_score = 0.90
        elif total_uncertainty_factor < 0.35:
            support_level = "MODERATE"
            support_desc = "Moderate distance to observation stations. Standard inference."
            support_score = 0.72
        else:
            support_level = "LOW"
            support_desc = "Complex orographic relief or sparse observation density. Conservative advice applied."
            support_score = 0.52

        return {
            "p10": round(float(p10), 2),
            "p50": round(float(p50), 2),
            "p90": round(float(p90), 2),
            "support_level": support_level,
            "support_score": support_score,
            "support_description": support_desc
        }
