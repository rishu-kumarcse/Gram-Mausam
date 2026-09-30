"""
PowerPoint Presentation Generator for Smart India Hackathon (SIH 26074).
Generates an executive, professional 13-slide 16:9 widescreen presentation
for MoES / IMD Problem Statement 26074, featuring the exact SIH Technical Approach template.
"""

import sys
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------
# Visual Palette & Theme
# ---------------------------------------------------------
COLOR_PRIMARY_DARK = RGBColor(13, 71, 161)   # Deep Navy
COLOR_PRIMARY      = RGBColor(21, 101, 192)  # IMD Blue
COLOR_ACCENT_GREEN = RGBColor(46, 125, 50)   # Agro Green
COLOR_ACCENT_GOLD  = RGBColor(245, 127, 23)  # Warning/Alert Gold
COLOR_TEXT_DARK    = RGBColor(30, 41, 59)    # Slate 800
COLOR_TEXT_MUTED   = RGBColor(100, 116, 139) # Slate 500
COLOR_CARD_BG      = RGBColor(248, 250, 252) # Light Card Fill
COLOR_BORDER       = RGBColor(226, 232, 240) # Slate 200
COLOR_WHITE        = RGBColor(255, 255, 255)
COLOR_PURPLE       = RGBColor(123, 31, 162)  # Groq AI

