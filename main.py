from write_to_pdf import write_to_pdf
import from_google

def generate_pdf():
    data = from_google.fetch_google_data()
    output_pdf = "Price_offer_output.pdf"
    write_to_pdf(data, output_pdf)

    with open(output_pdf, "rb") as f:
        pdf_data = f.read()

    response = Response(pdf_data, content_type="application/pdf")
    response.headers["Content-Disposition"] = "inline; filename=Price_offer_output.pdf"
    return response

if __name__ == "__main__":
    generate_pdf