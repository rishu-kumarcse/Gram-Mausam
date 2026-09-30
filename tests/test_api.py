"""
API Integration Tests using FastAPI TestClient.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("test_health passed!")

def test_districts_geo():
    res = client.get("/api/v1/geo/districts")
    assert res.status_code == 200
    data = res.json()
    assert "districts" in data
    assert "Pune" in data["districts"]
    print("test_districts_geo passed!")

def test_panchayats_geojson():
    res = client.get("/api/v1/geo/panchayats/IND.20.26.1_1")
    assert res.status_code == 200
    geo = res.json()
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) > 0
    print("test_panchayats_geojson passed!")

def test_block_downscaling_endpoint():
    payload = {
        "block_id": "IND.20.26.1_1",
        "rainfall_mm": 14.0,
        "rainfall_probability_pct": 70.0,
        "tmax_c": 31.0,
        "tmin_c": 21.0,
        "rh_max_pct": 85.0,
        "rh_min_pct": 55.0,
        "wind_speed_kmh": 12.0,
        "wind_direction_deg": 245.0
    }
    res = client.post("/api/v1/downscale/block", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "panchayats" in data["result"]
    assert len(data["result"]["panchayats"]) > 0
    print("test_block_downscaling_endpoint passed!")

def test_benchmark_endpoint():
    payload = {
        "block_id": "IND.20.26.1_1",
        "rainfall_mm": 15.0
    }
    res = client.post("/api/v1/downscale/benchmark", json=payload)
    assert res.status_code == 200
    assert "benchmark_results" in res.json()
    print("test_benchmark_endpoint passed!")

def test_advisory_generate_and_broadcast():
    gen_res = client.post("/api/v1/advisory/generate", json={
        "panchayat_name": "Baramati Rural",
        "crop_key": "wheat",
        "stage_key": "crown_root",
        "weather": {"rainfall_mm": 12.0, "rainfall_probability_pct": 80.0, "tmax_c": 30.0, "tmin_c": 20.0, "rh_max_pct": 85.0, "wind_speed_kmh": 14.0}
    })
    assert gen_res.status_code == 200
    adv = gen_res.json()["advisory"]

    # Test broadcast in Marathi
    bcast_res = client.post("/api/v1/advisory/broadcast", json={
        "advisory_payload": adv,
        "language": "mr"
    })
    assert bcast_res.status_code == 200
    bcast_data = bcast_res.json()
    assert "whatsapp_text" in bcast_data
    assert "sms_text" in bcast_data
    assert "voice_script" in bcast_data
    print("test_advisory_generate_and_broadcast passed!")

if __name__ == "__main__":
    test_health()
    test_districts_geo()
    test_panchayats_geojson()
    test_block_downscaling_endpoint()
    test_benchmark_endpoint()
    test_advisory_generate_and_broadcast()
    print("All API integration tests passed successfully!")
