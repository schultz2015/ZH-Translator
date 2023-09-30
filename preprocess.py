import cv2
import numpy as np

class Preprocess:
    def __init__(self):
        super().__init__()

    def process(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, binary = cv2.threshold(gray, 175, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

        mask = np.zeros(denoised.shape, dtype=np.uint8)
        cnts = cv2.findContours(denoised, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        print(cnts)
        cv2.fillPoly(mask, cnts, [255, 255, 255])
        mask = 255 - mask
        result = cv2.bitwise_or(denoised, mask)
        result=255-result
        return result
