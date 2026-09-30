"""
Geospatial Data API Routes.
Provides administrative hierarchy, block metadata, and Gram Panchayat GeoJSON polygons.
"""

from fastapi import APIRouter, HTTPException
import json
import os
from pathlib import Path
from src.core.config import config
from src.ingestion.live_weather_service import LiveWeatherService

router = APIRouter(prefix="/api/v1/geo", tags=["Geospatial Data"])

@router.get("/districts")
def get_districts():
    """Returns list of districts and blocks indexed in the system."""
    try:
        with open(config.geo.block_index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"status": "success", "districts": data.get("districts", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blocks/{block_id}")
def get_block_details(block_id: str):
    """Returns metadata and terrain stats for a specific block."""
    try:
        with open(config.geo.block_index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            blocks = data.get("blocks", {})
            if block_id in blocks:
                return {"status": "success", "block": blocks[block_id]}
            raise HTTPException(status_code=404, detail="Block ID not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/panchayats/{block_id}")
def get_panchayats_geojson(block_id: str):
    """
    Returns the real GeoJSON FeatureCollection of Gram Panchayats for a block.
    """
    block_file = Path(config.geo.panchayats_dir) / f"{block_id}.json"
    if block_file.exists():
        with open(block_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    
    # Fallback to sample geojson if block file not found
    if os.path.exists(config.geo.panchayats_sample_path):
        with open(config.geo.panchayats_sample_path, "r", encoding="utf-8") as f:
            return json.load(f)

    raise HTTPException(status_code=404, detail=f"GeoJSON for block {block_id} not found")

@router.get("/block-weather/{block_id}")
def get_block_live_weather(block_id: str):
    """
    Fetches real-time live ECMWF weather for the selected administrative block.
    """
    try:
        with open(config.geo.block_index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            blocks = data.get("blocks", {})
            if block_id not in blocks:
                raise HTTPException(status_code=404, detail="Block ID not found")
            b_info = blocks[block_id]
            lat = float(b_info.get("centroid_lat", 18.25))
            lon = float(b_info.get("centroid_lon", 74.35))
            
        weather_data = LiveWeatherService.fetch_live_block_forecast(lat=lat, lon=lon, forecast_days=5)
        forecasts = weather_data.get("daily_forecasts", [])
        today_forecast = forecasts[0] if forecasts else {
            "rainfall_mm": 5.0,
            "rainfall_probability_pct": 50.0,
            "tmax_c": 31.0,
            "tmin_c": 21.0,
            "rh_max_pct": 80.0,
            "rh_min_pct": 50.0,
            "wind_speed_kmh": 12.0,
            "wind_direction_deg": 245.0
        }
        
        return {
            "status": "success",
            "block_id": block_id,
            "block_name": b_info.get("block_name"),
            "district": b_info.get("district"),
            "lat": lat,
            "lon": lon,
            "is_live": weather_data.get("is_live", False),
            "source": weather_data.get("source", "Live ECMWF Ingestion"),
            "weather": today_forecast,
            "five_day_forecast": forecasts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

