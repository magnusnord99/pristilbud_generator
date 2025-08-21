# PDF Generators Package
# Contains modules for generating different types of PDFs

# Lazy imports to avoid import errors
def _import_generate_pdf():
    from .price_quote import generate_pdf
    return generate_pdf

def _import_generate_project_description_pdf():
    from .project_description import generate_project_description_pdf
    return generate_project_description_pdf

def _import_common():
    from .common import BASE_DIR, LOGO_PATH
    return BASE_DIR, LOGO_PATH

# Export the functions and constants
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
