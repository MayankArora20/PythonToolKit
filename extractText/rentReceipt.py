from fpdf import FPDF
import os
from datetime import datetime, timedelta

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
def generate_rent_receipt(month, year, output_dir="rent_receipts"):

    pdf = FPDF()
    for month in config["months"]:
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Draw border
        padding = 7
        pdf.set_line_width(0.5)
        pdf.rect(10, 10, 190, 120)  # Outer rectangle
        pdf.set_xy(10 + padding, 10 + padding) 

        # Title
        pdf.ln(6)
        pdf.cell(0, 7, txt="Rent Receipt", ln=True, align='C')
        pdf.cell(0, 7, txt=f"{config['payment_date']} {month} {year}", ln=True, align='C')

        pdf.ln(6)
        
        # Content
        content = (
            f"Received sum of Rs. {config['rent_amount']}/- from {config['your_name']} "
            f"towards the rent of property located at {config['property_address']} "
            f"for the period {month} {year}."
        )
        pdf.multi_cell(0, 7, txt=content)

        pdf.ln(6)
        pdf.cell(0, 6, txt=config["owner_name"], ln=True)
        pdf.cell(0, 6, txt=f"PAN: {config['owner_pan']}", ln=True)

    # Create output directory if not exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the PDF
    pdf_output_path = os.path.join(output_dir, f"Rent_Receipt_{month}_{year}.pdf")
    pdf.output(pdf_output_path)
    print(f"Generated: {pdf_output_path}")

# Main function to generate receipts for all months
def generate_all_receipts(year):
    generate_rent_receipt("month", year)

# Run the program
if __name__ == "__main__":
    
    generate_all_receipts(config['year'])