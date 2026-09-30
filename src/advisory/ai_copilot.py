"""
Krishi Mitr - AI Agromet Advisory Copilot powered by Groq.

Leverages Groq ultra-fast LLM inference to provide intelligent, contextual,
and conversational agro-meteorological advisory services grounded in:
1. Local Gram Panchayat downscaled weather
2. Crop developmental stage & Kc factor
3. Spraying window feasibility (drift & wash-off limits)
4. Irrigation NIR & ET0 deficit
5. Bio-climatic pest/disease outbreak warnings
6. ICAR-AICRPAM & IMD GKMS regulatory standards
"""

import json
import urllib.request
from typing import Dict, Any, Optional, List
from src.core.config import config

class AgrometAICopilot:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.groq.api_key
        self.endpoint = config.groq.endpoint
        self.primary_model = config.groq.model
        self.fallback_models = config.groq.fallback_models

    def ask(
        self,
        query: str,
        panchayat_name: str,
        weather: Dict[str, Any],
        crop_info: Dict[str, Any],
        spray_status: Optional[str] = "GO",
        irrigation_action: Optional[str] = "IRRIGATE",
        pest_alerts: Optional[List[Dict[str, Any]]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates an agronomic response grounded in the panchayat's downscaled data.
        """
        pest_str = ", ".join([p.get("name", "") for p in (pest_alerts or [])]) or "None detected"

        system_prompt = (
            "You are 'Krishi Mitr', an expert AI Agricultural & Meteorological Advisor for the "
            "India Meteorological Department (IMD) and Indian Council of Agricultural Research (ICAR). "
            "You provide practical, honest, scientifically sound advice to Indian farmers and extension officers.\n\n"
            "CURRENT GROUND CONTEXT FOR THE FARMER'S VILLAGE:\n"
            f"- Gram Panchayat: {panchayat_name}\n"
            f"- Downscaled Rainfall: {weather.get('rainfall_mm', 0.0)} mm (Probability: {weather.get('rainfall_probability_pct', 0)}%)\n"
            f"- Temperature: Max {weather.get('tmax_c', 30.0)}°C / Min {weather.get('tmin_c', 20.0)}°C\n"
            f"- Wind Speed: {weather.get('wind_speed_kmh', 10.0)} km/h (Monsoon azimuth)\n"
            f"- Max Humidity: {weather.get('rh_max_pct', 70.0)}%\n"
            f"- Crop: {crop_info.get('name', 'Crop')} (Stage: {crop_info.get('stage_description', 'Vegetative')})\n"
            f"- Chemical Spray Window Status: {spray_status}\n"
            f"- Irrigation Recommendation: {irrigation_action}\n"
            f"- Active Pest/Disease Alerts: {pest_str}\n\n"
            "RULES:\n"
            "1. Ground your answer in the weather data above. Explain WHY (e.g. wind drift hazard, rainfall wash-off, moisture deficit).\n"
            "2. Keep the answer concise (2-4 bullet points or short paragraphs).\n"
            "3. If the user asks in Marathi, Hindi, Kannada, Telugu, or Tamil, respond fluently in that language. "
            "If in English, respond in English.\n"
            "4. Always prioritize farmer safety and input cost reduction."
        )

        user_content = query.strip()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        models_to_try = [self.primary_model] + self.fallback_models
        last_error = None

        for model_name in models_to_try:
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 400
            }

            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "GramMausam/2.0"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    raw_res = json.loads(response.read().decode("utf-8"))
                    answer = raw_res["choices"][0]["message"]["content"]
                    return {
                        "status": "success",
                        "model_used": model_name,
                        "panchayat_name": panchayat_name,
                        "answer": answer
                    }
            except Exception as e:
                last_error = str(e)
                continue

        # If API is offline / uncontactable, return grounded deterministic response
        fallback_ans = (
            f"Based on downscaled forecasts for {panchayat_name}: "
            f"Expected rain is {weather.get('rainfall_mm', 0)} mm with {weather.get('rainfall_probability_pct', 0)}% chance. "
            f"Spraying Status: {spray_status}. Irrigation Action: {irrigation_action}. "
            f"Pest Alerts: {pest_str}. (Groq response fallback: {last_error})"
        )
        return {
            "status": "fallback",
            "model_used": "DeterministicRulesEngine",
            "panchayat_name": panchayat_name,
            "answer": fallback_ans
        }

ai_copilot = AgrometAICopilot()
