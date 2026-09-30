"""
WhatsApp, SMS, and Voice Alert Formatter.

Generates broadcast-ready messages formatted specifically for:
1. WhatsApp Agri-Bulletins (emojis, bold headers, clear action bullets)
2. 160-Character SMS Alerts (concise, high-urgency)
3. Voice / Audio scripts with clean phonetic pauses
"""

from typing import Dict, Any

class AgrometBroadcaster:
    @staticmethod
    def format_whatsapp_bulletin(advisory: Dict[str, Any]) -> str:
        pname = advisory.get("panchayat_name", "Gram Panchayat")
        cinfo = advisory.get("crop", {})
        cname = cinfo.get("name", "General Crop")
        stage = cinfo.get("stage_description", "Vegetative")
        w = advisory.get("weather_summary", {})
        spray = advisory.get("spray_advisory", {})
        irrig = advisory.get("irrigation_advisory", {})
        pests = advisory.get("pest_disease_alerts", [])
        actions = advisory.get("agronomic_action_items", [])
        support = advisory.get("support_level", "HIGH")

        spray_emoji = "🟢" if spray.get("status") == "GO" else ("🟡" if spray.get("status") == "CAUTION" else "🔴")
        irrig_emoji = "💧" if irrig.get("action") in ("IRRIGATE", "LIGHT") else "⏸️"

        lines = [
            f"🌾 *IMD-GKMS HYPERLOCAL WEATHER ADVISORY* 🌾",
            f"📍 *Panchayat:* {pname}",
            f"🌱 *Crop:* {cname} ({stage})",
            f"🎯 *Forecast Reliability:* {support} Confidence",
            f"────────────────────────",
            f"🌤️ *24h Downscaled Weather:*",
            f"• Rainfall: *{w.get('rainfall_mm', 0):.1f} mm* (Prob: {w.get('rainfall_probability_pct', 0):.0f}%)",
            f"• Temp (Max/Min): *{w.get('tmax_c', 0):.1f}°C / {w.get('tmin_c', 0):.1f}°C*",
            f"• Wind Speed: *{w.get('wind_speed_kmh', 0):.1f} km/h*",
            f"• Max Humidity: *{w.get('rh_max_pct', 0):.0f}%*",
            f"────────────────────────",
            f"{spray_emoji} *Chemical Spray Window:* *{spray.get('status')}*",
            f"👉 {spray.get('summary', '')}",
            f"⏰ Best Time: {spray.get('best_window', 'N/A')}",
            f"",
            f"{irrig_emoji} *Irrigation Guidance:* *{irrig.get('action')}*",
            f"👉 {irrig.get('guidance', '')}",
        ]

        if pests:
            lines.append(f"────────────────────────")
            lines.append(f"⚠️ *Pest & Disease Alerts:*")
            for p in pests:
                lines.append(f"• *{p.get('name')}* [{p.get('severity')}]: {p.get('action_recommendation')}")

        if actions:
            lines.append(f"────────────────────────")
            lines.append(f"📋 *Special Agronomic Actions:*")
            for a in actions:
                lines.append(f"• *{a.get('headline')}*: {a.get('action')}")

        lines.append(f"────────────────────────")
        lines.append(f"📢 _Issued by Agromet Extension Office | Ministry of Earth Sciences_")

        return "\n".join(lines)

    @staticmethod
    def format_sms_alert(advisory: Dict[str, Any]) -> str:
        pname = advisory.get("panchayat_name", "GP")
        w = advisory.get("weather_summary", {})
        spray = advisory.get("spray_advisory", {}).get("status", "GO")
        irrig = advisory.get("irrigation_advisory", {}).get("action", "IRRIGATE")
        rain = w.get("rainfall_mm", 0.0)

        sms = (
            f"IMD GKMS {pname}: Rain {rain:.1f}mm, Tmax {w.get('tmax_c', 30):.0f}C. "
            f"Spray: {spray}. Irrig: {irrig}. "
            f"Call Kisan Call Centre 1800-180-1551 for queries."
        )
        return sms[:160]

    @staticmethod
    def format_voice_script(advisory: Dict[str, Any]) -> str:
        pname = advisory.get("panchayat_name", "your gram panchayat")
        cname = advisory.get("crop", {}).get("name", "your crop")
        w = advisory.get("weather_summary", {})
        spray = advisory.get("spray_advisory", {})
        irrig = advisory.get("irrigation_advisory", {})

        script = (
            f"Attention farmers of {pname}. "
            f"Here is today's localized weather advisory for {cname}. "
            f"Downscaled forecast predicts {w.get('rainfall_mm', 0):.1f} millimeters of rain, "
            f"and a maximum temperature of {w.get('tmax_c', 30):.1f} degrees Celsius. "
            f"Regarding chemical spraying: {spray.get('summary', '')} "
            f"Regarding irrigation: {irrig.get('guidance', '')} "
            f"Please protect harvested crops and stay updated."
        )
        return script
