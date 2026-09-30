"""
Multilingual Agronomic Localization Engine.

Translates agromet advisories, warnings, and weather summaries into:
- Hindi (हिंदी)
- Marathi (मराठी)
- Kannada (ಕನ್ನಡ)
- Telugu (తెలుగు)
- Tamil (தமிழ்)
- English (default)
"""

from typing import Dict, Any, List

LOCALIZED_DICTIONARY = {
    "hi": {
        "spray_go": "दवाई छिड़काव के लिए अनुकूल समय है। हवा की गति सामान्य है।",
        "spray_caution": "सावधानी से छिड़काव करें। हल्की हवा या बूंदाबांदी का जोखिम है।",
        "spray_avoid": "कीटनाशक छिड़काव तुरंत स्थगित करें! तेज हवा या बारिश से दवा बहने का खतरा है।",
        "irrig_skip": "सिंचाई स्थगित रखें। पर्याप्त वर्षा से खेत में नमी बनी हुई है। जल निकासी की व्यवस्था करें।",
        "irrig_postpone": "सिंचाई रोकें। बारिश की संभावना को देखते हुए अभी पानी न दें।",
        "irrig_apply": "हल्की से मध्यम सिंचाई करें। फसल की जल मांग अधिक है।",
        "fertilizer_delay": "यूरिया और रासायनिक खाद का बुरकाव रोकें। तेज बारिश से पोषक तत्व बह जाएंगे।",
        "harvest_protect": "कटी हुई फसल को तुरंत तिरपाल से ढकें या सुरक्षित गोदाम में पहुंचाएं।",
        "temp_heat": "अत्यधिक तापमान की चेतावनी। दोपहर में खेत कार्य से बचें और मल्चिंग करें।",
        "temp_frost": "पाला/शीत लहर की चेतावनी। रात्रि में हल्की सिंचाई करें।",
        "pest_warning": "कीट/रोग प्रकोप की चेतावनी:",
        "rainfall": "वर्षा",
        "temp_max": "अधिकतम तापमान",
        "temp_min": "न्यूनतम तापमान",
        "wind": "हवा की गति",
        "humidity": "आर्द्रता"
    },
    "mr": {
        "spray_go": "औषध फवारणीसाठी पोषक वातावरण आहे. वाऱ्याचा वेग मर्यादित आहे.",
        "spray_caution": "फवारणी करताना काळजी घ्या. मंद वारा किंवा पावसाची शक्यता आहे.",
        "spray_avoid": "औषध फवारणी तातडीने पुढे ढकला! पाऊस आणि वाऱ्यामुळे औषध वाहून जाण्याचा धोका आहे.",
        "irrig_skip": "पाणी देणे टाळा. पुरेसा पाऊस झाल्याने जमिनीत ओलावा आहे. शेतात पाणी साचू देऊ नका.",
        "irrig_postpone": "सिंचन पुढे ढकला. पावसाची शक्यता असल्याने पाणी देणे थांबवा.",
        "irrig_apply": "वेळापत्रकानुसार पिकाला पाणी द्या. पिकाची पाण्याची गरज जास्त आहे.",
        "fertilizer_delay": "युरिया व खतांचा डोस देणे पुढे ढकला. पावसामुळे खते वाहून जाण्याचा धोका आहे.",
        "harvest_protect": "काढणी केलेले धान्य तातडीने ताडपत्रीने झाका किंवा सुरक्षित शेडमध्ये ठेवा.",
        "temp_heat": "उष्णतेच्या लाटेचा इशारा. फळगळ रोखण्यासाठी सूक्ष्म सिंचनाचा वापर करा.",
        "temp_frost": "थंडीची लाट/धुक्याचा इशारा. पिकांचे संरक्षण करण्यासाठी संध्याकाळी हलके पाणी द्या.",
        "pest_warning": "कीड व रोग प्रादुर्भावाचा इशारा:",
        "rainfall": "पाऊस",
        "temp_max": "कमाल तापमान",
        "temp_min": "किमान तापमान",
        "wind": "वाऱ्याचा वेग",
        "humidity": "हवेतील आर्द्रता"
    },
    "kn": {
        "spray_go": "ಔಷಧಿ ಸಿಂಪಡಣೆಗೆ ಸೂಕ್ತ ಹವಾಮಾನವಿದೆ. ಗಾಳಿಯ ವೇಗ ಸಹಜವಾಗಿದೆ.",
        "spray_caution": "ಎಚ್ಚರಿಕೆಯಿಂದ ಸಿಂಪಡಿಸಿ. ಹಗುರ ಗಾಳಿ ಅಥವಾ ಮಳೆಯ ಸಾಧ್ಯತೆ ಇದೆ.",
        "spray_avoid": "ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆ ತಕ್ಷಣ ಮುಂದೂಡಿ! ಮಳೆಯಿಂದ ಔಷಧಿ ವ್ಯರ್ಥವಾಗುವ ಅಪಾಯವಿದೆ.",
        "irrig_skip": "ನೀರಾವರಿ ಮುಂದೂಡಿ. ಸಾಕಷ್ಟು ಮಳೆಯಿಂದಾಗಿ ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶವಿದೆ.",
        "irrig_postpone": "ಮಳೆ ನಿರೀಕ್ಷೆಯಿರುವುದರಿಂದ ನೀರು ಹಾಯಿಸುವುದನ್ನು ಮುಂದೂಡಿ.",
        "irrig_apply": "ಬೆಳೆಗೆ ಅಗತ್ಯವಿರುವಂತೆ ಲಘು ನೀರಾವರಿ ಒದಗಿಸಿ.",
        "fertilizer_delay": "ಯೂರಿಯಾ ಗೊಬ್ಬರ ಹಾಕುವುದನ್ನು ಮುಂದೂಡಿ. ಮಳೆಗೆ ರಸಗೊಬ್ಬರ ಕೊಚ್ಚಿಹೋಗುವ ಅಪಾಯವಿದೆ.",
        "harvest_protect": "ಕೊಯ್ಲು ಮಾಡಿದ ಬೆಳೆಗಳನ್ನು ಸುರಕ್ಷಿತ ಸ್ಥಳಕ್ಕೆ ಸ್ಥಳಾಂತರಿಸಿ ಅಥವಾ ಟಾರ್ಪಲಿನ್‌ನಿಂದ ಮುಚ್ಚಿ.",
        "pest_warning": "ಕೀಟ ಮತ್ತು ರೋಗದ ಮುನ್ನೆಚ್ಚರಿಕೆ:",
        "rainfall": "ಮಳೆ",
        "temp_max": "ಗರಿಷ್ಠ ತಾಪಮಾನ",
        "temp_min": "ಕನಿಷ್ಠ ತಾಪಮಾನ",
        "wind": "ಗಾಳಿಯ ವೇಗ",
        "humidity": "ತೇವಾಂಶ"
    },
    "te": {
        "spray_go": "మందుల పిచికారీకి అనుకూల వాతావరణం ఉంది.",
        "spray_caution": "జాగ్రత్తగా పిచికారీ చేయండి. గాలి తీవ్రతను గమనించండి.",
        "spray_avoid": "పిచికారీని వాయిదా వేయండి! వర్షం వలన మందు కొట్టుకుపోయే ప్రమాదం ఉంది.",
        "irrig_skip": "నీటిపారుదల నిలిపివేయండి. వర్షం వలన తగినంత తేమ ఉంది.",
        "irrig_postpone": "వర్ష సూచన ఉన్నందున నీరు పెట్టడం వాయిదా వేయండి.",
        "irrig_apply": "షెడ్యూల్ ప్రకారం పంటకు నీటితడులు అందించండి.",
        "fertilizer_delay": "ఎరువుల వినియోగాన్ని వాయిదా వేయండి. వర్షపు నీటితో ఎరువులు కొట్టుకుపోతాయి.",
        "harvest_protect": "కోత కోసిన ధాన్యాన్ని సురక్షిత ప్రాంతాలకు తరలించండి.",
        "pest_warning": "తెగుళ్లు మరియు పురుగుల హెచ్చరిక:",
        "rainfall": "వర్షపాతం",
        "temp_max": "గరిష్ట ఉష్ణోగ్రత",
        "temp_min": "కనిష్ట ఉష్ణోగ్రత",
        "wind": "గాలి వేగం",
        "humidity": "తేమ"
    },
    "ta": {
        "spray_go": "மருந்து தெளிப்பதற்கு உகந்த வானிலை நிலவுகிறது.",
        "spray_caution": "கவனமாக மருந்து தெளிக்கவும்.",
        "spray_avoid": "மருந்து தெளிப்பதை உடனே ஒத்திவைக்கவும்! மழை பெய்ய வாய்ப்புள்ளது.",
        "irrig_skip": "பாசனத்தை தவிர்க்கவும். மண்ணில் போதுமான ஈரப்பதம் உள்ளது.",
        "irrig_postpone": "மழை வாய்ப்பு உள்ளதால் நீர்ப்பாசனத்தை ஒத்திவைக்கவும்.",
        "irrig_apply": "பயிர்களுக்கு தேவையான நீர்ப்பாசனம் செய்யவும்.",
        "fertilizer_delay": "உரம் இடுவதை தள்ளிப்போடவும். மழையால் உரம் வீணாகும் அபாயம்.",
        "harvest_protect": "அறுவடை செய்த தானியங்களை தார்பாய் கொண்டு பாதுகாப்பாக மூடவும்.",
        "pest_warning": "பூச்சி மற்றும் நோய் எச்சரிக்கை:",
        "rainfall": "மழைப்பொழிவு",
        "temp_max": "அதிகபட்ச வெப்பநிலை",
        "temp_min": "குறைந்தபட்ச வெப்பநிலை",
        "wind": "காற்றின் வேகம்",
        "humidity": "ஈரப்பதம்"
    }
}

