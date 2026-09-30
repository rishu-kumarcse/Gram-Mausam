"""
Agro-Meteorological Advisory API Routes.

Endpoints for:
1. Querying supported crops, phenological stages, and Kc coefficients
2. Generating full agromet advisories for downscaled panchayat weather
3. Formatting multilingual WhatsApp, SMS, and audio speech payloads
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from src.advisory.advisory_generator import AgrometAdvisoryGenerator
from src.advisory.crop_calendar import CropCalendar
from src.vernacular.translator import VernacularTranslator
from src.vernacular.broadcaster import AgrometBroadcaster

router = APIRouter(prefix="/api/v1/advisory", tags=["Agro-Meteorological Advisories"])

advisor = AgrometAdvisoryGenerator()
calendar = CropCalendar()

class AdvisoryGenerateRequest(BaseModel):
    panchayat_name: str = "Baramati Village"
    crop_key: str = "wheat"
    stage_key: Optional[str] = "crown_root"
    support_level: str = "HIGH"
    weather: Dict[str, float] = Field(default_factory=lambda: {
        "rainfall_mm": 5.0,
        "rainfall_probability_pct": 60.0,
        "tmax_c": 31.0,
        "tmin_c": 21.0,
        "rh_max_pct": 82.0,
        "rh_min_pct": 55.0,
        "wind_speed_kmh": 12.0
    })

class BroadcastFormatRequest(BaseModel):
    advisory_payload: Dict[str, Any]
    language: str = "mr" # en, hi, mr, kn, te, ta

@router.get("/crops")
def list_crops():
    """Lists available crops and their phenological development stages."""
    return {
        "status": "success",
        "crops": calendar.crops
    }

@router.get("/languages")
def list_languages():
    """Lists supported Indian vernacular languages."""
    return {
        "status": "success",
        "languages": VernacularTranslator.get_supported_languages()
    }

@router.post("/generate")
def generate_advisory(req: AdvisoryGenerateRequest):
    """
    Synthesizes actionable agromet advisory based on downscaled micro-weather.
    """
    adv = advisor.generate_panchayat_advisory(
        panchayat_name=req.panchayat_name,
        weather=req.weather,
        crop_key=req.crop_key,
        stage_key=req.stage_key,
        support_level=req.support_level
    )
    return {"status": "success", "advisory": adv}

@router.post("/broadcast")
def format_broadcast_channels(req: BroadcastFormatRequest):
    """
    Formats the advisory into WhatsApp, SMS, and Voice Speech formats in target language.
    """
    payload = req.advisory_payload
    lang = req.language

    # Localize advisory
    localized = VernacularTranslator.localize_advisory(payload, lang=lang)

    # Format channels
    whatsapp = AgrometBroadcaster.format_whatsapp_bulletin(localized)
    sms = AgrometBroadcaster.format_sms_alert(localized)
    voice_script = localized.get("voice_script") or AgrometBroadcaster.format_voice_script(localized)

    return {
        "status": "success",
        "language": lang,
        "whatsapp_text": whatsapp,
        "sms_text": sms,
        "voice_script": voice_script
    }

class AskAIRequest(BaseModel):
    query: str
    panchayat_name: str = "Baramati Village"
    weather: Dict[str, Any] = Field(default_factory=dict)
    crop_info: Dict[str, Any] = Field(default_factory=dict)
    spray_status: Optional[str] = "GO"
    irrigation_action: Optional[str] = "IRRIGATE"
    pest_alerts: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = "mr"

@router.post("/ask-ai")
def ask_ai_copilot(req: AskAIRequest):
    """
    Interacts with Groq LLM (Krishi Mitr) using grounded local panchayat micro-weather.
    """
    from src.advisory.ai_copilot import ai_copilot
    res = ai_copilot.ask(
        query=req.query,
        panchayat_name=req.panchayat_name,
        weather=req.weather,
        crop_info=req.crop_info,
        spray_status=req.spray_status,
        irrigation_action=req.irrigation_action,
        pest_alerts=req.pest_alerts,
        language=req.language or "mr"
    )
    return res
