"""
Master Agro-Meteorological Advisory Generator.

Integrates all agronomic modules into a unified, high-integrity advisory dossier:
1. Spraying Decision Engine
2. Irrigation Optimization Engine
3. Bio-climatic Pest & Disease Analyzer
4. GKMS General Agronomic Rules
5. Support-Aware Conservativeness (Downgrades actions if uncertainty support is LOW)
"""

from typing import Dict, Any, Optional
from src.advisory.crop_calendar import CropCalendar
from src.advisory.pest_disease import PestDiseaseAdvisor
from src.advisory.spray_window import SprayWindowAdvisor
from src.advisory.irrigation_advisor import IrrigationAdvisor
from src.advisory.agromet_rules import AgrometRuleEngine

class AgrometAdvisoryGenerator:
    def __init__(self):
        self.crop_cal = CropCalendar()
        self.pest_adv = PestDiseaseAdvisor()
        self.spray_adv = SprayWindowAdvisor()
        self.irrig_adv = IrrigationAdvisor()
        self.rules_engine = AgrometRuleEngine()

    def generate_panchayat_advisory(
        self,
        panchayat_name: str,
        weather: Dict[str, float],
        crop_key: str = "wheat",
        stage_key: Optional[str] = None,
        support_level: str = "HIGH"
    ) -> Dict[str, Any]:
        """
        Synthesizes a comprehensive agromet advisory dossier for a specific panchayat.
        """
        crop_info = self.crop_cal.get_crop_info(crop_key) or {
            "name": crop_key.capitalize(),
            "stages": {}
        }
        
        stages = crop_info.get("stages", {})
        if not stage_key or stage_key not in stages:
            # Pick first or middle stage as default
            stage_key = list(stages.keys())[0] if stages else "vegetative"

        stage_info = stages.get(stage_key, {
            "desc": stage_key.capitalize(),
            "kc": 1.0,
            "critical_water": False
        })

        crop_kc = float(stage_info.get("kc", 1.0))
        is_critical_water = bool(stage_info.get("critical_water", False))

        # 1. Spray Window Feasibility
        spray_eval = self.spray_adv.evaluate_spray_conditions(weather)

        # 2. Irrigation Scheduling (ET0 & Net Deficit)
        irrig_eval = self.irrig_adv.calculate_irrigation_requirement(
            weather=weather,
            crop_kc=crop_kc,
            critical_water_stage=is_critical_water
        )

        # 3. Pest & Disease Bio-Climatic Risks
        pest_risks = self.pest_adv.evaluate_risks(weather, crop_key)

        # 4. GKMS General Rules (Fertilizer, Harvest, Lodging, Temperature)
        general_rules = self.rules_engine.evaluate_general_agromet_rules(
            weather=weather,
            crop_name=crop_info.get("name", crop_key),
            stage_name=stage_info.get("desc", stage_key)
        )

        # 5. Support-Aware Conservativeness
        # If epistemic uncertainty support is LOW, downgrade irreversible actions to CAUTION
        if support_level == "LOW":
            if spray_eval["status"] == "GO":
                spray_eval["status"] = "CAUTION"
                spray_eval["summary"] = "Borderline confidence due to sparse gauge coverage. Exercise caution before spraying."
            if irrig_eval["action"] == "IRRIGATE" and not is_critical_water:
                irrig_eval["action"] = "LIGHT"
                irrig_eval["guidance"] += " (Conservative advice: Model confidence is moderate/low; verify soil profile before heavy irrigation)."

        # Determine composite status
        severity_priority = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "CAUTION": 2, "LOW": 1, "GO": 1, "FAVORABLE": 1, "NONE": 0}
        max_sev = "MODERATE"
        if any(r.get("severity") == "CRITICAL" for r in general_rules):
            max_sev = "CRITICAL"
        elif any(r.get("severity") == "HIGH" for r in general_rules) or any(p.get("severity") == "HIGH" for p in pest_risks):
            max_sev = "HIGH"

        return {
            "panchayat_name": panchayat_name,
            "crop": {
                "key": crop_key,
                "name": crop_info.get("name", crop_key),
                "stage_key": stage_key,
                "stage_description": stage_info.get("desc", stage_key),
                "kc_factor": crop_kc,
                "critical_water_stage": is_critical_water
            },
            "overall_severity": max_sev,
            "support_level": support_level,
            "spray_advisory": spray_eval,
            "irrigation_advisory": irrig_eval,
            "pest_disease_alerts": pest_risks,
            "agronomic_action_items": general_rules,
            "weather_summary": {
                "rainfall_mm": weather.get("rainfall_mm", 0.0),
                "rainfall_probability_pct": weather.get("rainfall_probability_pct", 0.0),
                "tmax_c": weather.get("tmax_c", 30.0),
                "tmin_c": weather.get("tmin_c", 20.0),
                "rh_max_pct": weather.get("rh_max_pct", 70.0),
                "wind_speed_kmh": weather.get("wind_speed_kmh", 10.0)
            }
        }
