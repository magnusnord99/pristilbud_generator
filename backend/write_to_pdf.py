# backend/write_to_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import from_google
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


def _sanitize_filename(name: str) -> str:
    name = (name or "N_A").strip()
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name)


def _extract_sheet_id(google_url: str) -> str:
    # Tåler både .../d/<id>/edit og .../d/<id> varianter
    m = re.search(r"/d/([a-zA-Z0-9-_]+)", google_url or "")
    if not m:
        raise ValueError("Ugyldig Google Sheets URL.")
    return m.group(1)


def _header_and_company_block(c, details, company_info, y_start):
    c.setFont("Helvetica", 11)
    y = y_start
    # Venstre: kontakt/kunde
    c.drawString(50, y, f"{details.get('Vår kontakt', 'N/A')}/{details.get('Kunde', 'N/A')}")
    # Høyre: logo
    c.drawImage(LOGO_PATH, 410, y - 50, width=150, height=75, preserveAspectRatio=True, mask='auto')
    y -= 70

    # Bedriftsinfo
    c.setFont("Helvetica-Bold", 11)
    c.drawString(360, y, "LEA FILMS")
    c.setFont("Helvetica", 10)

    col_1_x = 360
    col_2_x = col_1_x + 100
    col_y = y - 15
    for label, value in company_info.items():
        c.drawString(col_1_x, col_y, f"{label}:")
        for line in (value or "").split("\n"):
            c.drawString(col_2_x, col_y, line)
            col_y -= 15
    return y - 130  # plass før neste seksjon


