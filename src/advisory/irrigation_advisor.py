"""
Evapotranspiration (ET0) and Crop Water Irrigation Scheduling Module.

Calculates:
1. Reference Evapotranspiration (ET0) via Hargreaves-Samani method.
2. Crop Water Requirement (ETc = Kc * ET0).
3. Effective Precipitation (USDA-SCS method).
4. Net Irrigation Water Requirement (NIR = max(0, ETc - Peff)).
5. Actionable guidance: Skip, Postpone, Apply light irrigation, or Full scheduled irrigation.
"""

import math
from typing import Dict, Any, Optional

class IrrigationAdvisor:
    @staticmethod
    def calculate_et0(tmax: float, tmin: float, lat: float = 18.5) -> float:
        """
        Computes daily reference evapotranspiration (ET0 in mm/day) using Hargreaves equation.
        """
        tmean = (tmax + tmin) / 2.0
        tdelta = max(1.0, tmax - tmin)
        
        # Estimate extraterrestrial radiation Ra (approx 14.5 - 16.0 MJ/m2/day for Deccan latitude)
        # 1 MJ/m2/day ≈ 0.408 mm/day equivalent evaporation
        ra_approx_mm = 15.0 * 0.408 # ~6.12 mm/day
        
        et0 = 0.0023 * ra_approx_mm * (tmean + 17.8) * math.sqrt(tdelta)
        return max(1.5, min(9.5, round(et0, 2)))

    @classmethod
    def calculate_irrigation_requirement(
        cls,
        weather: Dict[str, float],
        crop_kc: float = 1.0,
        critical_water_stage: bool = False,
        soil_type: str = "medium_black",
        lat: float = 18.5
    ) -> Dict[str, Any]:
        tmax = float(weather.get("tmax_c", 30.0))
        tmin = float(weather.get("tmin_c", 20.0))
        rainfall = float(weather.get("rainfall_mm", 0.0))
        rain_prob = float(weather.get("rainfall_probability_pct", 10.0))

        # 1. Reference ET0
        et0 = cls.calculate_et0(tmax, tmin, lat)

        # 2. Crop ETc
        etc = round(et0 * crop_kc, 2)

        # 3. Effective Rainfall (Pe)
        if rainfall > 5.0:
            peff = round(max(0.0, 0.8 * rainfall - 2.0), 2)
        elif rainfall > 2.0:
            peff = round(0.5 * rainfall, 2)
        else:
            peff = 0.0

        # 4. Net Irrigation Water Deficit (NIR)
        net_deficit_mm = round(max(0.0, etc - peff), 2)

        # 5. Recommendation Action
        if peff >= etc or rainfall >= 12.0:
            action = "SKIP"
            guidance = f"Skip irrigation. Effective rainfall ({peff:.1f} mm) fully meets or exceeds daily crop demand ({etc:.1f} mm). Ensure surface drainage."
            hours_drip = 0.0
        elif rainfall >= 5.0 or (rain_prob >= 70.0 and rainfall >= 2.0):
            action = "POSTPONE"
            guidance = f"Postpone irrigation. Light to moderate rain anticipated ({rainfall:.1f} mm, {rain_prob:.0f}% chance). Monitor field moistness before resuming."
            hours_drip = 0.0
        elif net_deficit_mm < 1.5:
            action = "LIGHT"
            guidance = f"Light irrigation. Daily deficit is minimal ({net_deficit_mm:.1f} mm). A brief maintenance run is sufficient."
            hours_drip = 1.0
        else:
            action = "IRRIGATE"
            stage_note = " (CRITICAL STAGE: moisture stress now will impair yield)" if critical_water_stage else ""
            guidance = f"Apply scheduled irrigation: Net water deficit is {net_deficit_mm:.1f} mm ({net_deficit_mm * 10:.0f} m³/ha){stage_note}."
            # Estimate drip duration assuming standard 4 LPH drippers ~ 2.5 mm/hr
            hours_drip = round(net_deficit_mm / 2.2, 1)

        return {
            "action": action, # SKIP | POSTPONE | LIGHT | IRRIGATE
            "guidance": guidance,
            "et0_mm_day": et0,
            "etc_mm_day": etc,
            "effective_rainfall_mm": peff,
            "net_deficit_mm": net_deficit_mm,
            "drip_runtime_hours": hours_drip,
            "critical_stage_warning": critical_water_stage
        }
