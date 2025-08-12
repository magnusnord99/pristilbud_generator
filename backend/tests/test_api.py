# backend/tests/test_api.py
from fastapi.testclient import TestClient
from main import app

def test_generate_pdf_endpoint(mocker):
    import write_to_pdf as pdfmod
    FAKE_DATA = {
        "grouped_sums": [("Oppstart/planlegging", 10000.0)],
        "total_days": 1,
        "post_prod_days": 0,
        "pre_prod_days": 1,
        "details": {"Kunde": "Acme", "Versjon": "v1"},
        "company_info": {"Org.nr": "123"},
        "total_excl_mva": 10000.0,
        "total_incl_mva": 12500.0,
    }
    mocker.patch("from_google.fetch_google_data", return_value=FAKE_DATA)

    client = TestClient(app)
    payload = {
        "url": "https://docs.google.com/spreadsheets/d/FAKE/edit",
        "language": "NO",
        "reise": "y",
        "mva": "n"
    }
    r = client.post("/generate-pdf", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "attachment;" in r.headers.get("content-disposition", "")
    assert r.content.startswith(b"%PDF")