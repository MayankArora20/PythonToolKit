# Python3 program to convert image to pdf
# using img2pdf library

# importing necessary libraries
import img2pdf
from PIL import Image
import os
from os import listdir
from os.path import isfile, join

# storing image path
imgs = [f for f in listdir("C:/Users/mkaro/Desktop/python/imgsToPdf/FilesToMerge") if isfile(join("C:/Users/mkaro/Desktop/python/imgsToPdf/FilesToMerge", f))]
img_path = "C:/Users/mkaro/Desktop/python/imgsToPdf/FilesToMerge/"

# storing pdf path
pdf_path = "C:/Users/mkaro/Desktop/python/imgsToPdf/claim.pdf"
# opening or creating pdf file
# file = open(pdf_path, "ab")

imgList = []

for imgName in imgs:
    print(img_path+imgName)
    # opening image
    image = Image.open(img_path+imgName)
    imageRGB = image.convert("RGB")
    imgList.insert(imageRGB)

# closing pdf file
# file.close()
im_1.save(r'C:\Users\Ron\Desktop\Test\my_images.pdf', save_all=True, append_images=image_list)
# output
print("Successfully made pdf file")
