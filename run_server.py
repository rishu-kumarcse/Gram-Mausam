"""
GramMausam- Server Launcher.
Starts FastAPI application with embedded Web UI.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import uvicorn
from src.core.config import config

def main():
    print("=" * 70)
    print("  [GramMausam-26074] Weather Downscaling & Agro-Met Intelligence")
    print("  Smart India Hackathon - Problem Statement ID 26074")
    print("  Ministry of Earth Sciences (MoES) & India Meteorological Department (IMD)")
    print(f"  Serving on http://localhost:{config.port}")
    print("  OpenAPI Documentation: http://localhost:{config.port}/docs")
    print("=" * 70)
    
    uvicorn.run(
        "src.api.main:app",
        host=config.host,
        port=config.port,
        reload=False
    )

if __name__ == "__main__":
    main()
