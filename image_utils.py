import cv2, numpy, pytesseract
import text_utils

image_text_original       = ""
image_text_grayscaled     = ""
image_text_monochromed    = ""
image_text_mean_threshold = ""

def scan_image(image):
    image = numpy.array(image) # converts the image to a compatible format

    # 0. Original 
    try:
        image_text_original = pytesseract.image_to_string(image, config = "--psm 12")
        return image_text_original
    except TypeError:
        print("Cannot open this file type.")

def simplify_image(image):
    image = numpy.array(image) # converts the image to a compatible format

    # 1. Grayscale
    try: 
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except: 
        print ("Couldn't grayscale image")

    # 2. Monochrome
    try: 
        image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    except: 
        print ("Couldn't monochrome image")

    # 3. Mean threshold
    try:
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    except: 
        print ("Couldn't mean threshold image")

    return image