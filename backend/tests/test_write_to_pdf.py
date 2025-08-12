# backend/tests/test_write_to_pdf.py
import io
import builtins
import types
import write_to_pdf as pdfmod

FAKE_DATA = {
    "grouped_sums": [
        ("Oppstart/planlegging", 10000.0),
        ("Produksjonsdager", 50000.0),
        ("Post produksjon", 20000.0),
        ("Produksjon totalt eksl. mva", 80000.0),
        ("Produksjon totalt inkl. mva", 100000.0),
    ],
    "total_days": 5,
    "post_prod_days": 3,
    "pre_prod_days": 1,
    "details": {
        "Kunde": "Test Kunde AS",
        "Versjon": "v1",
        "Tilbud dato": "2025-08-09",
        "Prosjekt": "Testprosjekt",
        "Referanse": "REF-123",
        "Deres referanse": "Kontakt X",
        "Kundenummer": "1001",
        "Vår kontakt": "Magnus",
        "Betalingsdetaljer": "14 dager",
        "Leveringsdato": "2025-09-01",
    },
    "company_info": {
        "Org.nr": "123 456 789",
        "Adresse": "Gate 1\n0001 Oslo",
        "E-post": "hei@leafilms.no",
        "Telefon": "+47 99 99 99 99",
    },
    "total_excl_mva": 80000.0,
    "total_incl_mva": 100000.0,
}

def test_generate_pdf_returns_buffer_and_name(mocker):
    # Mock Google
    mocker.patch("from_google.fetch_google_data", return_value=FAKE_DATA)

    buf, fname = pdfmod.generate_pdf(
        google_url="https://docs.google.com/spreadsheets/d/ABC123/edit",
        language="NO",
        reise="y",
        mva="n"
    )

    assert isinstance(buf, io.BytesIO)
    assert fname.startswith(("Pristilbud_", "Price_offer_"))
    # PDF header
    head = buf.getvalue()[:4]
    assert head == b"%PDF"

def test_filename_sanitization(mocker):
    fake = FAKE_DATA.copy()
    fake["details"] = dict(FAKE_DATA["details"], Kunde="Kunde/Med:Ulovlige*tegn?")
    mocker.patch("from_google.fetch_google_data", return_value=fake)
    buf, fname = pdfmod.generate_pdf(
        "https://docs.google.com/spreadsheets/d/ABC123/edit", "EN", "n", "y"
    )
    assert "Kunde_Med_Ulovlige_tegn_" in fname

def test_language_en_and_vat_line(mocker):
    mocker.patch("from_google.fetch_google_data", return_value=FAKE_DATA)
    buf, _ = pdfmod.generate_pdf(
        "https://docs.google.com/spreadsheets/d/ABC123/edit", "EN", "n", "y"
    )
    # Lettvekts-sjekk: fil ikke tom og PDF
    data = buf.getvalue()
    assert data.startswith(b"%PDF")
    assert len(data) > 1000  # grov sanity
