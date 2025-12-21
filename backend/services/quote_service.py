"""
Quote Service - Handles data fetching and processing for price quotes
Separates data retrieval from PDF generation for better flexibility
"""
import from_google
from pdf_generators.common import _extract_sheet_id
from typing import Dict, List, Tuple, Optional, Any


def fetch_quote_data(google_url: str) -> Dict[str, Any]:
    """
    Fetch quote data from Google Sheets
    
    Args:
        google_url: Full Google Sheets URL
        
    Returns:
        Dictionary containing all quote data:
        - grouped_sums: List of (category, amount) tuples
        - total_days: int or float
        - post_prod_days: int or float
        - pre_prod_days: int or float
        - details: Dict of customer/project details
        - company_info: Dict of company information
        - total_excl_mva: float
        - total_incl_mva: float
        - sheet_id: str (for reference)
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If data fetching fails
    """
    sheet_id = _extract_sheet_id(google_url)
    
    # Fetch data from Google Sheets
    data = from_google.fetch_google_data(SPREADSHEET_ID=sheet_id)
    
    # Add sheet_id for reference
    data["sheet_id"] = sheet_id
    
    return data


def prepare_quote_data_for_pdf(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare quote data for PDF generation
    Extracts and validates required fields
    
    Args:
        data: Quote data dictionary from fetch_quote_data()
        
    Returns:
        Prepared data dictionary for PDF generation
    """
    return {
        "grouped_sums": data["grouped_sums"],
        "total_days": data["total_days"],
        "post_prod_days": data["post_prod_days"],
        "pre_prod_days": data["pre_prod_days"],
        "details": data["details"],
        "company_info": data["company_info"],
        "total_excl_mva": data["total_excl_mva"],
        "total_incl_mva": data["total_incl_mva"],
    }

