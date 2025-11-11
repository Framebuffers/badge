import logging
from PIL import Image
from hw.epd import EPD

class ImageManipulation:
    def __init__(self, epd: EPD) -> None:
        self._image_buffer = []
        self.dp: EPD = epd
        pass
    
    def to_1b_bmp(self, img: Image.Image) -> Image.Image:
        """Convert image to 1-bit BMP format suitable for e-ink displays."""
        logging.debug("Converting image to 1-bit BMP format")
        img_1b = img.convert('1')  # Convert to 1-bit pixels, black and white
        logging.debug("Conversion complete")
        return img_1b

    def resize_image(self, img: Image.Image, width: int, height: int) -> Image.Image:
        """Resize image to specified width and height."""
        logging.debug(f"Resizing image to {width}x{height}")
        resized_img = img.resize((width, height), Image.ANTIALIAS) # type: ignore
        logging.debug("Resizing complete")
        return resized_img

    
    