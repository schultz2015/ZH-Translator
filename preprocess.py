import cv2


class Preprocess:
    def __init__(self):
        super().__init__()

    def scale(self, image):
        print("scale")
        size = 600
        # 获取原始图像宽高。
        height, width = image.shape[0], image.shape[1]
        # 等比例缩放尺度。
        scale = height / size
        # 获得相应等比例的图像宽度。
        width_size = int(width / scale)
        print(width, height)
        # resize
        if (width <= 100 or height < 150):
            image_resize = cv2.resize(image, (width_size, size))
        else:
            image_resize = image
        return image_resize

    def binary(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        return denoised
