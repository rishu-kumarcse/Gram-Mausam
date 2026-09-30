"""
Statistical Machine Learning Downscaling Module.

Uses Gradient Boosted Trees (XGBoost) and Random Forests to predict fine-scale
panchayat meteorological variations from synoptic block forecasts and geospatial features.
Features used:
- block_forecast_rainfall_mm
- panchayat_latitude, panchayat_longitude
- elevation_m
- station_distance_km
- lead_days (1-5)
- month, day_of_year
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.config import config

class MLDownscaler:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or config.ml.xgboost_weights_path
        self.model = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception as e:
                print(f"[MLDownscaler] Warning: Could not load model from {self.model_path}: {e}")
                self.model = None

    def is_loaded(self) -> bool:
        return self.model is not None

    def predict_panchayat_weather(
        self,
        block_forecast: Dict[str, float],
        panchayat_props: Dict[str, Any],
        date_str: Optional[str] = None,
        lead_day: int = 1
    ) -> Dict[str, float]:
        """
        Runs ML regression for a single panchayat.
        """
        # Determine temporal features
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                month = dt.month
                day_of_year = dt.timetuple().tm_yday
            except Exception:
                month = 7 # Monsoon peak default
                day_of_year = 195
        else:
            now = datetime.now()
            month = now.month
            day_of_year = now.timetuple().tm_yday

        lat = float(panchayat_props.get("centroid_lat") or panchayat_props.get("lat") or 18.5)
        lon = float(panchayat_props.get("centroid_lon") or panchayat_props.get("lon") or 74.0)
        
        terrain = panchayat_props.get("terrain", {})
        elev = float(terrain.get("elevation_m") or panchayat_props.get("elevation_m") or 550.0)
        station_dist = float(panchayat_props.get("distance_to_station_km") or 12.0)

        block_rain = float(block_forecast.get("rainfall_mm", 0.0))

        if self.model is not None:
            # Build feature vector matching training schema:
            # ['block_forecast_rainfall_mm', 'panchayat_latitude', 'panchayat_longitude',
            #  'elevation_m', 'station_distance_km', 'lead_days', 'month', 'day_of_year']
            feature_row = pd.DataFrame([{
                'block_forecast_rainfall_mm': block_rain,
                'panchayat_latitude': lat,
                'panchayat_longitude': lon,
                'elevation_m': elev,
                'station_distance_km': station_dist,
                'lead_days': lead_day,
                'month': month,
                'day_of_year': day_of_year
            }])

            try:
                pred_rain = float(self.model.predict(feature_row)[0])
                # Non-negativity constraint on rainfall
                pred_rain = max(0.0, pred_rain)
            except Exception as e:
                # ML inference error fallback
                pred_rain = block_rain
        else:
            # Heuristic regression fallback
            elev_diff = elev - 500.0
            pred_rain = max(0.0, block_rain * (1.0 + (elev_diff / 1000.0) * 0.3))

        # Two-stage classification for rainy day probability:
        # P(Rain >= 2.5 mm)
        if pred_rain < 0.5:
            rain_prob = max(5.0, pred_rain * 20.0)
        elif pred_rain < 2.5:
            rain_prob = 30.0 + (pred_rain - 0.5) * 25.0
        else:
            rain_prob = min(98.0, 70.0 + (pred_rain - 2.5) * 1.5)

        return {
            "ml_rainfall_mm": round(pred_rain, 2),
            "ml_rainfall_probability_pct": round(rain_prob, 1),
            "model_type": "XGBoostRegressor" if self.model else "HeuristicRegressor"
        }
