from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap
from reportlab.lib.utils import simpleSplit
import from_google  # Import your existing script
import os
import re

url = input("Type your Google Sheets URL: ")

# Extract the Spreadsheet ID using regex
match = re.search(r"/d/([a-zA-Z0-9-_]+?)/edit", url)

if match:
    SPREADSHEET_ID_get = match.group(1)  # Extracted ID
    print(f"Extracted Spreadsheet ID: {SPREADSHEET_ID_get}")
else:
    print("Invalid URL format. Please check the link.")

# Fetch grouped data from from_google.py
data = from_google.fetch_google_data(SPREADSHEET_ID=SPREADSHEET_ID_get)
grouped_sums = data["grouped_sums"]
total_days = data["total_days"]
post_prod_days = data["post_prod_days"]
pre_prod_days = data["pre_prod_days"]
details = data["details"]
company_info = data["company_info"]
total_excl_mva = data["total_excl_mva"]
total_incl_mva = data["total_incl_mva"]

# Define PDF output file
# Hent navn fra 'Vår kontakt', og bruk 'N/A' hvis det ikke finnes
pdf_name = details.get('Kunde', 'N/A')

# Define page margins
left_margin = 50
right_margin = 550  # Adjusted to prevent text overflow
max_width = right_margin - left_margin  # Ensure text fits within the page width


# Rens filnavnet for ulovlige tegn
def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name)

clean_pdf_name = sanitize_filename(pdf_name)

# Lag en full filbane med det dynamiske navnet
output_pdf_no = f"/Users/magnusnordmo/Desktop/Pristilbud_{clean_pdf_name}_{details.get("Versjon", "N/A")}_@leafilms.pdf"
output_pdf_en = f"/Users/magnusnordmo/Desktop/Price_offer_{clean_pdf_name}_{details.get("Versjon", "N/A")}_@leafilms.pdf"


logo_path = "/Users/magnusnordmo/Desktop/Pristilbud_generator/logo.png"

