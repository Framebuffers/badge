import os
import logging
import time
import random
from typing import Literal, List

from PIL import Image, ImageDraw

from .routines import DisplayRoutines
from .img_manip import ImageManipulation

logger = logging.getLogger(__name__)

FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'fonts')
IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'img')


class DisplayTests:
    def __init__(self, display: DisplayRoutines) -> None:
        self.display = display
        self.img_manip = ImageManipulation(display.dp)

    def text(self, text: str, wait: int = 5) -> None:
        """Test text rendering on display."""
        logger.info('Testing text input.')
        logger.info(f'loading text: {text}')
        self.display.load_txt(text)
        self.display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'), 20, 0, 10, 10)
        self.display.render()
        time.sleep(wait)
        self.display.clear_canvas()
        logger.info('Canvas cleared')

    def image(self, img: Image.Image, wait: int = 5,
              aspect_ratio: Literal['stretch', 'center', 'fit', 'tile'] = 'fit') -> None:
        """Test image display with specified aspect ratio."""
        logger.info('Loading image')
        self.display.load_img_scaled(img, aspect_ratio)
        self.display.render()
        logger.debug(f"Rendered image, aspect_ratio={aspect_ratio}")
        time.sleep(wait)
        self.display.clear_canvas()
        logger.info('Canvas cleared')

    def canvas_create(self, orientation: str = 'horizontal') -> None:
        """Test canvas creation."""
        logger.debug(f'Creating canvas, orientation: {orientation}')
        self.display.create_canvas(orientation)
        logger.debug(f"Image exists: {self.display._image is not None}, Draw exists: {self.display._draw is not None}")

    def qr(self, text: str, size: int, x: int, y: int, wait: int = 5) -> None:
        """Test QR code generation and display."""
        self.display.create_qr_code(text, size, x, y)
        logger.debug("QR code created on canvas")
        if self.display._image:
            logger.debug(f"Canvas size: {self.display._image.size}, mode: {self.display._image.mode}")
        self.display.render()
        logger.debug("Rendered QR code")
        time.sleep(wait)
        self.display.clear_canvas()
        logger.info('Canvas cleared')

    def refresh_base(self, img: Image.Image, wait: int = 5) -> None:
        """Test refreshing the base image."""
        self.display.refresh_base_img(img)
        logger.debug("Performed partial refresh with new base image")
        time.sleep(wait)

    def fast_mode(self, images: List[Image.Image], wait: int = 5) -> None:
        """Test fast mode rendering with multiple images."""
        for idx, img in enumerate(images):
            logger.debug(f"Fast mode test iteration {idx}")
            self.display._image = img
            self.display.render(fast=True)
            time.sleep(wait)

    def render_partial(self, img: Image.Image, loops: int = 5) -> None:
        """Test partial refresh with a clock overlay."""
        logger.info('Testing partial refresh with clock')

        self.display._image = img.copy()
        self.display._draw = ImageDraw.Draw(self.display._image)
        self.display.render(fast=False)

        start_time = time.time()

        for i in range(loops):
            self.display._draw.rectangle((10, 10, 100, 35), fill=255)

            elapsed = time.time() - start_time
            self.display.load_txt(f'{elapsed:.1f}s')
            self.display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'), 20, 0, 10, 10)

            self.display.render(fast=True)
            logger.debug(f'Clock update {i+1}/{loops}')
            time.sleep(1)

        self.display.clear_canvas()
        logger.info('Test complete')

    def draw_shapes(self, wait: int = 5, clear_canvas: bool = True, refresh: bool = True) -> None:
        """Test drawing random shapes on canvas.

        Args:
            wait: Seconds to wait after rendering (only applies if refresh=True)
            clear_canvas: Whether to clear canvas after wait (only applies if refresh=True)
            refresh: Whether to render to display. Set False to overlay more content.
        """
        if not self.display._image:
            self.display.create_canvas('horizontal')

        for _ in range(10):
            x1_temp = random.randint(0, self.display.dp_width - 1)
            y1_temp = random.randint(0, self.display.dp_height - 1)
            x2_temp = random.randint(0, self.display.dp_width - 1)
            y2_temp = random.randint(0, self.display.dp_height - 1)

            x1, x2 = min(x1_temp, x2_temp), max(x1_temp, x2_temp)
            y1, y2 = min(y1_temp, y2_temp), max(y1_temp, y2_temp)

            shape_type = random.choice(['line', 'rectangle', 'arc'])

            if shape_type == 'line':
                self.display.draw_line(x1, y1, x2, y2, fill=random.choice([0, 255]))
            elif shape_type == 'rectangle':
                self.display.draw_rectangle(x1, y1, x2, y2, fill=128, outline=0)
            else:
                self.display.draw_arc(x1, y1, x2, y2, start=0, end=180, fill=0)

        logger.debug("Shapes drawn on canvas")

        if refresh:
            self.display.render()
            time.sleep(wait)
            if clear_canvas:
                self.display.clear_canvas()
                logger.info('Canvas cleared')

    def run_all(self, test_image: Image.Image | None = None) -> None:
        """Run all display tests."""
        if test_image is None:
            test_path = os.path.join(IMG_PATH, 'test')
            image_files = [f for f in os.listdir(test_path)
                           if f.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg'))]
            if image_files:
                random_file = random.choice(image_files)
                test_image = Image.open(os.path.join(test_path, random_file))
                logger.debug(f"Random test image loaded: {random_file}, size={test_image.size}, mode={test_image.mode}")
            else:
                test_image = Image.new('1', (self.display.dp.width, self.display.dp.height), 255)
                logger.debug("No test images found, using blank image")

        self.canvas_create()

        self.text('hewo')

        self.draw_shapes()

        for _ in range(2):
            self.image(test_image, wait=3, aspect_ratio='fit')
            logger.debug("Tested fit mode")

            self.image(test_image, wait=3, aspect_ratio='center')
            logger.debug("Tested center mode")

            self.image(test_image, wait=3, aspect_ratio='stretch')
            logger.debug("Tested stretch mode")

            self.image(test_image, wait=3, aspect_ratio='tile')
            logger.debug("Tested tile mode")

        bmp_for_partial = self.img_manip.to_1b_bmp(test_image)
        self.render_partial(bmp_for_partial, 10)
        logger.debug("Tested partial rendering")

        for _ in range(2):
            bmp = self.img_manip.to_1b_bmp(test_image)
            self.refresh_base(bmp, wait=3)
            logger.debug("Tested refreshing base image")

        self.qr('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 50, 10, 10)
        logger.debug("Tested QR code generation")

        bmp_for_fast = self.img_manip.to_1b_bmp(test_image)
        self.fast_mode([bmp_for_fast for _ in range(10)], wait=1)
        logger.debug("Tested fast mode rendering")
