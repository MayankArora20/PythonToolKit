import fitz  # PyMuPDF

pdf_document = "c:/Users/mkaro/Desktop/python/playingWithpdf/pdfs/rep.pdf"
doc = fitz.open(pdf_document)

for page_num in range(len(doc)):
    page = doc.load_page(page_num)  # Load page
    pix = page.get_pixmap()  # Render page to an image
    pix.save(f"page_{page_num + 1}.png")  # Save image
