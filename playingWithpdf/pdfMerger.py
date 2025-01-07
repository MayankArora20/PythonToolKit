from PyPDF2 import PdfMerger
from os import listdir
from os.path import isfile, join

# Define the directory containing the PDF files
input_dir = "c:/Users/mkaro/Desktop/python/playingWithpdf/FilesToMerge"
output_pdf = "c:/Users/mkaro/Desktop/python/playingWithpdf/FilesToMerge/MergeFiles.pdf"

# Get a list of all PDF files in the directory
pdfs = [f for f in listdir(input_dir) if isfile(join(input_dir, f)) and f.endswith('.pdf')]

# Print the list of PDFs to verify
print(pdfs)

# Create a PdfMerger object
merger = PdfMerger()

# Append each PDF to the merger
for pdf in pdfs:
    print("Merging:", pdf)
    merger.append(join(input_dir, pdf))

# Write out the merged PDF
merger.write(output_pdf)
merger.close()

print(f"Merged PDF saved as {output_pdf}")
