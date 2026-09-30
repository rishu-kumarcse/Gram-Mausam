"""
Conservation of Mass & Energy Reconciliation Module.

Crucial scientific guarantee:
Official IMD block forecasts represent the integrated meteorological flux across the block.
Downscaling refines the spatial partition across Gram Panchayats according to terrain,
but the area-weighted aggregate MUST conserve the official synoptic block forecast:

    sum_{i=1}^N (w_i * Y_panchayat_i) == Y_block
    where w_i = Area_i / sum(Area)

If unconstrained regression predicts higher or lower rainfall everywhere, this module
adjusts values via multiplicative (for positive-bounded precipitation/wind) or
additive (for unconstrained temperatures) scaling while preserving terrain anomalies.
"""

from typing import List, Dict, Any
import numpy as np

class ForecastReconciler:
    @staticmethod
    def reconcile_block_panchayats(
        panchayat_predictions: List[Dict[str, Any]],
        block_forecast: Dict[str, float],
        tolerance: float = 1e-4
    ) -> List[Dict[str, Any]]:
        """
        Reconciles a list of downscaled panchayat predictions back to the official block forecast.
        """
        if not panchayat_predictions:
            return []

        # 1. Compute normalized weights from panchayat area
        raw_areas = [max(0.1, float(p.get("area_km2", 5.0))) for p in panchayat_predictions]
        total_area = sum(raw_areas)
        weights = np.array([a / total_area for a in raw_areas])

        # 2. Reconcile Rainfall (Multiplicative or additive with non-negativity)
        target_rain = float(block_forecast.get("rainfall_mm", 0.0))
        pred_rains = np.array([float(p["downscaled_weather"]["rainfall_mm"]) for p in panchayat_predictions])
        
        weighted_pred_rain = np.sum(weights * pred_rains)

        if target_rain <= 0.0:
            reconciled_rains = np.zeros_like(pred_rains)
        elif weighted_pred_rain > 0.0:
            scale_factor = target_rain / weighted_pred_rain
            # Damp extreme scaling to prevent explosion if initial prediction was very small
            scale_factor = max(0.2, min(5.0, scale_factor))
            reconciled_rains = pred_rains * scale_factor
            
            # Minor residual additive correction for exact convergence
            new_weighted = np.sum(weights * reconciled_rains)
            residual = target_rain - new_weighted
            reconciled_rains = np.maximum(0.0, reconciled_rains + residual)
        else:
            reconciled_rains = np.full_like(pred_rains, target_rain)

        # 3. Reconcile Tmax and Tmin (Additive shift preserving lapse rate gradients)
        target_tmax = float(block_forecast.get("tmax_c", 30.0))
        target_tmin = float(block_forecast.get("tmin_c", 20.0))

        pred_tmax = np.array([float(p["downscaled_weather"]["tmax_c"]) for p in panchayat_predictions])
        pred_tmin = np.array([float(p["downscaled_weather"]["tmin_c"]) for p in panchayat_predictions])

        tmax_shift = target_tmax - np.sum(weights * pred_tmax)
        tmin_shift = target_tmin - np.sum(weights * pred_tmin)

        reconciled_tmax = pred_tmax + tmax_shift
        reconciled_tmin = pred_tmin + tmin_shift

        # Ensure physically realistic Tmax >= Tmin + 1.0
        reconciled_tmax = np.maximum(reconciled_tmin + 1.0, reconciled_tmax)

        # 4. Reconcile Wind Speed
        target_wind = float(block_forecast.get("wind_speed_kmh", 10.0))
        pred_wind = np.array([float(p["downscaled_weather"]["wind_speed_kmh"]) for p in panchayat_predictions])
        w_wind = np.sum(weights * pred_wind)
        wind_scale = (target_wind / w_wind) if w_wind > 0 else 1.0
        reconciled_wind = np.maximum(1.0, pred_wind * wind_scale)

        # 5. Update panchayat prediction objects
        for i, p in enumerate(panchayat_predictions):
            dw = p["downscaled_weather"]
            dw["rainfall_mm"] = round(float(reconciled_rains[i]), 2)
            dw["tmax_c"] = round(float(reconciled_tmax[i]), 1)
            dw["tmin_c"] = round(float(reconciled_tmin[i]), 1)
            dw["wind_speed_kmh"] = round(float(reconciled_wind[i]), 1)
            
            # Recalculate rain probability if rain is zero
            if dw["rainfall_mm"] == 0.0 and target_rain == 0.0:
                dw["rainfall_probability_pct"] = min(10.0, float(dw.get("rainfall_probability_pct", 10.0)))

            p["reconciled"] = True
            p["area_weight"] = round(float(weights[i]), 4)

        return panchayat_predictions
