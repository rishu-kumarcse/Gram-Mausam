"""
Bio-Climatic Pest & Disease Risk Modeling Module.

Implements epidemiological threshold models for key Indian agricultural pests & diseases:
- Late Blight in Tomato/Potato (Wallin/Hyre index)
- Downy Mildew & Powdery Mildew in Grapes/Onion (Mills period)
- Blast in Paddy/Rice
- Pink Bollworm in Cotton
- Fall Armyworm in Maize
- Thrips & Purple Blotch in Onion
"""

import json
from typing import Dict, List, Any, Optional
from src.core.config import config

class PestDiseaseAdvisor:
    def __init__(self, pest_db_path: Optional[str] = None):
        self.pest_db_path = pest_db_path or config.agronomic.pest_db_path
        self.models = {}
        self._load_models()

    def _load_models(self):
        try:
            with open(self.pest_db_path, "r", encoding="utf-8") as f:
                self.models = json.load(f)
        except Exception as e:
            print(f"[PestDiseaseAdvisor] Warning: Could not load pest models: {e}")

    def evaluate_risks(
        self,
        weather: Dict[str, float],
        crop_key: str
    ) -> List[Dict[str, Any]]:
        """
        Evaluates active disease and pest risks for a crop under downscaled weather.
        """
        active_risks = []
        crop_key = crop_key.lower()

        tmax = float(weather.get("tmax_c", 30.0))
        tmin = float(weather.get("tmin_c", 20.0))
        mean_temp = (tmax + tmin) / 2.0
        rh_max = float(weather.get("rh_max_pct", 75.0))
        rainfall = float(weather.get("rainfall_mm", 0.0))
        rain_prob = float(weather.get("rainfall_probability_pct", 20.0))

        for pest_id, model in self.models.items():
            if crop_key not in model.get("target_crops", []):
                continue

            cond = model.get("conditions", {})
            severity = "NONE"
            reasons = []

            # 1. Late Blight evaluation
            if pest_id == "late_blight":
                if (10.0 <= mean_temp <= 22.0) and rh_max >= 88.0 and (rainfall > 1.0 or rain_prob > 60.0):
                    severity = "HIGH"
                    reasons.append(f"Optimal spore germination temp ({mean_temp:.1f}°C) and persistent high RH ({rh_max:.0f}%) with wet conditions")
                elif (10.0 <= mean_temp <= 24.0) and rh_max >= 78.0:
                    severity = "MODERATE"
                    reasons.append(f"Elevated night humidity ({rh_max:.0f}%) favorable for initial blight infection")

            # 2. Downy Mildew evaluation
            elif pest_id == "downy_mildew":
                if (16.0 <= mean_temp <= 25.0) and rh_max >= 85.0 and rainfall > 0.5:
                    severity = "HIGH"
                    reasons.append(f"Foliar wetness and high RH ({rh_max:.0f}%) with moderate temperature ({mean_temp:.1f}°C)")
                elif (15.0 <= mean_temp <= 28.0) and rh_max >= 78.0:
                    severity = "MODERATE"
                    reasons.append(f"Atmospheric humidity approaching mildew threshold ({rh_max:.0f}%)")

            # 3. Powdery Mildew evaluation (favors dry warm days with humid nights)
            elif pest_id == "powdery_mildew":
                if (22.0 <= tmax <= 33.0) and (50.0 <= rh_max <= 78.0) and rainfall < 1.0:
                    severity = "HIGH"
                    reasons.append(f"Warm dry weather ({tmax:.1f}°C) with moderate morning humidity favorable for powdery mildew conidia")
                elif (20.0 <= tmax <= 35.0) and (45.0 <= rh_max <= 80.0):
                    severity = "MODERATE"
                    reasons.append("Dry canopy conditions with favorable fungal incubation temperatures")

            # 4. Rice Blast evaluation
            elif pest_id == "blast":
                if (20.0 <= tmin <= 26.0) and rh_max >= 88.0:
                    severity = "HIGH"
                    reasons.append(f"Cool humid nights (Tmin {tmin:.1f}°C, RH {rh_max:.0f}%) create heavy morning dew essential for blast lesion spread")
                elif rh_max >= 80.0 and (18.0 <= tmin <= 28.0):
                    severity = "MODERATE"
                    reasons.append("Sustained relative humidity above 80%")

            # 5. Pink Bollworm
            elif pest_id == "pink_bollworm":
                if 28.0 <= tmax <= 37.0 and rainfall < 2.0:
                    severity = "MODERATE"
                    reasons.append("Warm dry spells stimulate moth activity and larval penetration into bolls")

            # 6. Fall Armyworm
            elif pest_id == "fall_armyworm":
                if 22.0 <= mean_temp <= 32.0 and rainfall < 5.0:
                    severity = "MODERATE"
                    reasons.append("Optimal vegetative temperature accelerating armyworm developmental cycle")

            # 7. Thrips & Purple Blotch in Onion
            elif pest_id == "thrips_purple_blotch":
                if rainfall > 2.0 and tmax >= 26.0 and rh_max >= 80.0:
                    severity = "HIGH"
                    reasons.append("Post-rain high humidity combined with warmth triggers rapid purple blotch lesion outbreak")
                elif tmax >= 30.0 and rh_max < 60.0:
                    severity = "MODERATE"
                    reasons.append("Hot dry conditions favoring thrips vector reproduction")

            if severity in ("MODERATE", "HIGH"):
                active_risks.append({
                    "pest_id": pest_id,
                    "name": model.get("name", pest_id),
                    "severity": severity,
                    "reasons": reasons,
                    "action_recommendation": model.get("recommendation", ""),
                    "organic_alternative": model.get("organic_measure", "")
                })

        return active_risks
