from weasyprint import HTML

html_content = """
<html>
  <head>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      h1 { text-align: center; color: #4CAF50; }
      .content { margin-top: 20px; }
      .signature { margin-top: 40px; font-weight: bold; }
    </style>
  </head>
  <body>
    <h1>Rent Receipt</h1>
    <div class="content">
      Received sum of Rs. <b>15,000/-</b> from <b>Jane Smith</b> towards the rent 
      of the property located at <i>123, Green Street, Springfield</i> for the 
      period of January 2024.
    </div>
    <div class="signature">
      Signature<br>
      John Doe<br>
      Owner's PAN: <b>ABCDE1234F</b>
    </div>
  </body>
</html>
"""

HTML(string=html_content).write_pdf("rent_receipt.pdf")
