# 🌾 GRAMMAUSAM — Panchayat-Level Weather Downscaling & Agro-Meteorological Advisory System

> **SIH Problem Statement 26074 | Smart India Hackathon**
> **Downscaling of weather forecast from Block level to Panchayat level**
> **Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)**
> **Agriculture, FoodTech & Rural Development**

[![SIH 2024](https://img.shields.io/badge/SIH-Problem%20Statement%2026074-blue?style=for-the-badge)](https://www.sih.gov.in/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API%20Backend-009688?style=for-the-badge)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Downscaling%20ML-1A7F37?style=for-the-badge)](https://xgboost.readthedocs.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Residual%20U-Net-EE4C2C?style=for-the-badge)](https://pytorch.org/)
[![GeoJSON](https://img.shields.io/badge/GeoJSON-Panchayat%20GIS-4F46E5?style=for-the-badge)](https://geojson.org/)

---

## 📋 Table of Contents

1. [Problem Statement (SIH PS 26074)](#-problem-statement-sih-ps-26074)
2. [Our Solution — GRAMMAUSAM](#-our-solution--grammausam)
3. [System Architecture](#-system-architecture)
4. [Dataset](#-dataset)
5. [Downscaling Methodology](#-downscaling-methodology)
6. [ML Model 1 — XGBoost](#-ml-model-1--xgboost)
7. [ML Model 2 — Residual U-Net](#-ml-model-2--residual-u-net)
8. [Advisory Engine](#-advisory-engine)
9. [Application Interface](#-application-interface)
10. [Project Structure](#-project-structure)
11. [Installation & Usage](#%EF%B8%8F-installation--usage)
12. [References](#-references)

---

## 🎯 Problem Statement (SIH PS 26074)

| Field | Details |
|---|---|
| **PS Number** | 26074 |
| **Title** | Downscaling of weather forecast from Block level to Panchayat level |
| **Organization** | Ministry of Earth Sciences (MoES) |
| **Department** | India Meteorological Department (IMD) |
| **Category** | Software |
| **Domain** | Agriculture, Climate Intelligence, Rural Development |

### Challenge Description

Official IMD forecasts are issued at the block scale, but agricultural decisions are made at the village or panchayat scale. Microclimatic differences caused by elevation, terrain, wind exposure, and local rainfall gradients create strong variation over short distances. A single block may contain multiple agro-climatic zones with different rainfall, temperature, humidity, and irrigation needs.

The core challenge is to convert block-level weather products into actionable Panchayat-scale insights that can support:

- hyperlocal rainfall and temperature estimation
- crop-stage and irrigation planning
- disease and pest risk monitoring
- timely, vernacular advisory delivery to farmers
- officer review and operational decision support

> The problem demands a solution that is physically grounded, operationally realistic, and useful in real agricultural contexts rather than a purely academic forecast exercise.

---

## 💡 Our Solution — GRAMMAUSAM

**GRAMMAUSAM** is an integrated climate-to-agri intelligence platform designed to bridge the gap between official IMD block forecasts and field-level advisory decisions. It combines:

| Layer | Technology | Role |
|---|---|---|
| **Downscaling Engine** | Physics + XGBoost + U-Net | Converts coarse block forecasts into Panchayat-level estimates |
| **Reconciliation Layer** | Conservation-of-mass correction | Preserves official forecast integrity while refining spatial detail |
| **Uncertainty Layer** | P10/P50/P90 confidence bounds | Keeps advisory decisions conservative when confidence is weak |
| **Advisory Engine** | GKMS-style agronomic rules | Suggests irrigation, spray timing, and crop actions |
| **Delivery Layer** | FastAPI + static web app | Exposes APIs and a full operational dashboard |
| **Farmer Interface** | Vernacular output + web access | Makes advice understandable and usable on the ground |

### Key Achievements vs. SIH 26074 Requirements

| Requirement | Our Implementation | Result |
|---|---|---|
| Block-to-Panchayat downscaling | Physics + ML + U-Net cascade | ✅ Spatial detail at local scale |
| Operational forecast integrity | Area-weighted reconciliation | ✅ Official totals preserved |
| Field-relevant agricultural advisory | Crop stage and weather-based logic | ✅ Actionable guidance for farmers |
| Multi-language delivery | Vernacular templates and voice-ready output | ✅ Easier farmer comprehension |
| Officer decision support | GeoJSON-based panchayat inspection | ✅ Human-in-the-loop review workflow |
| Real API exposure | FastAPI backend + static frontend | ✅ Web application and service integration |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GRAMMAUSAM SYSTEM                                │
├──────────────────┬──────────────────────┬───────────────────────────┤
│  DATA INGESTION  │   DOWNSCALING        │   ADVISORY & DELIVERY     │
│                  │                      │                           │
│ IMD Block        │  ┌──────────────┐    │  ┌─────────────────────┐  │
│ Forecast / Live  │  │ Physics      │    │  │ FastAPI Backend     │  │
│ NWP Data ───────►│  │ lapse rate   │────►│  │ + REST API          │  │
│                  │  │ & rain shadow│    │  └─────────────────────┘  │
│ GeoJSON Blocks  │  └──────┬───────┘    │                           │
│ + Panchayat     │         │            │  ┌─────────────────────┐  │
│ polygons        │  ┌──────▼───────┐    │  │ Advisory Engine     │  │
│                  │  │ XGBoost      │    │  │ - Irrigation        │  │
│                  │  │ Micro-       │────►│  │ - Spray window     │  │
│                  │  │ anomaly      │    │  │ - Disease/pest     │  │
│                  │  │ model        │    │  │ - Crop logic       │  │
│                  │  └──────┬───────┘    │  └─────────────────────┘  │
│                  │         │            │                           │
│                  │  ┌──────▼───────┐    │  ┌─────────────────────┐  │
│                  │  │ Residual     │────►│  │ Static Dashboard    │  │
│                  │  │ U-Net        │    │  │ + Leaflet map       │  │
│                  │  │ super-       │    │  │ + Officer review    │  │
│                  │  │ resolution   │    │  └─────────────────────┘  │
│                  │  └──────┬───────┘    │                           │
│                  │         │            │  ┌─────────────────────┐  │
│                  │  ┌──────▼───────┐    │  │ Vernacular Output   │  │
│                  │  │ Reconciler   │────►│  │ Hindi, Marathi,     │  │
│                  │  │ correction   │    │  │ Kannada, Telugu,   │  │
│                  │  └──────────────┘    │  │ Tamil, English      │  │
│                  │                      │  └─────────────────────┘  │
└──────────────────┴──────────────────────┴───────────────────────────┘
```

### Data Flow

```
Block Forecast ──► Terrain-Aware Feature Engineering ──► XGBoost / U-Net
                                    │
                                    ▼
                     Panchayat-Level Rainfall / Temperature / Humidity
                                    │
                                    ▼
           Reconciliation + Uncertainty Quantification + Crop Rules
                                    │
                             Farmer & Officer Advisory
```

---

## 📊 Dataset

**Primary spatial layers** are built from local GIS, weather, and agronomic datasets stored in the repository under the `data/` folder.

| Data Source | Contents | Role |
|---|---|---|
| `data/geo/blocks_mh.json` | Maharashtra block polygons | Block-level geographic context |
| `data/geo/block_index.json` | Block metadata | Lookup and indexing |
| `data/geo/panchayats_by_block/` | Panchayat polygons by block | Fine-scale spatial resolution |
| `data/crops/crop_database.json` | Crop calendars and crop-stage metadata | Agronomic advisory logic |
| `data/crops/pest_disease_models.json` | Pest and disease thresholds | Risk evaluation |
| `data/samples/imd_block_forecast_bulletin.json` | IMD bulletin sample | Realistic API and demo input |

### Spatial Coverage

- 82 blocks across Maharashtra
- GeoJSON polygon coverage for Panchayat-level districts and villages
- Multi-layer meteorological and topographic context for local climate differentiation

### Feature Categories

| Category | Variables |
|---|---|
| **Topography** | elevation, slope, terrain exposure, distance to gauges |
| **Meteorology** | rainfall, temperature, humidity, wind, dewpoint |
| **Monsoon context** | azimuth-based windward/leeward effects |
| **Hydroclimatic** | rain-shadow signals and localized anomaly features |
| **Agronomic** | crop stage, water requirement, pest risk thresholds |

---

## 🔧 Downscaling Methodology

The solution does not rely on a single black-box model. It applies a layered method that respects both the physical character of weather and the operational constraints of IMD forecast products.

### 1. Physics-Guided Baseline

The downscaling logic incorporates:

- environmental lapse rate for temperature adjustment with elevation
- monsoon azimuth orientation for windward/leeward rainfall enhancement and shadowing
- terrain-based rainfall redistribution over local topographic gradients

This acts as a strong physical prior for local temperature and precipitation field continuity.

### 2. Statistical ML Correction

A machine learning layer learns station-to-panchayat residual patterns from geography, terrain, and meteorological context. This is where the model learns micro-scale departures from the block forecast that are not captured by simple elevation adjustments alone.

### 3. Deep Spatial U-Net Correction

The repository includes a PyTorch Residual U-Net for super-resolution-style spatial refinement. It is designed to learn continuous local patterns across a coarse-to-fine rainfall field, with spatial structure informed by terrain and temperature context.

### 4. Reconciliation

The reconciliation step ensures that area-weighted Panchayat outputs add back up to the official block forecast. This is essential in a real meteorological workflow because operational agencies need forecast totals to remain physically and institutionally consistent.

---

## 🌲 ML Model 1 — XGBoost

> **Primary statistical learner for residual downscaling**

### Why XGBoost?

XGBoost is well-suited for structured tabular correction tasks where the output is a localized anomaly or residual grounded in topographic and meteorological features. It is transparent, fast, and effective when the signal is mostly feature-driven rather than sequence-driven.

### Model Role

The XGBoost model is used to infer local deviations from the official block forecast using variables such as:

- elevation gradients
- local DEM and slope structure
- distance to gauge or block center
- rainfall/temperature anomaly signatures
- monsoon exposure and rain-shadow indicators

### Operational Objective

Instead of predicting an entire forecast field from scratch, it learns the correction factor that transforms a coarse forecast into a more realistic Panchayat-scale value while preserving block totals after reconciliation.

---

## 🧠 ML Model 2 — Residual U-Net

> **Deep learning image-style local refinement engine**

### Why U-Net?

The downscaling task is spatially structured: rainfall and temperature vary smoothly over terrain but can change sharply across ridges, valleys, and exposed slopes. A residual U-Net is well-suited for learning those high-resolution spatial patterns.

### Architecture Summary

| Layer | Configuration | Purpose |
|---|---|---|
| Input | multichannel spatial tensor | rainfall, DEM, temperature, dewpoint context |
| Encoder | stacked convolution blocks | extract local-hierarchical spatial features |
| Bottleneck | compressed latent representation | model broad terrain-to-weather patterns |
| Decoder | transpose-convolution + skip connections | reconstruct high-resolution field |
| Output | rainfall residual map | local refinement on top of baseline forecast |

### U-Net Input Channels

The model pipeline uses a multi-channel representation combining:

- coarse rainfall field
- DEM / terrain structure
- station-like temperature context
- dewpoint context
- local atmospheric state structure

This allows the network to model realistic orographic effects and localized rainfall responses under monsoon conditions.

---

## 🌾 Advisory Engine

The project goes beyond weather prediction by converting downscaled weather into actionable agronomic intelligence. The advisory engine combines crop phenology, weather thresholds, and agronomic rules to generate operational guidance.

### Core Advisory Functions

| Function | Purpose |
|---|---|
| `AgrometAdvisoryGenerator` | Unified planetary advisory generation |
| `SprayWindowAdvisor` | Checks if spraying is safe under wind, humidity, and rainfall conditions |
| `IrrigationAdvisor` | Estimates irrigation needs based on crop stage and ET demand |
| `PestDiseaseAdvisor` | Evaluates blast, mildew, blight, and other climate-linked risks |
| `AgrometRuleEngine` | Applies GKMS-style general warnings and agronomic actions |

### Sample Advisory Outputs

- Spray status: GO / CAUTION / AVOID
- Irrigation action: IRRIGATE / LIGHT / HOLD
- Disease risk: LOW / MODERATE / HIGH / CRITICAL
- General action items for farmer or extension officer
- Conservative downgrading when weather confidence is low

### Crop Intelligence

The crop database includes crop calendars, development stages, and crop-specific coefficients like $K_c$ for irrigation logic. This helps turn forecast weather into stage-aware decisions that are meaningful for field operations.

---

## 🖥️ Application Interface

The platform exposes a browser-based interface and an API-driven operational workflow. The repository includes a static frontend under `static/` and a FastAPI backend in `src/api/`.

### Interface Modes

| Interface | Experience |
|---|---|
| **API Layer** | Structured weather and advisory endpoints |
| **Panchayat Map View** | Spatial inspection of block-to-panchayat forecast gradients |
| **Officer Workflow** | review, advisory approval, operational oversight |
| **Farmer-facing output** | simple, practical advisory cards and bulletins |

### Live API Endpoints

Examples from the backend include:

- `/health` — service health check
- `/api/v1/ingestion/live-block` — fetch live block forecast data
- `/api/v1/samples/imd-bulletin` — sample IMD bulletin payload
- geospatial and advisory routes for panchayat-based analysis

This makes the project suitable both as a research prototype and a deployable service layer.

---

## 📁 Project Structure

```
GramMausam-26074/
│
├── run_server.py                     # FastAPI app entry point
├── requirements.txt                  # Python dependencies
├── configs/                          # runtime config and deployment settings
├── data/
│   ├── crops/
│   │   ├── crop_database.json        # crop calendar and stage coefficients
│   │   └── pest_disease_models.json  # crop disease/pest logic
│   ├── geo/
│   │   ├── block_index.json          # block metadata
│   │   ├── blocks_mh.json            # Maharashtra block polygons
│   │   ├── panchayats_sample.geojson # example panchayat geometry
│   │   └── panchayats_by_block/      # per-block panchayat shape files
│   └── samples/
│       └── imd_block_forecast_bulletin.json
├── models/
│   └── weights/
│       ├── unet_best_model.pt        # trained U-Net weights
│       └── xgboost_downscaler.joblib # trained XGBoost model
├── src/
│   ├── advisory/                     # advisory logic, crop rules, irrigation, pest analysis
│   ├── api/                          # FastAPI routers and app setup
│   ├── core/                         # config and central constants
│   ├── downscaling/                  # physics, ML, reconciliation, U-Net, uncertainty
│   ├── ingestion/                    # live data loaders and sample ingestion
│   ├── vernacular/                   # translation/broadcasting utilities
│   ├── workflow/                     # officer review workflow logic
│   └── ...
├── static/
│   ├── index.html
│   ├── css/
│   └── js/
├── tests/
│   ├── test_advisory.py
│   ├── test_api.py
│   └── test_downscaling.py
└── README.md
```

---

## ⚙️ Installation & Usage

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| pip | Latest |
| Optional GPU | Helpful for deep learning workflows |

### Step 1 — Clone the repository

```bash
git clone <repository-url>
cd GramMausam-26074
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Run the application

```bash
python run_server.py
```

The server launches the API and serves the static frontend. Use the app through the browser, or interact with the backend endpoints directly.

### Step 4 — Run tests

```bash
python tests/test_downscaling.py
python tests/test_advisory.py
python tests/test_api.py
```

### Expected local access

- API server: `http://localhost:8050`
- Swagger docs: `http://localhost:8050/docs`
- Static UI: `http://localhost:8050/`

---

## 📚 References

1. **Chen, T. & Guestrin, C. (2016)** — *XGBoost: A Scalable Tree Boosting System*, KDD 2016
2. **Ronneberger, O., Fischer, P., & Brox, T. (2015)** — *U-Net: Convolutional Networks for Biomedical Image Segmentation*, MICCAI
3. **India Meteorological Department** — *Gramin Krishi Mausam Sewa (GKMS) advisories and agrometeorological standards*
4. **ICAR / Ministry of Agriculture** — Crop stage and agronomic recommendations
5. **Open geospatial and hydrometeorological standards** — used for polygon, weather, and forecast interoperability

---

## 👥 Team

> Built for **Smart India Hackathon — Problem Statement 26074**
> Downscaling of weather forecast from Block level to Panchayat level for agro-meteorological advisory services.

*🌾 GRAMMAUSAM — Hyperlocal climate intelligence for farmers and agricultural decision-makers.*