# Function to create a PDF similar to the template
def write_to_pdf_en(data, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 11)

    # Start at the top of the page
    y_position = 800

    left_margin = 50
    right_margin = 550  # Adjusted to prevent text overflow
    max_width = right_margin - left_margin

    # Header - Left Side
    c.drawString(50, y_position, f"{details.get('Vår kontakt', 'N/A')}/{details.get('Kunde', 'N/A')}")


    logo_width = 150  # Width of the logo in points
    logo_height = 75  # Height of the logo in points
    c.drawImage(logo_path, 410, y_position - 50, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    y_position -= 70

    # Header - Right Side (Company Info)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(360, y_position, "LEA FILMS")
    c.setFont("Helvetica", 10)

    # Two columns for company info dynamically
    company_info_items = list(company_info.items())  # Convert dictionary to list of tuples
    col_1_x = 360  # X position for the first column
    col_2_x = col_1_x + 100  # X position for the second column
    col_y = y_position - 15

    for label, value in company_info_items:
        c.drawString(col_1_x, col_y, f"{label}:")
        for line in value.split("\n"):  # Handle multiline values
            c.drawString(col_2_x, col_y, line)
            col_y -= 15  # Move down for each line
    

    # Tilbud Section
    y_position -= 130  # Add space between sections
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position, "Offer")
    y_position -= 20  # Add space below header

    # Dynamic Offer Details
    c.setFont("Helvetica", 10)
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

    # Calculate rows per column dynamically
    column_positions = [50, 360, 500, 650]  # X positions for each column
    total_columns = len(column_positions)
    rows_per_column = (len(offer_details) // 2) + 1  # Items divided across 4 columns

    # Distribute items across 4 columns
    for col in range(total_columns):
        col_items = offer_details[col * rows_per_column:(col + 1) * rows_per_column]
        print(col_items)
        current_y = y_position  # Reset Y position for each column
        for label, value in col_items:
            c.drawString(column_positions[col], current_y, f"{label}")  # Draw label
            c.drawString(column_positions[col] + 100, current_y, f"{value}")  # Draw value with spacing
            current_y -= 15  # Move down for next row
        

    y_position -= 10 

        # Terms and Conditions text
    terms_and_conditions_en = """\
    Leafilms will be responsible for the overall planning, production, and delivery of the project as outlined in this offer.
    The project scope, timeline, and deliverables will be agreed upon before production begins. Any changes to the
    scope during the project may incur additional costs and require a written agreement. \n
    Travel, accommodation, and subsistence costs for the crew are included in the budget unless otherwise specified. \n
    If unforeseen circumstances (e.g., severe weather or other factors beyond Leafilms’ control) prevent production
    from proceeding as planned, alternative arrangements will be made in consultation with the client. Any delays or
    rescheduling may incur additional costs.\n
    Cancellation within 14 days before the start date: 50% of the agreed price will be invoiced.
    Cancellation within 48 hours before the start date: 100% of the agreed price will be invoiced.\n
    Leafilms retains full copyright to all materials produced. The client is granted usage rights for the agreed purpose
    and project. Resale or redistribution is not permitted without prior written consent from Leafilms.
    Leafilms must be credited in accordance with industry standards wherever the material is used, where practical.\n
    All materials, including footage and project files, will be delivered to the client as agreed. Storage and archiving of
    the material beyond the delivery date are the responsibility of the client.\n
    The invoice is split into two equal payments. The first half will be issued upon signing the production agreement,
    and the second half will be issued after the final production day. Please be aware that late payments may incur
    additional fees."""


    # Add this block below your table headers and before the footer:
    # Table Headers
    y_position -= 90  # Add space below the columns and before terms
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position, "Terms and Conditions")
    y_position -= 20  # Move down for the content

    # Draw terms and conditions
    c.setFont("Helvetica", 10)
    lines = terms_and_conditions_en.splitlines()  # Split the text into lines
 
    for paragraph in lines:
        wrapped_text = simpleSplit(paragraph.strip(), "Helvetica", 9, max_width)  # Wrap text

        for line in wrapped_text:
            c.drawString(left_margin, y_position, line)
            y_position -= 9  # Adjust line spacing

        y_position -= 5 

    # Ensure space for the footer remains
    y_position -= 20
    if y_position < 50:  # If running out of space, add a warning (or adjust further)
        print("Warning: Terms and Conditions section may overlap with the footer.")


    # Table Headers
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y_position, "Beskrivelse")
    c.drawString(250, y_position, "Antall")
    c.drawString(400, y_position, "Sum (NOK)")
    y_position -= 15
    c.line(50, y_position, 550, y_position)  # Line under headers
    y_position -= 15

    # Table Data (Exclude Produksjon totalt)
    c.setFont("Helvetica", 10)
    for unit, total in grouped_sums:
        if unit not in ["Produksjon totalt eksl. mva", "Produksjon totalt inkl. mva"]:
            c.drawString(50, y_position, unit)

            # Use specific days for Post produksjon and Oppstart/planlegging
            if unit == "Post produksjon":
                c.drawString(250, y_position, f"{post_prod_days} days" if post_prod_days else "-")
            elif unit == "Oppstart/planlegging":
                c.drawString(250, y_position, f"{pre_prod_days} days" if pre_prod_days else "-")
            else:
                c.drawString(250, y_position, f"{total_days} days" if total_days else "-")

            c.drawString(400, y_position, f"{total:,.2f}")
            y_position -= 12  # Space between rows


    c.line(50, y_position, 550, y_position)  # Line under headers
    y_position -= 12

    # Total Section
    c.setFont("Helvetica-Bold", 10)
    if total_excl_mva is not None:
        c.drawString(50, y_position, "Production total :")
        c.drawRightString(472, y_position, f"{total_excl_mva:,.2f} NOK")  # Align right
        y_position -= 40
    # if total_incl_mva is not None:
    #     c.drawString(50, y_position, "Produksjon totalt inkl. mva:")
    #     c.drawRightString(472, y_position, f"{total_incl_mva:,.2f} NOK")  # Align right
        

    # Save the PDF
    c.save()
    print(f"PDF (EN) saved to {filename}")






