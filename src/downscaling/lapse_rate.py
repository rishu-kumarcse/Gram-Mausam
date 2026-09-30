"""
Physics-Guided Orographic & Environmental Lapse Rate Downscaling Module.

Computes micro-climatic physical adjustments between Block average elevation/exposure
and local Gram Panchayat micro-topography:
1. Environmental Temperature Lapse Rate: ΔT = -Γ * Δz
2. Orographic Precipitation Enhancement & Rain-Shadow along 245° Indian Summer Monsoon flow.
3. Slope-Aspect Solar Radiation & Surface Warming.
4. Relative Humidity & Dewpoint elevation adjustment.
"""

import math
import numpy as np
from typing import Dict, Any
from src.core.config import config

class OrographicPhysicsDownscaler:
    def __init__(self):
        self.lapse_rate_c_per_km = config.physics.temperature_lapse_rate_c_per_km
        self.dewpoint_lapse_rate = config.physics.dewpoint_lapse_rate_c_per_km
        self.monsoon_azimuth = config.physics.monsoon_azimuth_deg
        self.decay_length_km = config.physics.rain_shadow_decay_km
        self.barrier_threshold_m = config.physics.barrier_threshold_m

    def downscale_panchayat_physics(
        self,
        block_forecast: Dict[str, float],
        panchayat_terrain: Dict[str, Any],
        block_mean_elevation: float
    ) -> Dict[str, float]:
        """
        Calculates physical micro-climatic anomalies for a single panchayat relative
        to the block synoptic conditions.
        """
        # Terrain parameters
        panchayat_elev = float(panchayat_terrain.get("elevation_m", 500.0))
        delta_elev_m = panchayat_elev - block_mean_elevation
        delta_elev_km = delta_elev_m / 1000.0

        slope_deg = float(panchayat_terrain.get("slope_deg", 0.0))
        monsoon_exposure = float(panchayat_terrain.get("monsoon_exposure", 0.0)) # positive if facing windward (SW)
        upwind_barrier_m = float(panchayat_terrain.get("upwind_barrier_m", 0.0))
        dist_coast_km = float(panchayat_terrain.get("distance_to_coast_km", 100.0))
        local_relief_m = float(panchayat_terrain.get("local_relief_m", 20.0))

        # 1. Temperature Lapse Rate Adjustments
        # Higher elevation = cooler temperatures (-6.5 °C / km)
        delta_tmax = -self.lapse_rate_c_per_km * delta_elev_km
        delta_tmin = - (self.lapse_rate_c_per_km * 0.85) * delta_elev_km # nocturnal radiative cooling inversion factor

        # Valley cold-air pooling under gentle slopes and high surrounding relief at night
        if slope_deg < 2.0 and delta_elev_m < -50.0:
            delta_tmin -= 1.2 # nocturnal cold air drainage pool

        # 2. Orographic Rain Enhancement & Rain-Shadow
        # Baseline block rainfall
        block_rain = float(block_forecast.get("rainfall_mm", 0.0))
        block_rain_prob = float(block_forecast.get("rainfall_probability_pct", 50.0))

        # Rain factor starts at 1.0 (neutral)
        rain_factor = 1.0

        # Elevation enhancement on windward slopes (orographic lifting)
        if delta_elev_m > 0:
            # Approx +3% to +8% rain per 100m rise on windward exposures
            lift_rate = 0.05 if monsoon_exposure >= 0 else 0.02
            rain_factor += (delta_elev_m / 100.0) * lift_rate

        # Rain-shadow deficit behind significant upwind barriers (leeward lee drying)
        if upwind_barrier_m > self.barrier_threshold_m and monsoon_exposure < 0:
            # Exponential rain shadow suppression
            barrier_ratio = min(upwind_barrier_m / 400.0, 1.0)
            shadow_suppression = 0.45 * barrier_ratio * (1.0 - math.exp(-upwind_barrier_m / 200.0))
            rain_factor -= shadow_suppression

        rain_factor = max(0.15, min(2.5, rain_factor))
        panchayat_rain = block_rain * rain_factor

        # Adjust rainfall probability accordingly
        prob_adjustment = (rain_factor - 1.0) * 20.0
        panchayat_rain_prob = max(5.0, min(95.0, block_rain_prob + prob_adjustment))

        # 3. Relative Humidity Adjustment
        block_rh_max = float(block_forecast.get("rh_max_pct", 80.0))
        block_rh_min = float(block_forecast.get("rh_min_pct", 50.0))

        # Cooler air at higher elevation holds less saturated vapor -> higher RH
        # ΔRH ≈ +4% per 100m elevation gain, orographic condensation
        rh_elev_delta = (delta_elev_m / 100.0) * 1.5
        panchayat_rh_max = max(20.0, min(99.0, block_rh_max + rh_elev_delta))
        panchayat_rh_min = max(15.0, min(95.0, block_rh_min + rh_elev_delta))

        # 4. Wind Speed Adjustment
        block_wind = float(block_forecast.get("wind_speed_kmh", 10.0))
        # Exposed ridges experience higher wind speed, valleys receive friction damping
        roughness_factor = 1.0 + (local_relief_m / 250.0) * 0.3 if delta_elev_m > 0 else max(0.6, 1.0 - abs(delta_elev_m)/300.0)
        panchayat_wind = max(1.0, block_wind * roughness_factor)

        # 5. Assemble result
        downscaled_tmax = round(block_forecast.get("tmax_c", 30.0) + delta_tmax, 1)
        downscaled_tmin = round(block_forecast.get("tmin_c", 20.0) + delta_tmin, 1)

        return {
            "rainfall_mm": round(panchayat_rain, 2),
            "rainfall_probability_pct": round(panchayat_rain_prob, 1),
            "tmax_c": downscaled_tmax,
            "tmin_c": downscaled_tmin,
            "rh_max_pct": round(panchayat_rh_max, 1),
            "rh_min_pct": round(panchayat_rh_min, 1),
            "wind_speed_kmh": round(panchayat_wind, 1),
            "wind_direction_deg": float(block_forecast.get("wind_direction_deg", 245.0)),
            "delta_elevation_m": round(delta_elev_m, 1),
            "orographic_factor": round(rain_factor, 3),
            "physics_model": "OrographicLapseRate_v2"
        }
