"""
FastAPI Master Application for GramMausam-26074.
Next-Gen Panchayat-Level Weather Downscaling & Agro-Meteorological Advisory Intelligence Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
import json

from src.core.config import config
from src.api.routes_geo import router as geo_router
from src.api.routes_downscale import router as downscale_router
from src.api.routes_advisory import router as advisory_router
from src.api.routes_officer import router as officer_router
from src.ingestion.live_weather_service import LiveWeatherService

app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="Next-Gen Panchayat-Level Weather Downscaling & Agro-Meteorological Advisory Services (SIH Problem Statement ID 26074 - MoES / IMD)"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(geo_router)
app.include_router(downscale_router)
app.include_router(advisory_router)
app.include_router(officer_router)

# Live Forecast Ingestion Endpoint
@app.get("/api/v1/ingestion/live-block")
def fetch_live_block(lat: float = 18.2189, lon: float = 74.4580, days: int = 5):
    """Fetches real-time weather predictions from open NWP / ECMWF connectors."""
    data = LiveWeatherService.fetch_live_block_forecast(lat=lat, lon=lon, forecast_days=days)
    return {"status": "success", "data": data}

@app.get("/api/v1/samples/imd-bulletin")
def get_sample_imd_bulletin():
    """Returns sample official IMD 5-day Block Bulletin."""
    bulletin_file = Path(config.geo.blocks_path).parent.parent / "samples" / "imd_block_forecast_bulletin.json"
    if bulletin_file.exists():
        with open(bulletin_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "error", "message": "Sample bulletin not found"}

# Mount Static Files (Frontend UI)
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": config.app_name,
        "version": config.app_version,
        "problem_statement": "SIH26074 - MoES / IMD"
    }