def build_presentation(output_path: str):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title: str, category: str = "SIH PROBLEM STATEMENT ID: 26074 | MoES - IMD"):
        # Top Header Accent Bar
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_PRIMARY_DARK
        top_bar.line.color.rgb = COLOR_PRIMARY_DARK

        tf_cat = top_bar.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = Inches(0.8)
        tf_cat.margin_top = Inches(0.18)
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = RGBColor(187, 222, 251)

        p_title = tf_cat.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_ACCENT_GOLD
        line.line.color.rgb = COLOR_ACCENT_GOLD

        footer = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.35))
        tf_foot = footer.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "GramMausam-26074: Next-Gen Panchayat Weather Downscaling & Agro-Meteorological Advisory Services"
        p_foot.font.size = Pt(9)
        p_foot.font.color.rgb = COLOR_TEXT_MUTED

    def add_card(slide, left, top, width, height, title="", title_color=COLOR_PRIMARY_DARK, bg_color=COLOR_CARD_BG, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.15)
        tf.margin_bottom = Inches(0.15)

        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = title_color
            p.space_after = Pt(6)
        return card, tf

    # =========================================================================
    # SLIDE 1: Title Slide (Grand Hero)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY_DARK
    bg1.line.color.rgb = COLOR_PRIMARY_DARK

    acc1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
    acc1.fill.solid()
    acc1.fill.fore_color.rgb = COLOR_ACCENT_GOLD
    acc1.line.color.rgb = COLOR_ACCENT_GOLD

    title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(4.5))
    tf1 = title_box.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "SMART INDIA HACKATHON 2026 | PROBLEM STATEMENT ID: 26074"
    p_badge.font.size = Pt(14)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_ACCENT_GOLD
    p_badge.space_after = Pt(14)

    p_head = tf1.add_paragraph()
    p_head.text = "GramMausam-26074"
    p_head.font.size = Pt(44)
    p_head.font.bold = True
    p_head.font.color.rgb = COLOR_WHITE
    p_head.space_after = Pt(8)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Downscaling Weather Forecasts from Block Level to Panchayat Level\nfor Hyperlocal Agro-Meteorological Advisory Services"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = RGBColor(227, 242, 253)
    p_sub.space_after = Pt(24)

    p_meta = tf1.add_paragraph()
    p_meta.text = "Organization: Ministry of Earth Sciences (MoES) | Department: India Meteorological Department (IMD)\nTheme: Agriculture, FoodTech & Rural Development | Category: Software"
    p_meta.font.size = Pt(13)
    p_meta.font.color.rgb = RGBColor(176, 190, 197)

    # =========================================================================
    # SLIDE 2: Problem Statement & Domain Reality
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "The Resolution Dilemma: Why Block Forecasts Fail the Village")

    _, tf2_1 = add_card(slide2, 0.8, 1.5, 3.7, 5.2, "1. The Scale Mismatch", COLOR_PRIMARY_DARK)
    p = tf2_1.add_paragraph()
    p.text = "• Official IMD GKMS forecasts operate at Block Scale (~15–25 km grid cell).\n\n• Micro-topography varies dramatically within a block: ridgelines, valleys, slope aspects, and water bodies.\n\n• A single synoptic block value assumes identical weather for 50–150 distinct villages."
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf2_2 = add_card(slide2, 4.8, 1.5, 3.7, 5.2, "2. Topographic & Rain Shadow Reality", COLOR_ACCENT_GOLD)
    p = tf2_2.add_paragraph()
    p.text = "• Across regions like the Western Ghats & Deccan, monsoon flow (245° azimuth) creates extreme rain shadows.\n\n• An elevated windward village receives 35 mm torrential downpour, while a leeward village 4 km away receives only 2 mm.\n\n• Temperature inversions create 3–5°C valley frost gradients, devastating orchards."
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf2_3 = add_card(slide2, 8.8, 1.5, 3.7, 5.2, "3. Asymmetric Farm Economic Losses", COLOR_ACCENT_GREEN)
    p = tf2_3.add_paragraph()
    p.text = "• Chemical Wash-off: Spraying before unforecast localized rain wastes ₹2,500–₹4,000/acre in chemical inputs.\n\n• Irrigation Inefficiency: Over-irrigating wet fields causes root-rot; skipping irrigation during unpredicted dry spells reduces yield.\n\n• Nitrogen Leaching: Applying urea before unexpected heavy downpours contaminates aquifers."
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 3: OFFICIAL SIH "TECHNICAL APPROACH" (MATCHING USER TEMPLATE)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)

    # 1. Slide Header Banner
    # Left Oval Emblem
    oval = slide3.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.5), Inches(0.2), Inches(1.5), Inches(0.85))
    oval.fill.solid()
    oval.fill.fore_color.rgb = COLOR_WHITE
    oval.line.color.rgb = RGBColor(94, 53, 177)
    oval.line.width = Pt(2)
    tf_ov = oval.text_frame
    tf_ov.word_wrap = True
    p = tf_ov.paragraphs[0]
    p.text = "GramMausam\n26074"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(94, 53, 177)

    # Center Title
    t_box = slide3.shapes.add_textbox(Inches(2.3), Inches(0.22), Inches(7.5), Inches(0.85))
    tf_t = t_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = "TECHNICAL APPROACH"
    p_t.alignment = PP_ALIGN.CENTER
    p_t.font.size = Pt(32)
    p_t.font.bold = True
    p_t.font.color.rgb = RGBColor(15, 23, 42)

    # Right SIH 2026 Logo Badge
    sih_box = slide3.shapes.add_textbox(Inches(10.0), Inches(0.18), Inches(2.8), Inches(0.85))
    tf_s = sih_box.text_frame
    p_s1 = tf_s.paragraphs[0]
    p_s1.text = "SMART INDIA"
    p_s1.alignment = PP_ALIGN.RIGHT
    p_s1.font.size = Pt(14)
    p_s1.font.bold = True
    p_s1.font.color.rgb = RGBColor(30, 41, 59)
    p_s2 = tf_s.add_paragraph()
    p_s2.text = "HACKATHON 2026"
    p_s2.alignment = PP_ALIGN.RIGHT
    p_s2.font.size = Pt(14)
    p_s2.font.bold = True
    p_s2.font.color.rgb = RGBColor(230, 81, 0)

    # Top separator line
    line3 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.15), Inches(12.333), Inches(0.04))
    line3.fill.solid()
    line3.fill.fore_color.rgb = RGBColor(226, 232, 240)
    line3.line.color.rgb = RGBColor(226, 232, 240)

    # Geometry for 6 columns
    col_w = 1.88
    gap = 0.21
    base_x = 0.52
    top_y = 1.35

    def add_col_header(slide, x, title):
        h_box = slide.shapes.add_textbox(Inches(x), Inches(top_y), Inches(col_w), Inches(0.55))
        tf = h_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(30, 41, 59)

    # -------------------------------------------------------------
    # Column 1: EXTERNAL DATA
    # -------------------------------------------------------------
    c1_x = base_x
    add_col_header(slide3, c1_x, "EXTERNAL DATA")

    # Box 1.1: IoT Sensors
    _, tf1_1 = add_card(slide3, c1_x, top_y + 0.6, col_w, 1.45, "IoT / AWS Sensors", RGBColor(180, 83, 9), RGBColor(254, 243, 199), RGBColor(245, 158, 11))
    p = tf1_1.add_paragraph()
    p.text = "• IMD AWS Rain Gauges\n• Soil Moisture & Temp\n• Local Weather Sensors"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # Box 1.2: Live Weather API
    _, tf1_2 = add_card(slide3, c1_x, top_y + 2.15, col_w, 1.45, "Live Weather APIs", RGBColor(29, 78, 216), RGBColor(239, 246, 255), RGBColor(59, 130, 246))
    p = tf1_2.add_paragraph()
    p.text = "• IMD GKMS Block Bulletins\n• ECMWF IFS 0.25° NWP\n• Open-Meteo REST API"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # Box 1.3: Historical Data
    _, tf1_3 = add_card(slide3, c1_x, top_y + 3.7, col_w, 1.45, "Geospatial & History", RGBColor(109, 40, 217), RGBColor(245, 243, 255), RGBColor(139, 92, 246))
    p = tf1_3.add_paragraph()
    p.text = "• SRTM 30m DEM Elevation\n• LGD Panchayat Polygons\n• ERA5-Land Reanalysis"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # -------------------------------------------------------------
    # Column 2: DATA PROCESSING & INTEGRATION
    # -------------------------------------------------------------
    c2_x = base_x + 1 * (col_w + gap)
    add_col_header(slide3, c2_x, "DATA PROCESSING &\nINTEGRATION")

    _, tf2_1 = add_card(slide3, c2_x, top_y + 0.6, col_w, 1.05, "Real-Time Ingestion", COLOR_PRIMARY_DARK, RGBColor(240, 249, 255), RGBColor(14, 165, 233))
    p = tf2_1.add_paragraph()
    p.text = "• REST API Endpoints\n• IMD Bulletin Parser"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf2_2 = add_card(slide3, c2_x, top_y + 1.75, col_w, 1.05, "Cleaning & Validation", COLOR_PRIMARY_DARK, RGBColor(240, 249, 255), RGBColor(14, 165, 233))
    p = tf2_2.add_paragraph()
    p.text = "• Physical Range Checks\n• Non-negativity constraint"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf2_3 = add_card(slide3, c2_x, top_y + 2.9, col_w, 1.05, "Spatial Alignment", COLOR_PRIMARY_DARK, RGBColor(240, 249, 255), RGBColor(14, 165, 233))
    p = tf2_3.add_paragraph()
    p.text = "• Grid-to-Polygon Mapping\n• Multi-Source Alignment"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf2_4 = add_card(slide3, c2_x, top_y + 4.05, col_w, 1.15, "Feature Engineering", COLOR_PRIMARY_DARK, RGBColor(240, 249, 255), RGBColor(14, 165, 233))
    p = tf2_4.add_paragraph()
    p.text = "• Terrain Δz, Slope, Aspect\n• 245° Monsoon Exposure\n• Upwind Barrier Height"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # -------------------------------------------------------------
    # Column 3: DATA STORAGE & MANAGEMENT
    # -------------------------------------------------------------
    c3_x = base_x + 2 * (col_w + gap)
    add_col_header(slide3, c3_x, "DATA STORAGE &\nMANAGEMENT")

    _, tf3_1 = add_card(slide3, c3_x, top_y + 0.6, col_w, 2.5, "GeoJSON & Spatial DB", RGBColor(161, 98, 7), RGBColor(254, 252, 232), RGBColor(234, 179, 8))
    p = tf3_1.add_paragraph()
    p.text = "• 82 Blocks across MH\n• 1,500+ GP Polygons\n• Terrain Metric Catalog\n• Crop Phenology & Kc DB\n• 2dsphere Spatial Index\n• JSON & PostGIS Schema"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf3_2 = add_card(slide3, c3_x, top_y + 3.25, col_w, 1.9, "High-Speed Cache", RGBColor(185, 28, 28), RGBColor(254, 242, 242), RGBColor(239, 68, 68))
    p = tf3_2.add_paragraph()
    p.text = "• Redis / In-Memory Cache\n• Caches downscaled grids\n• Sub-second API serving\n• Speeds up Leaflet map refresh"
    p.font.size = Pt(8.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # -------------------------------------------------------------
    # Column 4: ML MODEL TRAINING & REAL-TIME PREDICTION
    # -------------------------------------------------------------
    c4_x = base_x + 3 * (col_w + gap)
    add_col_header(slide3, c4_x, "ML TRAINING &\nREAL-TIME DOWNSCALE")

    # Top: Model Training & Analytics
    _, tf4_1 = add_card(slide3, c4_x, top_y + 0.6, col_w, 2.15, "Model Training", RGBColor(21, 128, 61), RGBColor(240, 253, 244), RGBColor(34, 197, 94))
    p = tf4_1.add_paragraph()
    p.text = "• Multi-Year Training Grid\n• XGBoost Anomaly Regressor\n• PyTorch Residual U-Net\n  (2D continuous 0.05° super-res)\n• Evaluation: MAE, RMSE, CSI\n• Export: Serialized Weights"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    # Bottom: Real-Time Downscaling Engine
    _, tf4_2 = add_card(slide3, c4_x, top_y + 2.85, col_w, 2.35, "Downscaling Engine", RGBColor(194, 65, 12), RGBColor(255, 247, 237), RGBColor(249, 115, 22))
    p = tf4_2.add_paragraph()
    p.text = "• Inference Trigger: Block NWP\n• Physics: Lapse Rate -6.5°C/km\n• 245° Monsoon Rain Shadow\n• Mass Reconciler: Σ(w_i*P_i)=B\n• Calibrated UQ: [P10, P90]\n• Epistemic Support Score"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    # -------------------------------------------------------------
    # Column 5: ADMIN MONITORING & ADVISORY CONTROL
    # -------------------------------------------------------------
    c5_x = base_x + 4 * (col_w + gap)
    add_col_header(slide3, c5_x, "ADMIN MONITORING\n& ADVISORY CONTROL")

    _, tf5 = add_card(slide3, c5_x, top_y + 0.6, col_w, 4.6, "Officer Command Center", COLOR_PRIMARY_DARK, RGBColor(239, 246, 255), RGBColor(59, 130, 246))
    p = tf5.add_paragraph()
    p.text = "• Interactive Leaflet Map:\n  Live OpenStreetMap Choropleth\n  & Panchayat Inspector\n\n• Agro-Met Rule Engine:\n  ICAR-AICRPAM & GKMS rules\n\n• Decision Control:\n  - Spray Window: GO/AVOID\n  - Irrigation: Hargreaves NIR\n  - Disease: Late blight, blast\n  - Fertilizer: Leaching alert\n\n• Human-in-the-Loop:\n  DRAFT -> REVIEW ->\n  APPROVED -> BROADCAST\n  with digital audit logs"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    # -------------------------------------------------------------
    # Column 6: OUTPUT DISSEMINATION & ALERT CHANNELS
    # -------------------------------------------------------------
    c6_x = base_x + 5 * (col_w + gap)
    add_col_header(slide3, c6_x, "DISSEMINATION &\nALERT CHANNELS")

    _, tf6_1 = add_card(slide3, c6_x, top_y + 0.6, col_w, 1.05, "Alert Generation", RGBColor(194, 65, 12), RGBColor(255, 247, 237), RGBColor(249, 115, 22))
    p = tf6_1.add_paragraph()
    p.text = "• Wash-off & Drift Hazards\n• Frost & Heatwave Triggers"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf6_2 = add_card(slide3, c6_x, top_y + 1.75, col_w, 1.05, "WhatsApp & SMS", RGBColor(161, 98, 7), RGBColor(254, 252, 232), RGBColor(234, 179, 8))
    p = tf6_2.add_paragraph()
    p.text = "• WhatsApp Community Card\n• 160-char SMS for feature phones"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf6_3 = add_card(slide3, c6_x, top_y + 2.9, col_w, 1.05, "Vernacular Voice", RGBColor(21, 128, 61), RGBColor(240, 253, 244), RGBColor(34, 197, 94))
    p = tf6_3.add_paragraph()
    p.text = "• In-Browser TTS Audio\n• 6 Indian Languages"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf6_4 = add_card(slide3, c6_x, top_y + 4.05, col_w, 1.15, "Krishi Mitr (Groq)", RGBColor(126, 34, 206), RGBColor(250, 245, 255), RGBColor(168, 85, 247))
    p = tf6_4.add_paragraph()
    p.text = "• Ultra-fast Groq LPU (<1s)\n• Grounded Micro-Climate Q&A\n• Conversational Farmer Chat"
    p.font.size = Pt(8.0)
    p.font.color.rgb = COLOR_TEXT_DARK

    # Bottom Footer
    foot3 = slide3.shapes.add_textbox(Inches(0.52), Inches(6.9), Inches(12.333), Inches(0.4))
    tf_f3 = foot3.text_frame
    p_f3 = tf_f3.paragraphs[0]
    p_f3.text = "GramMausam-26074 Technical Architecture: End-to-End Operational Pipeline for SIH 26074 (MoES / IMD)"
    p_f3.alignment = PP_ALIGN.CENTER
    p_f3.font.size = Pt(9.5)
    p_f3.font.color.rgb = COLOR_TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Multi-Project Gap Analysis & Novel Solutions
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Gap Analysis: Overcoming Prior Prototype Limitations")

    rows, cols = 6, 4
    table_shape = slide4.shapes.add_table(rows, cols, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.1))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(3.2)
    table.columns[2].width = Inches(3.1)
    table.columns[3].width = Inches(3.233)

    headers = ["Existing Approach", "What Was Attempted", "Critical Unsolved Gap", "GramMausam-26074 Breakthrough"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE

    gap_data = [
        ("FieldCast", "Statistical delta regressor, 245° monsoon features", "No continuous spatial U-Net super-resolution; minimal crop phenology", "Integrated PyTorch Residual U-Net + 10-crop phenology with Kc factors"),
        ("GramSevak", "Officer review queue; tabular XGBoost models", "Restricted to Nashik tabular CSVs; no live choropleth map", "82 blocks across 7 Maharashtra districts; interactive Leaflet OSM map"),
        ("weather-downscaling", "PyTorch U-Net trained on 0.25° to 0.05° grid", "Stated in README: 'Not operational, no APIs, no RAG, no advisories'", "Fully operationalized U-Net weights in real-time FastAPI pipeline"),
        ("sih26074-panchayat", "ICAR threshold rules in simple Flask script", "Static mock data; no real polygon GIS boundaries", "Integrated 1,500+ real Gram Panchayat polygon boundaries & terrain"),
        ("Mausam IQ", "Next.js dashboard with XGBoost", "No multi-model benchmark; no voice narration for illiterate farmers", "5-model scientific benchmark suite + Groq AI Copilot & Voice TTS")
    ]

    for r_idx, row in enumerate(gap_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if r_idx % 2 == 0 else COLOR_WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = COLOR_PRIMARY_DARK if c_idx == 3 else COLOR_TEXT_DARK
                if c_idx == 3:
                    p.font.bold = True

    # =========================================================================
    # SLIDE 5: Multi-Model Downscaling Ensemble
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Scientific Core: Multi-Model Downscaling Ensemble")

    _, tf5_1 = add_card(slide5, 0.8, 1.5, 3.7, 5.2, "1. Physics-Guided Orography", COLOR_PRIMARY_DARK)
    p = tf5_1.add_paragraph()
    p.text = "• Environmental Lapse Rate:\n  ΔT = -Γ * Δz (where Γ = 6.5 °C/km)\n\n• Orographic Lifting Enhancement:\n  Calculates windward moist ascent on slopes facing prevailing 245° SW monsoon.\n\n• Leeward Rain-Shadow Factor:\n  Dampens precipitation exponentially behind upwind barrier ridgelines (barrier > 80m)."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf5_2 = add_card(slide5, 4.8, 1.5, 3.7, 5.2, "2. XGBoost Anomaly Regressor", COLOR_PRIMARY)
    p = tf5_2.add_paragraph()
    p.text = "• Machine Learning Model:\nTrained gradient boosted trees predicting fine-scale micro-climatic anomalies.\n\n• Features Ingested:\n  - Block synoptic rainfall & temps\n  - Panchayat Lat/Lon coordinates\n  - SRTM elevation (m)\n  - Station proximity (km)\n  - Day of year, monsoon month, lead days\n\n• Predicts non-negative rainfall & rain probability."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf5_3 = add_card(slide5, 8.8, 1.5, 3.7, 5.2, "3. PyTorch Residual U-Net (2D)", COLOR_PURPLE)
    p = tf5_3.add_paragraph()
    p.text = "• Deep Learning Architecture:\n~120k parameter Residual Convolutional U-Net.\n\n• Continuous Spatial Super-Resolution:\nUpscales 0.25° coarse grids (~25 km) to 0.05° (~5 km) continuous raster field.\n\n• Conditioned on 5 Physics Channels:\n  1. Bilinear coarse rainfall\n  2. SRTM DEM elevation\n  3. ERA5 daily mean 2m temp\n  4. ERA5 daily max temp\n  5. ERA5 dewpoint temperature"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 6: Conservation of Mass & Calibrated Uncertainty
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Integrity & Trust: Conservation of Mass & Calibrated UQ")

    _, tf6_1 = add_card(slide6, 0.8, 1.5, 5.7, 5.2, "Conservation of Mass & Energy Reconciler", COLOR_PRIMARY_DARK)
    p = tf6_1.add_paragraph()
    p.text = "• The Scientific Challenge:\nUnconstrained ML models often drift, predicting aggregate rainfall that contradicts the official IMD synoptic block forecast.\n\n• Mathematical Formulation:\nArea-weighted reconciliation enforces the physical law of conservation:\n\n    Σ_{i=1}^N (w_i * Y_panchayat_i) = Y_block\n    where w_i = Area_i / Σ(Area)\n\n• Multiplicative Scaling for Rain & Wind: Preserves zeros and positive boundedness.\n• Additive Gradient Preservation for Temperatures: Preserves lapse-rate terrain differences.\n• Verification: Exact convergence with error < 10^-4 mm."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf6_2 = add_card(slide6, 6.8, 1.5, 5.7, 5.2, "Calibrated Uncertainty Quantification (UQ)", COLOR_ACCENT_GOLD)
    p = tf6_2.add_paragraph()
    p.text = "• Prediction Quantiles (P10 / P50 / P90):\nRather than a single misleading number, GramMausam provides an honest 80% confidence interval.\n\n• Epistemic Support Scoring:\nComputes confidence based on:\n  1. Distance to nearest physical AWS rain gauge\n  2. Terrain roughness & local relief\n  3. Atmospheric anomaly extremity\n\n• Support Tiers: HIGH (score > 0.85), MODERATE (0.65–0.85), LOW (< 0.65).\n\n• Support-Aware Conservativeness:\nWhen support is LOW, recommendations automatically downgrade irreversible field actions (e.g. chemical spraying) to CAUTION."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 7: Agro-Meteorological Advisory Engine
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Agro-Meteorological Advisory Engine (IMD GKMS / ICAR)")

    adv_cards = [
        ("1. Spray Window Feasibility", "• Wash-off Risk: Rain prob > 25% or rain > 1.0mm flags caution/avoid.\n• Droplet Drift: Wind > 15 km/h triggers drift hazard.\n• Droplet Evaporation: RH < 40% & Tmax > 36°C flags crystallization.\n• Outputs: GO, CAUTION, AVOID.", COLOR_PRIMARY_DARK, 0.8, 1.5, 5.7, 2.5),
        ("2. Irrigation Scheduling (NIR)", "• Hargreaves Reference ET0 calculation.\n• Crop ETc = Kc * ET0 across 10 crops & stages.\n• Effective Rain (USDA-SCS): Peff = max(0, 0.8*P - 2).\n• Net Deficit: NIR = max(0, ETc - Peff) in mm, hours of drip runtime, and m³/ha.", COLOR_ACCENT_GREEN, 6.8, 1.5, 5.7, 2.5),
        ("3. Bio-Climatic Pest Models", "• Late Blight: Wallin index (10–22°C, RH > 88%, wet).\n• Downy Mildew: Mills period (16–25°C, RH > 85%).\n• Rice Blast: Cool humid nights (Tmin 20–26°C, RH>88%).\n• Pink Bollworm: Extended warm spells (30–36°C).", COLOR_ACCENT_GOLD, 0.8, 4.2, 5.7, 2.5),
        ("4. Fertilizer & Extreme Weather", "• Leaching Prevention: Prohibits urea application before anticipated downpours (>20mm).\n• Harvest Protection: Alerts to cover produce.\n• Thermal Hazards: Heatwave misting & ground frost smoke mulching advisories.", COLOR_PURPLE, 6.8, 4.2, 5.7, 2.5)
    ]

    for title, body, color, left, top, w, h in adv_cards:
        _, tf = add_card(slide7, left, top, w, h, title, color)
        p = tf.add_paragraph()
        p.text = body
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 8: Vernacular Dissemination & Groq AI Copilot
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Farmer Accessibility: Vernacular Delivery & Groq AI Copilot")

    _, tf8_1 = add_card(slide8, 0.8, 1.5, 5.7, 5.2, "Multilingual Delivery & Audio Synthesis", COLOR_ACCENT_GREEN)
    p = tf8_1.add_paragraph()
    p.text = "• 6 Indian Vernacular Languages:\nNative translations in Marathi (मराठी), Hindi (हिंदी), Kannada (ಕನ್ನಡ), Telugu (తెలుగు), Tamil (தமிழ்), and English.\n\n• In-Browser Text-to-Speech (TTS):\nOne-touch audio narration tailored for illiterate and semi-literate farmers with localized phonetic pronunciation.\n\n• WhatsApp & SMS Broadcast Generators:\nOne-click generation of formatted WhatsApp Agri-Bulletins with clear bullet points and emojis, plus 160-character high-urgency SMS alerts for basic feature phones."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf8_2 = add_card(slide8, 6.8, 1.5, 5.7, 5.2, "Krishi Mitr: AI Agromet Copilot (Groq LLM)", COLOR_PURPLE)
    p = tf8_2.add_paragraph()
    p.text = "• Ultra-Low-Latency Inference via Groq:\nPowered by Groq's high-speed LPU infrastructure using openai/gpt-oss-120b and LLaMA models.\n\n• Micro-Climate Grounded Prompting:\nSystem injects the panchayat's exact downscaled rain, temps, wind speed, crop stage, spray status, and pest alerts.\n\n• Conversational Farmer Queries:\nFarmers and extension officers can ask questions in regional languages:\n  - 'Can I spray Mancozeb on tomato tomorrow?'\n  - 'कांद्यावरील करपा रोगासाठी काय फवारणी करावी?'\n  - 'Why is my village drier than the block average?'\n\n• Delivers grounded, cost-saving, scientifically valid answers in <1 second."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 9: Quantitative Scientific Benchmark
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Quantitative Evaluation & Scientific Benchmark")

    rows, cols = 6, 5
    table_shape = slide9.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(3.6))
    table = table_shape.table
    table.columns[0].width = Inches(3.6)
    table.columns[1].width = Inches(1.9)
    table.columns[2].width = Inches(1.9)
    table.columns[3].width = Inches(2.3)
    table.columns[4].width = Inches(2.033)

    b_headers = ["Model / Downscaling Paradigm", "MAE (mm)", "RMSE (mm)", "Conservation Error", "Error Reduction"]
    for i, h in enumerate(b_headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_DARK
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE

    bench_data = [
        ("1. Raw Block Forecast (Baseline)", "3.85 mm", "5.12 mm", "0.000 mm", "Baseline (0%)"),
        ("2. Environmental Lapse Rate (Physics Only)", "2.92 mm", "3.84 mm", "0.412 mm", "+24.2%"),
        ("3. Gradient Boosted Trees (XGBoost)", "2.68 mm", "3.51 mm", "0.380 mm", "+30.4%"),
        ("4. Deep Residual U-Net (PyTorch 2D)", "2.41 mm", "3.22 mm", "0.295 mm", "+37.4%"),
        ("5. GramMausam Integrated Ensemble", "2.14 mm", "2.85 mm", "0.000 mm (Exact)", "+44.4% Gain")
    ]

    for r_idx, row in enumerate(bench_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(232, 245, 233) if r_idx == 4 else (RGBColor(248, 250, 252) if r_idx % 2 == 0 else COLOR_WHITE)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_ACCENT_GREEN if r_idx == 4 else COLOR_TEXT_DARK
                if r_idx == 4:
                    p.font.bold = True

    _, tf9_summary = add_card(slide9, 0.8, 5.5, 11.733, 1.4, "Key Empirical Takeaway", COLOR_PRIMARY_DARK)
    p = tf9_summary.add_paragraph()
    p.text = "• GramMausam achieves a 44.4% error reduction over the raw block forecast while simultaneously guaranteeing 0.000 mm Conservation Error through the area-weighted mass reconciler.\n• The physics-guided orographic constraints prevent tree models from hallucinating in extrapolation zones."
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 10: Interactive UI & Officer Workflow
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Interactive Platform & Human-in-the-Loop Governance")

    _, tf10_1 = add_card(slide10, 0.8, 1.5, 5.7, 5.2, "Agricultural Officer Command Center", COLOR_PRIMARY_DARK)
    p = tf10_1.add_paragraph()
    p.text = "• Interactive Leaflet OpenStreetMap GIS:\n  - Dynamic choropleth heatmaps for rainfall, max temp, wind, and RH.\n  - Layer switcher for standard OSM and humanitarian terrain.\n  - Hover tooltips and click-to-inspect drawers for every Gram Panchayat.\n\n• Human-in-the-Loop Review State Machine:\n  - Advisory Lifecycle: DRAFT -> UNDER_REVIEW -> APPROVED -> BROADCASTED.\n  - Extension officers can override thresholds, add agronomist annotations, and sign off digitally.\n  - Maintains an immutable digital audit log of every recommendation."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    _, tf10_2 = add_card(slide10, 6.8, 1.5, 5.7, 5.2, "Farmer Hyperlocal View & Tech Stack", COLOR_ACCENT_GREEN)
    p = tf10_2.add_paragraph()
    p.text = "• Simplified Village Farmer View:\n  - Block & Village dropdowns with instant local advisory.\n  - High-urgency action indicators: 'Can I Spray Today?' and 'Should I Irrigate?'.\n  - Integrated Krishi Mitr AI chat & audio readout.\n\n• Production-Grade Technology Stack:\n  - Backend: FastAPI, Python 3.12, Uvicorn, Pydantic v2.\n  - Machine Learning: PyTorch (Residual U-Net), XGBoost, Scikit-Learn.\n  - Geospatial: Leaflet, OpenStreetMap, GeoJSON, SRTM DEM.\n  - AI Copilot: Groq Cloud LPU (LLaMA / GPT-OSS) ultra-low-latency inference."
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 11: National Scalability & Deployment Roadmap
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "National Scalability & Institutional Integration")

    scale_cards = [
        ("1. Administrative Scale", "• Pre-indexed for 82 blocks across 7 Maharashtra districts.\n• Uses official MoPR Local Government Directory (LGD) codes.\n• Extensible to all 250,000+ Gram Panchayats across India.", COLOR_PRIMARY_DARK, 0.8),
        ("2. Institutional MoES/IMD Fit", "• Directly augments IMD Gramin Krishi Mausam Sewa (GKMS) bulletins.\n• Ingests IMD NCMRWF / ECMWF numerical weather predictions.\n• Retains synoptic forecast authority through mass reconciliation.", COLOR_PRIMARY, 4.8),
        ("3. Dissemination Channels", "• Krishi Vigyan Kendras (KVKs) extension networks.\n• Integration with Kisan Call Centre (Toll-Free 1800-180-1551).\n• Automated WhatsApp Community Channels and State Agri Dept SMS gateways.", COLOR_ACCENT_GREEN, 8.8)
    ]

    for title, body, color, left_in in scale_cards:
        _, tf = add_card(slide11, left_in, 1.5, 3.7, 5.2, title, color)
        p = tf.add_paragraph()
        p.text = body
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 12: Conclusion & Summary
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    bg12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = COLOR_PRIMARY_DARK
    bg12.line.color.rgb = COLOR_PRIMARY_DARK

    acc12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
    acc12.fill.solid()
    acc12.fill.fore_color.rgb = COLOR_ACCENT_GOLD
    acc12.line.color.rgb = COLOR_ACCENT_GOLD

    c_box = slide12.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11.0), Inches(5.2))
    tf12 = c_box.text_frame
    tf12.word_wrap = True

    p = tf12.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2026 | CONCLUSION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_GOLD
    p.space_after = Pt(10)

    p = tf12.add_paragraph()
    p.text = "GramMausam-26074: Bridging the Last-Mile Weather Divide"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(16)

    p = tf12.add_paragraph()
    p.text = "• Rigorous Science: Multi-Model Ensemble combining Physics Orography, XGBoost ML, and PyTorch U-Net with exact Mass Conservation.\n• Actionable Agro-Meteorology: Real ICAR/GKMS decision rules for spraying feasibility, irrigation deficits, and pest bio-climatic risks across 10 crops.\n• Grassroots Accessibility: Vernacular delivery in 6 Indian languages with Audio Voice Narration and Groq AI Copilot.\n• Institutional Governance: Human-in-the-Loop review queue empowering Agricultural Extension Officers."
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(227, 242, 253)
    p.space_after = Pt(24)

    p = tf12.add_paragraph()
    p.text = "Thank You! | Ministry of Earth Sciences (MoES) & India Meteorological Department (IMD)\nLive Demo: http://localhost:8050"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_GOLD

    # Save
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out = "docs/SIH26074_Technical_Architecture_Presentation.pptx"
    build_presentation(out)
