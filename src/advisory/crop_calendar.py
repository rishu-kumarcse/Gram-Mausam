"""
Crop Phenology and Growing Degree Days (GDD) Module.

Tracks crop developmental stages:
- Sowing / Nursery
- Vegetative / Tillering
- Flowering / Anthesis
- Grain Filling / Fruit Setting
- Physiological Maturity & Harvest

Computes daily Growing Degree Days:
    GDD = max(0, ((Tmax + Tmin) / 2) - Tbase)
"""

import json
from typing import Dict, Any, Optional
from src.core.config import config

class CropCalendar:
    def __init__(self, crop_db_path: Optional[str] = None):
        self.crop_db_path = crop_db_path or config.agronomic.crop_db_path
        self.crops = {}
        self._load_crops()

    def _load_crops(self):
        try:
            with open(self.crop_db_path, "r", encoding="utf-8") as f:
                self.crops = json.load(f)
        except Exception as e:
            print(f"[CropCalendar] Warning: Could not load crops: {e}")

    def list_available_crops(self) -> Dict[str, str]:
        return {k: v.get("name", k) for k, v in self.crops.items()}

    def get_crop_info(self, crop_key: str) -> Optional[Dict[str, Any]]:
        return self.crops.get(crop_key.lower())

    def get_crop_stage(self, crop_key: str, stage_key: str) -> Optional[Dict[str, Any]]:
        crop = self.get_crop_info(crop_key)
        if not crop:
            return None
        stages = crop.get("stages", {})
        return stages.get(stage_key.lower())

    def calculate_gdd(self, crop_key: str, tmax: float, tmin: float) -> float:
        crop = self.get_crop_info(crop_key)
        base_temp = crop.get("base_temp_c", 10.0) if crop else 10.0
        mean_temp = (tmax + tmin) / 2.0
        return max(0.0, mean_temp - base_temp)
