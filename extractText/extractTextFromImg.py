import easyocr

# Initialize EasyOCR reader (specify language if needed)
reader = easyocr.Reader(['en'])  # 'en' for English

# Load and process the image
result = reader.readtext("C:/Users/mkaro/Desktop/python/extractText/extractTextFromHere/rent.png")

# Extract and print detected text
for detection in result:
    print(detection[1])  # detection[1] contains the recognized text