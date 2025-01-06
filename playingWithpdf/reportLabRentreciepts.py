from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os

# Configuration
config = {
    "owner_name": "owner_name",
    "year": 2024,
    "owner_pan": "pan",
    "property_address": "A wing Flat 101 Haunted society, Bhoot Bangala, Ghost City",
    "rent_amount": 1000,
    "your_name": "Hulk Smash",
    "payment_date": 1,  # Day of the month rent is paid
    "months": ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October",
               "November", "December"]
}

# Function to generate rent receipt PDF
def generate_rent_receipts(year, output_dir="rent_receipts"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_path = os.path.join(output_dir, f"Rent_Receipts_{year}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)

    width, height = A4  # Page dimensions
    padding = 1.5 * cm  # Padding around the border
    receipt_height = (height - 3 * padding) / 2  # Height of each receipt

    for i, month in enumerate(config['months']):
        pos = i % 2  # 2 receipts per page

        if pos == 0 and i != 0:
            c.showPage()  # Move to next page after two receipts

        y_offset = height - padding - receipt_height if pos == 0 else padding

        # Draw the outer border (rectangle)
        c.setLineWidth(1)
        c.rect(padding, y_offset, width - 2 * padding, receipt_height)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, y_offset + receipt_height - 2 * cm, "Rent Receipt")

        # Add payment date below the title
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, y_offset + receipt_height - 2.7 * cm, f"{config['payment_date']} {month}, {year}")

        # Content
        content = (
            f"Received sum of <b>Rs. {config['rent_amount']}/-</b> from <b>{config['your_name']}</b> "
            f"towards the rent of property located at <b>{config['property_address']}</b> "
            f"for the period <b>{month}, {year}</b>."
        )

        # Word wrapping and adding content as a Paragraph
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_normal.fontName = 'Helvetica'
        style_normal.fontSize = 12
        style_normal.leading = 14  # Line spacing

        paragraph = Paragraph(content, style_normal)
        frame = Frame(padding + 5, y_offset + 1 * cm, width - 3 * padding, receipt_height - 5 * cm, showBoundary=0)
        frame.addFromList([paragraph], c)

        # Add Owner's details
        c.drawString(padding + 5, y_offset + 5 * cm, config["owner_name"])
        c.drawString(padding + 5, y_offset + 4.5 * cm, f"PAN: {config['owner_pan']}")

    # Save the PDF
    c.save()
    print(f"Generated: {pdf_path}")

# Run the program
if __name__ == "__main__":
    generate_rent_receipts(config['year'])
