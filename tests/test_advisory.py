"""
Unit Tests for Agro-Meteorological Advisories, Crop Phenology, Pests, and Irrigation.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.advisory.spray_window import SprayWindowAdvisor
from src.advisory.irrigation_advisor import IrrigationAdvisor
from src.advisory.pest_disease import PestDiseaseAdvisor
from src.advisory.crop_calendar import CropCalendar
from src.advisory.agromet_rules import AgrometRuleEngine
from src.advisory.advisory_generator import AgrometAdvisoryGenerator

def test_spray_window_logic():
    # Rainy windy weather should trigger AVOID
    bad_weather = {"wind_speed_kmh": 22.0, "rainfall_mm": 5.0, "rainfall_probability_pct": 80.0, "tmax_c": 30.0, "rh_min_pct": 50.0}
    res_bad = SprayWindowAdvisor.evaluate_spray_conditions(bad_weather)
    assert res_bad["status"] == "AVOID"

    # Calm dry morning should trigger GO
    good_weather = {"wind_speed_kmh": 6.0, "rainfall_mm": 0.0, "rainfall_probability_pct": 5.0, "tmax_c": 28.0, "rh_min_pct": 55.0}
    res_good = SprayWindowAdvisor.evaluate_spray_conditions(good_weather)
    assert res_good["status"] == "GO"
    print("test_spray_window_logic passed!")

def test_irrigation_logic():
    # When heavy rain falls, irrigation should be skipped
    rainy_weather = {"tmax_c": 30.0, "tmin_c": 20.0, "rainfall_mm": 18.0, "rainfall_probability_pct": 85.0}
    res = IrrigationAdvisor.calculate_irrigation_requirement(rainy_weather, crop_kc=1.0)
    assert res["action"] == "SKIP"
    assert res["effective_rainfall_mm"] > 0

    # When dry, irrigation should be required
    dry_weather = {"tmax_c": 34.0, "tmin_c": 20.0, "rainfall_mm": 0.0, "rainfall_probability_pct": 0.0}
    res_dry = IrrigationAdvisor.calculate_irrigation_requirement(dry_weather, crop_kc=1.15)
    assert res_dry["action"] == "IRRIGATE"
    assert res_dry["net_deficit_mm"] > 0
    print("test_irrigation_logic passed!")

def test_pest_models():
    pest_engine = PestDiseaseAdvisor()
    # Late blight trigger: Cool & wet (Tomato)
    blight_weather = {"tmax_c": 19.0, "tmin_c": 14.0, "rh_max_pct": 92.0, "rainfall_mm": 3.0, "rainfall_probability_pct": 80.0}
    risks = pest_engine.evaluate_risks(blight_weather, "tomato")
    blight_found = any(r["pest_id"] == "late_blight" for r in risks)
    assert blight_found
    print("test_pest_models passed!")

def test_master_advisory_generator():
    generator = AgrometAdvisoryGenerator()
    weather = {
        "rainfall_mm": 8.0,
        "rainfall_probability_pct": 65.0,
        "tmax_c": 31.0,
        "tmin_c": 21.0,
        "rh_max_pct": 85.0,
        "rh_min_pct": 60.0,
        "wind_speed_kmh": 12.0
    }
    adv = generator.generate_panchayat_advisory(
        panchayat_name="Koregaon",
        weather=weather,
        crop_key="wheat",
        stage_key="crown_root"
    )
    assert adv["panchayat_name"] == "Koregaon"
    assert "spray_advisory" in adv
    assert "irrigation_advisory" in adv
    assert "pest_disease_alerts" in adv
    print("test_master_advisory_generator passed!")

if __name__ == "__main__":
    test_spray_window_logic()
    test_irrigation_logic()
    test_pest_models()
    test_master_advisory_generator()
    print("All advisory unit tests passed successfully!")