def _offer_block(c, language, details, y):
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Tilbud" if language == "NO" else "Offer")
    y -= 20

    c.setFont("Helvetica", 10)
    if language == "NO":
        offer_details = [
            ("Versjon:", details.get("Versjon", "N/A")),
            ("Tilbud dato:", details.get("Tilbud dato", "N/A")),
            ("Prosjekt:", details.get("Prosjekt", "N/A")),
            ("Referanse:", details.get("Referanse", "N/A")),
            ("Deres kontakt:", details.get("Deres referanse", "N/A")),
            ("Kundenummer:", details.get("Kundenummer", "N/A")),
            ("Vår kontakt:", details.get("Vår kontakt", "N/A")),
            ("Betalings info:", details.get("Betalingsdetaljer", "N/A")),
            ("Levering dato:", details.get("Leveringsdato", "N/A")),
        ]
    else:
        offer_details = [
            ("Version:", details.get("Versjon", "N/A")),
            ("Offer Date:", details.get("Tilbud dato", "N/A")),
            ("Project:", details.get("Prosjekt", "N/A")),
            ("Reference:", details.get("Referanse", "N/A")),
            ("Their contact:", details.get("Deres referanse", "N/A")),
            ("Customer number:", details.get("Kundenummer", "N/A")),
            ("Our contact:", details.get("Vår kontakt", "N/A")),
            ("Payment details:", details.get("Betalingsdetaljer", "N/A")),
            ("Delivery date:", details.get("Leveringsdato", "N/A")),
        ]

    column_positions = [50, 360, 500, 650]
    total_columns = len(column_positions)
    rows_per_column = (len(offer_details) // 2) + 1

    for col in range(total_columns):
        col_items = offer_details[col * rows_per_column : (col + 1) * rows_per_column]
        current_y = y
        for label, value in col_items:
            c.drawString(column_positions[col], current_y, f"{label}")
            c.drawString(column_positions[col] + 100, current_y, f"{value}")
            current_y -= 15
    return y  # uendret baseline – vi justerer i neste blokk


def _terms_block(c, language, reise, y):
    left_margin, right_margin = 50, 550
    max_width = right_margin - left_margin

    # Tekster (fra din original)
    terms_en_travel = (
        "Leafilms will be responsible for the overall planning, production, and delivery of the project as outlined in this offer.\n"
        "The project scope, timeline, and deliverables will be agreed upon before production begins. Any changes to the "
        "scope during the project may incur additional costs and require a written agreement.\n\n"
        "Travel, accommodation, and subsistence costs for the crew are included in the budget unless otherwise specified.\n\n"
        "If unforeseen circumstances (e.g., severe weather or other factors beyond Leafilms’ control) prevent production "
        "from proceeding as planned, alternative arrangements will be made in consultation with the client. Any delays or "
        "rescheduling may incur additional costs.\n\n"
        "Cancellation within 14 days before the start date: 50% of the agreed price will be invoiced.\n"
        "Cancellation within 48 hours before the start date: 100% of the agreed price will be invoiced.\n\n"
        "The client is granted full copyright ownership and an unlimited commercial license for all produced content. "
        "Leafilms retains the right to use the content for its own marketing purposes. "
        "Leafilms must be credited in accordance with industry standards wherever the material is used, where practical.\n\n"
        "All materials, including footage and project files, will be delivered to the client as agreed. Storage and archiving of "
        "the material beyond the delivery date are the responsibility of the client.\n\n"
        "The invoice is split into two equal payments. The first half will be issued upon signing the production agreement, "
        "and the second half will be issued after the final production day. Please be aware that late payments may incur "
        "additional fees."
    )
    terms_en_no_travel = terms_en_travel.replace(
        "are included in the budget", "are not included in the budget"
    )

    terms_no_reise = (
        "Leafilms vil være ansvarlig for planleggingen, produksjonen og leveringen av prosjektet slik det er beskrevet i dette tilbudet.\n"
        "Prosjektets omfang, tidslinje og leveranser avtales før produksjonen starter. Eventuelle endringer i omfanget underveis kan medføre ekstra kostnader.\n\n"
        "Reise-, overnattings- og oppholdsutgifter for teamet er inkludert i budsjettet med mindre annet er spesifisert.\n\n"
        "Dersom uforutsette omstendigheter (f.eks. ekstremvær eller andre faktorer utenfor Leafilms’ kontroll) hindrer produksjonen i å gjennomføres som planlagt, "
        "vil alternative løsninger utarbeides i samråd med kunden. Eventuelle forsinkelser eller omlegginger kan medføre ekstra kostnader.\n\n"
        "Kansellering innen 14 dager før startdato: 50 % av den avtalte prisen vil bli fakturert.\n"
        "Kansellering innen 48 timer før startdato: 100 % av den avtalte prisen vil bli fakturert.\n\n"
        "Leafilms beholder full opphavsrett til alt produsert materiale. Kunden gis bruksrettigheter for det avtalte formålet og prosjektet. "
        "Videre salg eller distribusjon er ikke tillatt uten skriftlig samtykke fra Leafilms. Leafilms må krediteres i henhold til bransjestandarder "
        "der materialet brukes, der det er praktisk mulig.\n\n"
        "Alt materiale, inkludert opptak og prosjektfiler, vil bli levert til kunden som avtalt. Lagring og arkivering av materialet utover leveringsdatoen er kundens ansvar.\n\n"
        "Fakturaen deles opp i to like betalinger. Den første halvparten faktureres ved signering av produksjonsavtalen, og den andre halvparten faktureres etter siste produksjonsdag. "
        "Vær oppmerksom på at forsinkede betalinger kan medføre ekstra gebyrer."
    )
    terms_no_uten_reise = terms_no_reise.replace(
        "er inkludert i budsjettet", "er ikke inkludert i budsjettet"
    )

    y -= 90
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Vilkår" if language == "NO" else "Terms and Conditions")
    y -= 20

    c.setFont("Helvetica", 10 if language == "EN" else 9)
    text = (
        (terms_no_reise if reise == "y" else terms_no_uten_reise)
        if language == "NO"
        else (terms_en_travel if reise == "y" else terms_en_no_travel)
    )

    for paragraph in text.splitlines():
        wrapped = simpleSplit(paragraph.strip(), "Helvetica", 9, max_width)
        for line in wrapped:
            c.drawString(left_margin, y, line)
            y -= 9
        y -= 5

    y -= 20
    return max(y, 60)  # unngå å gå for lavt


def _table_block(c, language, grouped_sums, total_days, post_prod_days, pre_prod_days, y):
    # Tabellheaders
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Beskrivelse" if language == "NO" else "Description")
    c.drawString(250, y, "Antall" if language == "NO" else "Quantity")
    c.drawString(400, y, "Sum (NOK)")
    y -= 15
    c.line(50, y, 550, y)
    y -= 15

    # Rader
    c.setFont("Helvetica", 10)
    for unit, total in grouped_sums:
        if unit in ["Produksjon totalt eksl. mva", "Produksjon totalt inkl. mva"]:
            continue

        c.drawString(50, y, unit)

        if unit == "Post produksjon":
            val = f"{post_prod_days} dager" if language == "NO" else f"{post_prod_days} days"
        elif unit == "Oppstart/planlegging":
            val = f"{pre_prod_days} dager" if language == "NO" else f"{pre_prod_days} days"
        else:
            val = f"{total_days} dager" if language == "NO" else f"{total_days} days"

        c.drawString(250, y, val if val else "-")
        c.drawString(400, y, f"{total:,.2f}")
        y -= 12

    c.line(50, y, 550, y)
    y -= 12
    return y


def _totals_block(c, language, total_excl_mva, total_incl_mva, mva, y):
    c.setFont("Helvetica-Bold", 10)

    if total_excl_mva is not None:
        lbl = "Produksjon totalt eksl. mva:" if language == "NO" else "Production total (excl. VAT):"
        c.drawString(50, y, lbl)
        c.drawRightString(472, y, f"{total_excl_mva:,.2f} NOK")
        y -= 15

    if (mva == "y") and (total_incl_mva is not None):
        lbl = "Produksjon totalt inkl. mva:" if language == "NO" else "Production total (incl. VAT):"
        c.drawString(50, y, lbl)
        c.drawRightString(472, y, f"{total_incl_mva:,.2f} NOK")
        y -= 15

    return y


def generate_pdf(google_url: str, language: str, reise: str, mva: str):
    """
    language: 'NO' eller 'EN'
    reise: 'y' eller 'n'
    mva: 'y' eller 'n'
    """
    language = (language or "NO").upper()
    reise = (reise or "n").lower()
    mva = (mva or "n").lower()

    sheet_id = _extract_sheet_id(google_url)

    # Hent data fra Google
    data = from_google.fetch_google_data(SPREADSHEET_ID=sheet_id)
    grouped_sums = data["grouped_sums"]
    total_days = data["total_days"]
    post_prod_days = data["post_prod_days"]
    pre_prod_days = data["pre_prod_days"]
    details = data["details"]
    company_info = data["company_info"]
    total_excl_mva = data["total_excl_mva"]
    total_incl_mva = data["total_incl_mva"]

    # Foreslått filnavn
    kunde = _sanitize_filename(details.get("Kunde", "N_A"))
    versjon = _sanitize_filename(details.get("Versjon", "v0"))
    base = "Pristilbud" if language == "NO" else "Price_offer"
    filename = f"{base}_{kunde}_{versjon}_@leafilms.pdf"

    # Lag PDF i minnet
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    y = _header_and_company_block(c, details, company_info, y_start=800)
    _offer_block(c, language, details, y)
    y = _terms_block(c, language, reise, y)
    y = _table_block(c, language, grouped_sums, total_days, post_prod_days, pre_prod_days, y)
    _totals_block(c, language, total_excl_mva, total_incl_mva, mva, y)

    c.save()
    buf.seek(0)
    return buf, filename
