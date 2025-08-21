# backend/write_to_pdf.py
# This file now imports from the organized pdf_generators modules
# For backward compatibility, all functions are re-exported

# Lazy imports to avoid import errors
def _import_generate_pdf():
    from pdf_generators.price_quote import generate_pdf
    return generate_pdf

def _import_generate_project_description_pdf():
    from pdf_generators.project_description import generate_project_description_pdf
    return generate_project_description_pdf

def _import_common():
    from pdf_generators.common import BASE_DIR, LOGO_PATH
    return BASE_DIR, LOGO_PATH

# Re-export all functions for backward compatibility
__all__ = [
    'generate_pdf',
    'generate_project_description_pdf',
    'BASE_DIR',
    'LOGO_PATH'
]

# Make functions available at module level
def generate_pdf(*args, **kwargs):
    return _import_generate_pdf()(*args, **kwargs)

def generate_project_description_pdf(*args, **kwargs):
    return _import_generate_project_description_pdf()(*args, **kwargs)

# Make constants available
BASE_DIR, LOGO_PATH = _import_common()
