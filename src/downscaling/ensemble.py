"""
Multi-Model Ensemble Downscaling Orchestrator.

Combines:
1. Physics-guided Orographic & Environmental Lapse Rate model
2. Statistical ML Regressor (XGBoost)
3. Deep Learning Residual U-Net (PyTorch)
4. Conservation of Mass/Energy Reconciler
5. Uncertainty Quantification Engine
"""

from typing import List, Dict, Any, Optional
import numpy as np
from src.downscaling.lapse_rate import OrographicPhysicsDownscaler
from src.downscaling.ml_regressor import MLDownscaler
from src.downscaling.unet_pipeline import UNetDownscaler
from src.downscaling.reconciliation import ForecastReconciler
from src.downscaling.uncertainty import UncertaintyEngine

class EnsembleDownscaler:
    def __init__(self):
        self.physics = OrographicPhysicsDownscaler()
        self.ml = MLDownscaler()
        self.unet = UNetDownscaler()
        self.reconciler = ForecastReconciler()
        self.uq = UncertaintyEngine()

    def downscale_block(
        self,
        block_id: str,
        block_forecast: Dict[str, float],
        panchayats_data: List[Dict[str, Any]],
        block_stats: Optional[Dict[str, Any]] = None,
        date_str: Optional[str] = None,
        lead_day: int = 1
    ) -> Dict[str, Any]:
        """
        Executes end-to-end downscaling for all Gram Panchayats in a block.
        """
        block_stats = block_stats or {}
        mean_elev = float(block_stats.get("mean_elevation_m", 550.0))

        raw_panchayat_results = []

        for p in panchayats_data:
            props = p.get("properties", p)
            terrain = props.get("terrain", {})
            if not terrain:
                terrain = {
                    "elevation_m": props.get("elevation_m", mean_elev),
                    "slope_deg": props.get("slope_deg", 1.5),
                    "monsoon_exposure": props.get("monsoon_exposure", 0.0),
                    "ruggedness_m": props.get("ruggedness_m", 15.0),
                    "distance_to_coast_km": props.get("distance_to_coast_km", 120.0),
                    "upwind_barrier_m": props.get("upwind_barrier_m", 0.0)
                }

            # 1. Physics Model
            phys_res = self.physics.downscale_panchayat_physics(
                block_forecast=block_forecast,
                panchayat_terrain=terrain,
                block_mean_elevation=mean_elev
            )

            # 2. ML Regressor
            ml_res = self.ml.predict_panchayat_weather(
                block_forecast=block_forecast,
                panchayat_props=props,
                date_str=date_str,
                lead_day=lead_day
            )

            # 3. Ensemble Blending
            # Weight: 60% physics (strict terrain constraints) + 40% ML statistical corrections
            if self.ml.is_loaded():
                ens_rain = 0.55 * phys_res["rainfall_mm"] + 0.45 * ml_res["ml_rainfall_mm"]
                ens_prob = 0.50 * phys_res["rainfall_probability_pct"] + 0.50 * ml_res["ml_rainfall_probability_pct"]
            else:
                ens_rain = phys_res["rainfall_mm"]
                ens_prob = phys_res["rainfall_probability_pct"]

            downscaled_weather = {
                "rainfall_mm": round(float(ens_rain), 2),
                "rainfall_probability_pct": round(float(ens_prob), 1),
                "tmax_c": phys_res["tmax_c"],
                "tmin_c": phys_res["tmin_c"],
                "rh_max_pct": phys_res["rh_max_pct"],
                "rh_min_pct": phys_res["rh_min_pct"],
                "wind_speed_kmh": phys_res["wind_speed_kmh"],
                "wind_direction_deg": phys_res["wind_direction_deg"],
                "delta_elevation_m": phys_res["delta_elevation_m"],
                "orographic_factor": phys_res["orographic_factor"]
            }

            # 4. Uncertainty Quantification
            rain_uq = self.uq.estimate_uncertainty(
                weather_value=downscaled_weather["rainfall_mm"],
                parameter="rainfall_mm",
                terrain=terrain,
                station_distance_km=float(props.get("distance_to_station_km", 15.0))
            )

            tmax_uq = self.uq.estimate_uncertainty(
                weather_value=downscaled_weather["tmax_c"],
                parameter="tmax_c",
                terrain=terrain
            )

            pid = props.get("panchayat_id") or props.get("GPCODE") or "UNKNOWN_GP"
            pname = props.get("name") or props.get("panchayat_name") or props.get("GPNAME") or "Panchayat"
            area = float(props.get("area_km2") or props.get("area_sqkm") or 5.0)

            raw_panchayat_results.append({
                "panchayat_id": pid,
                "panchayat_name": pname,
                "area_km2": area,
                "centroid_lat": float(props.get("centroid_lat") or props.get("lat") or 18.5),
                "centroid_lon": float(props.get("centroid_lon") or props.get("lon") or 74.0),
                "elevation_m": float(terrain.get("elevation_m", mean_elev)),
                "downscaled_weather": downscaled_weather,
                "uncertainty": {
                    "rainfall": rain_uq,
                    "tmax": tmax_uq,
                    "overall_support": rain_uq["support_level"]
                },
                "geometry": p.get("geometry")
            })

        # 5. Mass & Energy Conservation Reconciliation across all panchayats in the block
        reconciled_panchayats = self.reconciler.reconcile_block_panchayats(
            panchayat_predictions=raw_panchayat_results,
            block_forecast=block_forecast
        )

        return {
            "block_id": block_id,
            "panchayat_count": len(reconciled_panchayats),
            "synoptic_block_forecast": block_forecast,
            "lead_day": lead_day,
            "panchayats": reconciled_panchayats
        }
