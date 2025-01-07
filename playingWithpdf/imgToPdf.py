# Python3 program to convert image to pdf
# using img2pdf library

# importing necessary libraries
import img2pdf
from PIL import Image
import os
from os import listdir
from os.path import isfile, join

# storing image path
imgs = [f for f in listdir("c:/Users/mkaro/Desktop/python/playingWithpdf/FilesToMerge") if isfile(join("c:/Users/mkaro/Desktop/python/playingWithpdf/FilesToMerge", f))]
img_path = "c:/Users/mkaro/Desktop/python/playingWithpdf/FilesToMerge/"

# storing pdf path
pdf_path = "c:/Users/mkaro/Desktop/python/playingWithpdf/pdfs/claim.pdf"
# opening or creating pdf file

imgList = []

for i, imgName in enumerate(imgs): 
    print(f"{i}: {img_path + imgName}") 
    # appending image path 
    imgList.append(img_path + imgName)

# Now you can use img2pdf to convert the list of image paths to a PDF 

with open(pdf_path, "wb") as f: f.write(img2pdf.convert(imgList))
# output
print("Successfully made pdf file")
