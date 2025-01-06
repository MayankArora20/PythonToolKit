from PyPDF2 import PdfMerger
from os import listdir
from os.path import isfile, join
import glob

pdfs = [f for f in listdir("c:/Users/mkaro/Desktop/pythoPdfMerger/FilesToMerge") if isfile(join("c:/Users/mkaro/Desktop/pythoPdfMerger/FilesToMerge", f))]

print(pdfs)

merger = PdfMerger()

for pdf in pdfs:
    print("merging: "+pdf)
    merger.append("c:/Users/mkaro/Desktop/pythoPdfMerger/FilesToMerge/"+pdf)

merger.write("c:/Users/mkaro/Desktop/pythoPdfMerger/MergedFile.pdf")
merger.close
