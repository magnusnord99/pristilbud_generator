# Common utilities and constants for PDF generation
import os
import re

# Base directory and paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


def _sanitize_filename(name: str) -> str:
    """Sanitize filename by removing invalid characters"""
    name = (name or "N_A").strip()
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name)


def _extract_sheet_id(google_url: str) -> str:
    """Extract Google Sheets ID from URL"""
    # Tåler både .../d/<id>/edit og .../d/<id> varianter
    m = re.search(r"/d/([a-zA-Z0-9-_]+)", google_url or "")
    if not m:
        raise ValueError("Ugyldig Google Sheets URL.")
    return m.group(1)
