"""
GramMausam-26074: Core Configuration and Constants.
Implements configuration management for downscaling algorithms, GIS, agronomic models, and API.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class PhysicsSettings(BaseModel):
    # Environmental lapse rate for temperature (approx -6.5 °C per km elevation rise)
    temperature_lapse_rate_c_per_km: float = 6.5
    # Dewpoint lapse rate (approx -2.0 °C per km)
    dewpoint_lapse_rate_c_per_km: float = 2.0
    # Prevailing Indian Summer Monsoon wind direction (degrees from North)
    monsoon_azimuth_deg: float = 245.0
    # Rain shadow decay length scale in km
    rain_shadow_decay_km: float = 18.0
    # Minimum elevation diff for significant barrier effect (meters)
    barrier_threshold_m: float = 80.0
    # IMD definition of rainy day threshold (mm)
    rainy_day_threshold_mm: float = 2.5

class MLSettings(BaseModel):
    unet_weights_path: str = str(BASE_DIR / "models" / "weights" / "unet_best_model.pt")
    xgboost_weights_path: str = str(BASE_DIR / "models" / "weights" / "xgboost_downscaler.joblib")
    confidence_quantile_low: float = 0.10  # P10
    confidence_quantile_median: float = 0.50 # P50
    confidence_quantile_high: float = 0.90 # P90
    max_reconciliation_iterations: int = 15

class AgronomicSettings(BaseModel):
    crop_db_path: str = str(BASE_DIR / "data" / "crops" / "crop_database.json")
    pest_db_path: str = str(BASE_DIR / "data" / "crops" / "pest_disease_models.json")
    spray_max_wind_kmh: float = 15.0
    spray_rain_prob_cutoff_pct: float = 25.0
    spray_rh_min_pct: float = 40.0
    spray_rh_max_pct: float = 75.0
    heavy_rain_fertilizer_cutoff_mm: float = 20.0

class GeoSettings(BaseModel):
    blocks_path: str = str(BASE_DIR / "data" / "geo" / "blocks_mh.json")
    block_index_path: str = str(BASE_DIR / "data" / "geo" / "block_index.json")
    panchayats_sample_path: str = str(BASE_DIR / "data" / "geo" / "panchayats_sample.geojson")
    panchayats_dir: str = str(BASE_DIR / "data" / "geo" / "panchayats_by_block")

class GroqSettings(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    model: str = "openai/gpt-oss-120b"
    fallback_models: list = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]
    endpoint: str = "https://api.groq.com/openai/v1/chat/completions"

class AppConfig(BaseModel):
    app_name: str = "GramMausam-26074"
    app_version: str = "2.0.0"
    debug: bool = False
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "7860")))
    physics: PhysicsSettings = Field(default_factory=PhysicsSettings)
    ml: MLSettings = Field(default_factory=MLSettings)
    agronomic: AgronomicSettings = Field(default_factory=AgronomicSettings)
    geo: GeoSettings = Field(default_factory=GeoSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)

config = AppConfig()
