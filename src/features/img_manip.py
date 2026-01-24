import logging
from PIL import Image
from ..hw import EPD

logger = logging.getLogger(__name__)


class ImageManipulation:
    def __init__(self, epd: EPD) -> None:
        self._image_buffer: list[Image.Image] = []
        self.dp: EPD = epd

    def to_1b_bmp(self, img: Image.Image, resize_to_display: bool = True) -> Image.Image:
        """Convert image to 1-bit BMP format suitable for e-ink displays.

        Args:
            img: PIL Image to convert
            resize_to_display: If True, resize to display dimensions
        """
        logger.debug(f"Converting image to 1-bit BMP format. Input size: {img.size}")
        img_1b = img.convert('1')

        if resize_to_display:
            target_size = (self.dp.width, self.dp.height)
            logger.debug(f"Resizing to display dimensions: {target_size}")
            img_1b = img_1b.resize(target_size, Image.Resampling.LANCZOS)

        logger.debug("Conversion complete")
        return img_1b

    def resize_image(self, img: Image.Image, width: int | None = None, height: int | None = None) -> Image.Image:
        """Resize image to specified dimensions. Defaults to display dimensions."""
        w = width if width is not None else self.dp.width
        h = height if height is not None else self.dp.height
        logger.debug(f"Resizing image to {w}x{h}")
        resized_img = img.resize((w, h), Image.Resampling.LANCZOS)
        logger.debug("Resizing complete")
        return resized_img
