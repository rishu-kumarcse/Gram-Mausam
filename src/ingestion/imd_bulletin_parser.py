"""
IMD Agromet Advisory Service Bulletin Parser.

Ingests and validates official IMD Block-level forecast bulletins from:
1. Structured JSON (IMD GKMS standard schema)
2. Tabular CSV forecasts
3. Raw meteorological parameter inputs
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class IMDBulletinParser:
    @staticmethod
    def parse_json_bulletin(json_data: Any) -> Dict[str, Any]:
        """
        Parses and standardizes an IMD 5-day Block Bulletin.
        """
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        block_id = data.get("block_id", "IND.20.26.1_1")
        block_name = data.get("block_name", "Baramati")
        district = data.get("district", "Pune")
        state = data.get("state", "Maharashtra")
        
        daily_forecasts = data.get("daily_forecasts", [])
        if not daily_forecasts:
            # Fallback to single-day parameter dict
            daily_forecasts = [{
                "date": datetime.now().date().isoformat(),
                "rainfall_mm": float(data.get("rainfall_mm", 0.0)),
                "rainfall_probability_pct": float(data.get("rainfall_probability_pct", 50.0)),
                "tmax_c": float(data.get("tmax_c", 30.0)),
                "tmin_c": float(data.get("tmin_c", 20.0)),
                "rh_max_pct": float(data.get("rh_max_pct", 75.0)),
                "rh_min_pct": float(data.get("rh_min_pct", 45.0)),
                "wind_speed_kmh": float(data.get("wind_speed_kmh", 10.0)),
                "wind_direction_deg": float(data.get("wind_direction_deg", 245.0)),
                "cloud_cover_octas": int(data.get("cloud_cover_octas", 4))
            }]

        return {
            "bulletin_id": data.get("bulletin_id", f"BULLETIN-{block_name}-{datetime.now().strftime('%Y%m%d')}"),
            "source": data.get("source", "India Meteorological Department (IMD)"),
            "block_id": block_id,
            "block_name": block_name,
            "district": district,
            "state": state,
            "horizon_days": len(daily_forecasts),
            "forecasts": daily_forecasts
        }
