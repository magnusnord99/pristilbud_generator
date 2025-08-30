# Common utilities and constants for PDF generation
import os
import re

# Base directory and paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


def _sanitize_filename(name: str) -> str:
    """Sanitize filename by removing invalid characters while preserving readability"""
    if not name:
        return "N_A"
    
    name = name.strip()
    
    # Replace only truly problematic characters
    # Keep: letters, numbers, spaces, hyphens, underscores, dots, parentheses
    # Remove: < > : " | ? * / \ and other problematic characters
    problematic_chars = '<>:"|?*\\/'
    for char in problematic_chars:
        name = name.replace(char, '_')
    
    # Replace multiple spaces/underscores with single underscore
    name = re.sub(r'[_\s]+', '_', name)
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    # Ensure it's not empty
    if not name:
        return "N_A"
    
    return name


def _extract_sheet_id(google_url: str) -> str:
    """Extract Google Sheets ID from URL"""
    # Tåler både .../d/<id>/edit og .../d/<id> varianter
    m = re.search(r"/d/([a-zA-Z0-9-_]+)", google_url or "")
    if not m:
        raise ValueError("Ugyldig Google Sheets URL.")
    return m.group(1)
