"""
Geospatial Data API Routes.
Provides administrative hierarchy, block metadata, and Gram Panchayat GeoJSON polygons.
"""

from fastapi import APIRouter, HTTPException
import json
import os
from pathlib import Path
from src.core.config import config

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