class VernacularTranslator:
    @staticmethod
    def get_supported_languages() -> List[Dict[str, str]]:
        return [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "hi", "name": "Hindi", "native": "हिंदी"},
            {"code": "mr", "name": "Marathi", "native": "मराठी"},
            {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"},
            {"code": "te", "name": "Telugu", "native": "తెలుగు"},
            {"code": "ta", "name": "Tamil", "native": "தமிழ்"}
        ]

    @classmethod
    def localize_advisory(cls, advisory_dict: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
        """
        Translates key advisory actions and weather summaries into target vernacular language.
        """
        lang = lang.lower()
        if lang not in LOCALIZED_DICTIONARY or lang == "en":
            # Return original English
            advisory_dict["language"] = "en"
            return advisory_dict

        dic = LOCALIZED_DICTIONARY[lang]
        res = dict(advisory_dict)
        res["language"] = lang

        # Translate Spray action
        spray_status = advisory_dict.get("spray_advisory", {}).get("status", "GO")
        if spray_status == "GO":
            res["spray_advisory"]["localized_summary"] = dic["spray_go"]
        elif spray_status == "CAUTION":
            res["spray_advisory"]["localized_summary"] = dic["spray_caution"]
        else:
            res["spray_advisory"]["localized_summary"] = dic["spray_avoid"]

        # Translate Irrigation action
        irrig_action = advisory_dict.get("irrigation_advisory", {}).get("action", "IRRIGATE")
        if irrig_action == "SKIP":
            res["irrigation_advisory"]["localized_guidance"] = dic["irrig_skip"]
        elif irrig_action == "POSTPONE":
            res["irrigation_advisory"]["localized_guidance"] = dic["irrig_postpone"]
        else:
            res["irrigation_advisory"]["localized_guidance"] = dic["irrig_apply"]

        # Localized voice broadcast script
        pname = advisory_dict.get("panchayat_name", "आपल्या गावासाठी")
        cname = advisory_dict.get("crop", {}).get("name", "पिकासाठी")
        w = advisory_dict.get("weather_summary", {})
        
        script = (
            f"{pname} ग्रामपंचायतीसाठी हवामान सल्ला. "
            f"अपेक्षित पाऊस {w.get('rainfall_mm', 0):.1f} मिमी, कमाल तापमान {w.get('tmax_c', 30):.1f} अंश सेल्सिअस. "
            f"{res['spray_advisory']['localized_summary']} "
            f"{res['irrigation_advisory']['localized_guidance']}"
        )
        res["voice_script"] = script
        return res
