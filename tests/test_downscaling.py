"""
Unit Tests for Weather Downscaling Algorithms, Models, Reconciliation, and UQ.
"""

import sys
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.downscaling.lapse_rate import OrographicPhysicsDownscaler
from src.downscaling.ml_regressor import MLDownscaler
from src.downscaling.unet_pipeline import UNetDownscaler
from src.downscaling.reconciliation import ForecastReconciler
from src.downscaling.uncertainty import UncertaintyEngine

def test_physics_lapse_rate():
    downscaler = OrographicPhysicsDownscaler()
    block_fc = {
        "rainfall_mm": 10.0,
        "rainfall_probability_pct": 60.0,
        "tmax_c": 32.0,
        "tmin_c": 22.0,
        "rh_max_pct": 80.0,
        "rh_min_pct": 50.0,
        "wind_speed_kmh": 12.0
    }
    
    # Panchayat 500m higher than block mean
    terrain_high = {
        "elevation_m": 1050.0,
        "slope_deg": 4.0,
        "monsoon_exposure": 0.5, # windward
        "upwind_barrier_m": 0.0,
        "local_relief_m": 50.0
    }
    
    res = downscaler.downscale_panchayat_physics(block_fc, terrain_high, block_mean_elevation=550.0)
    
    # 500m higher should be cooler by approx 0.5 * 6.5 ≈ 3.25 °C
    assert res["tmax_c"] < block_fc["tmax_c"]
    assert res["rainfall_mm"] >= block_fc["rainfall_mm"] # Orographic enhancement
    print("test_physics_lapse_rate passed!")

def test_reconciliation_conservation():
    reconciler = ForecastReconciler()
    target_block_rain = 15.0
    block_fc = {"rainfall_mm": target_block_rain, "tmax_c": 30.0, "tmin_c": 20.0, "wind_speed_kmh": 10.0}

    sample_predictions = [
        {"area_km2": 10.0, "downscaled_weather": {"rainfall_mm": 22.0, "tmax_c": 28.0, "tmin_c": 19.0, "wind_speed_kmh": 12.0}},
        {"area_km2": 20.0, "downscaled_weather": {"rainfall_mm": 11.0, "tmax_c": 31.0, "tmin_c": 21.0, "wind_speed_kmh": 9.0}},
        {"area_km2": 10.0, "downscaled_weather": {"rainfall_mm": 18.0, "tmax_c": 29.5, "tmin_c": 20.0, "wind_speed_kmh": 10.5}}
    ]

    reconciled = reconciler.reconcile_block_panchayats(sample_predictions, block_fc)
    
    # Compute area-weighted average
    total_area = sum(p["area_km2"] for p in reconciled)
    weighted_rain = sum(p["area_km2"] * p["downscaled_weather"]["rainfall_mm"] for p in reconciled) / total_area

    assert abs(weighted_rain - target_block_rain) < 0.05
    print("test_reconciliation_conservation passed! (Weighted average exactly matches block forecast)")

def test_unet_raster_shape():
    unet = UNetDownscaler()
    grid = unet.infer_continuous_raster(base_rainfall_mm=12.0, grid_shape=(16, 16))
    assert grid.shape == (16, 16)
    assert np.all(grid >= 0.0)
    print("test_unet_raster_shape passed!")

def test_uncertainty_quantiles():
    uq = UncertaintyEngine()
    res = uq.estimate_uncertainty(weather_value=20.0, parameter="rainfall_mm", terrain={"elevation_m": 600.0})
    assert res["p10"] <= res["p50"] <= res["p90"]
    assert res["support_level"] in ("HIGH", "MODERATE", "LOW")
    print("test_uncertainty_quantiles passed!")

if __name__ == "__main__":
    test_physics_lapse_rate()
    test_reconciliation_conservation()
    test_unet_raster_shape()
    test_uncertainty_quantiles()
    print("All downscaling unit tests passed successfully!")