def write_to_pdf_no(data, filename):
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 11)

    # Start at the top of the page
    y_position = 800

    left_margin = 50
    right_margin = 550  # Adjusted to prevent text overflow
    max_width = right_margin - left_margin

    # Header - Left Side
    c.drawString(50, y_position, f"{details.get('Vår kontakt', 'N/A')}/{details.get('Kunde', 'N/A')}")


    logo_width = 150  # Width of the logo in points
    logo_height = 75  # Height of the logo in points
    c.drawImage(logo_path, 410, y_position - 50, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    y_position -= 70

    # Header - Right Side (Company Info)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(360, y_position, "LEA FILMS")
    c.setFont("Helvetica", 10)

    # Two columns for company info dynamically
    company_info_items = list(company_info.items())  # Convert dictionary to list of tuples
    col_1_x = 360  # X position for the first column
    col_2_x = col_1_x + 100  # X position for the second column
    col_y = y_position - 15

    for label, value in company_info_items:
        c.drawString(col_1_x, col_y, f"{label}:")
        for line in value.split("\n"):  # Handle multiline values
            c.drawString(col_2_x, col_y, line)
            col_y -= 15  # Move down for each line
    

    # Tilbud Section
    y_position -= 130  # Add space between sections
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position, "Tilbud")
    y_position -= 20  # Add space below header

    # Dynamic Offer Details
    c.setFont("Helvetica", 10)
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

    # Calculate rows per column dynamically
    column_positions = [50, 360, 500, 650]  # X positions for each column
    total_columns = len(column_positions)
    rows_per_column = (len(offer_details) // 2) + 1  # Items divided across 4 columns

    # Distribute items across 4 columns
    for col in range(total_columns):
        col_items = offer_details[col * rows_per_column:(col + 1) * rows_per_column]
        print(col_items)
        current_y = y_position  # Reset Y position for each column
        for label, value in col_items:
            c.drawString(column_positions[col], current_y, f"{label}")  # Draw label
            c.drawString(column_positions[col] + 100, current_y, f"{value}")  # Draw value with spacing
            current_y -= 15  # Move down for next row
        

        # Terms and Conditions text
    terms_and_conditions_no = """\
    Leafilms vil være ansvarlig for planleggingen, produksjonen og leveringen av prosjektet slik det er beskrevet i dette tilbudet.
    Prosjektets omfang, tidslinje og leveranser avtales før produksjonen starter. Eventuelle endringer i omfanget underveis kan 
    medføre ekstra kostnader. \n
    Reise-, overnattings- og oppholdsutgifter for teamet er inkludert i budsjettet med mindre annet er spesifisert. \n
    Dersom uforutsette omstendigheter (f.eks. ekstremvær eller andre faktorer utenfor Leafilms’ kontroll) hindrer produksjonen 
    i å gjennomføres som planlagt, vil alternative løsninger utarbeides i samråd med kunden. Eventuelle forsinkelser eller 
    omlegginger kan medføre ekstra kostnader.\n
    Kansellering innen 14 dager før startdato: 50 % av den avtalte prisen vil bli fakturert.
    Kansellering innen 48 timer før startdato: 100 % av den avtalte prisen vil bli fakturert.\n
    Leafilms beholder full opphavsrett til alt produsert materiale. Kunden gis bruksrettigheter for det avtalte formålet 
    og prosjektet. Videre salg eller distribusjon er ikke tillatt uten skriftlig samtykke fra Leafilms.
    Leafilms må krediteres i henhold til bransjestandarder der materialet brukes, der det er praktisk mulig.\n
    Alt materiale, inkludert opptak og prosjektfiler, vil bli levert til kunden som avtalt. Lagring og arkivering av 
    materialet utover leveringsdatoen er kundens ansvar.\n
    Fakturaen deles opp i to like betalinger. Den første halvparten faktureres ved signering av produksjonsavtalen, 
    og den andre halvparten faktureres etter siste produksjonsdag. Vær oppmerksom på at forsinkede betalinger kan medføre 
    ekstra gebyrer."""


    # Add this block below your table headers and before the footer:
    # Table Headers
    y_position -= 90  # Add space below the columns and before terms
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_position, "VIlkår")
    y_position -= 20  # Move down for the content

    # Draw terms and conditions
    c.setFont("Helvetica", 9)
    lines = terms_and_conditions_no.splitlines()  # Split the text into lines
 
    for paragraph in lines:
        wrapped_text = simpleSplit(paragraph.strip(), "Helvetica", 9, max_width)  # Wrap text

        for line in wrapped_text:
            c.drawString(left_margin, y_position, line)
            y_position -= 9  # Adjust line spacing

        y_position -= 5 

    # Ensure space for the footer remains
    y_position -= 20
    if y_position < 50:  # If running out of space, add a warning (or adjust further)
        print("Warning: Terms and Conditions section may overlap with the footer.")


    # Table Headers
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y_position, "Beskrivelse")
    c.drawString(250, y_position, "Antall")
    c.drawString(400, y_position, "Sum (NOK)")
    y_position -= 15
    c.line(50, y_position, 550, y_position)  # Line under headers
    y_position -= 15

    # Table Data (Exclude Produksjon totalt)
    c.setFont("Helvetica", 10)
    for unit, total in grouped_sums:
        if unit not in ["Produksjon totalt eksl. mva", "Produksjon totalt inkl. mva"]:
            c.drawString(50, y_position, unit)

            # Use specific days for Post produksjon and Oppstart/planlegging
            if unit == "Post produksjon":
                c.drawString(250, y_position, f"{post_prod_days} dager" if post_prod_days else "-")
            elif unit == "Oppstart/planlegging":
                c.drawString(250, y_position, f"{pre_prod_days} dager" if pre_prod_days else "-")
            else:
                c.drawString(250, y_position, f"{total_days} dager" if total_days else "-")

            c.drawString(400, y_position, f"{total:,.2f}")
            y_position -= 12  # Space between rows


    c.line(50, y_position, 550, y_position)  # Line under headers
    y_position -= 12

    # Total Section
    c.setFont("Helvetica-Bold", 10)
    if total_excl_mva is not None:
        c.drawString(50, y_position, "Produksjon totalt eksl. mva:")
        c.drawRightString(472, y_position, f"{total_excl_mva:,.2f} NOK")  # Align right
        y_position -= 15
    if total_incl_mva is not None:
        c.drawString(50, y_position, "Produksjon totalt inkl. mva:")
        c.drawRightString(472, y_position, f"{total_incl_mva:,.2f} NOK")  # Align right
        

    # Save the PDF
    c.save()
    print(f"PDF (NO) saved to {filename}")













# Generate the PDF
spraak = input("Enter language (NO/EN):")
if spraak == 'NO':
    write_to_pdf_no(data, output_pdf_no)  # Split the text into lines
elif spraak == 'EN':
    write_to_pdf_en(data, output_pdf_en)
