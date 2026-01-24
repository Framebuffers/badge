import logging
from ..hw import EPD
from typing import Literal
from PIL import Image, ImageFont, ImageDraw, ImageFile
import qrcode

class DisplayRoutines:
    def __init__(self, display: EPD) -> None:
        self.dp: EPD = display                                # the e-ink display itself, never null
        self.buffer: str = ''                                 # whatever text to render
        self._image: Image.Image | None = None                # PIL Image
        self._draw: ImageDraw.ImageDraw | None = None         # ImageDraw.Draw instance
        self._refresh_counter: int = 0
        self._fast_mode: bool = False
        self.dp.Clear()
        
    @property
    def dp_height(self) -> int:
        return self.dp.height
    
    @property
    def dp_width(self) -> int:
        return self.dp.width
    
    @property
    def image(self):
        if not self._image:
            raise AttributeError('No image has been loaded.')
        return self._image
    
    @property
    def canvas(self):
        if not self._draw:
            raise AttributeError('There is no instance of ImageDraw canvas to draw to.')
        return self._draw
    
    @property
    def refresh_counter(self) -> int:
        return self._refresh_counter
    
    @property
    def fast_mode(self) -> bool:
        return self._fast_mode
    
    def create_canvas(self, orientation: str = 'horizontal') -> None:
        logging.debug(f"Creating canvas: {orientation}")
        if orientation == 'horizontal':
            self._image = Image.new('1', (self.dp_height, self.dp_width), 255)
        else:
            self._image = Image.new('1', (self.dp_width, self.dp_height), 255)

        self._draw = ImageDraw.Draw(self._image)
        logging.debug(f"Canvas created: image={self._image}, draw={self._draw}")
    
    def load_txt(self, txt: str) -> None:
        self.buffer = txt

    def display_txt(self, font_path: str, size: int, fill: int, x: int, y: int) -> None:
        """Render buffered text at coordinates. fill: 0 (black) or 255 (white)"""
        if not self._draw:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        font = ImageFont.truetype(font_path, size)
        self._draw.text((x, y), self.buffer, font=font, fill=fill)
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, fill: int = 0) -> None:
        """Draw line from (x1,y1) to (x2,y2)"""
        if not self._draw:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        self._draw.line((x1, y1, x2, y2), fill=fill)
    
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, fill: int = None, outline: int = 0) -> None: # type: ignore
        """Draw rectangle from (x1,y1) to (x2,y2)"""
        if not self._draw:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        self._draw.rectangle((x1, y1, x2, y2), fill=fill, outline=outline)
    
    def draw_arc(self, x1: int, y1: int, x2: int, y2: int, start: int = 0, end: int = 360, fill: int = 0) -> None:
        """Draw arc inside bounding box (x1,y1) to (x2,y2) from start to end degrees"""
        if not self._draw:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        self._draw.arc((x1, y1, x2, y2), start, end, fill=fill)
    
    def render(self, fast: bool = False) -> None:
        """Send canvas to display"""
        if not self._image:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        if fast:
            self.set_fast_mode(True)
            self.dp.display_fast(self.dp.getbuffer(self._image))
        else:
            self.dp.display(self.dp.getbuffer(self._image))
    
    def load_img(self, img: ImageFile.ImageFile) -> None:
        self.dp.display(self.dp.getbuffer(img))

    def load_img_scaled(self, img: Image.Image,
                        aspect_ratio: Literal['stretch', 'center', 'fit', 'tile'] = 'fit') -> None:
        """Load image scaled to display dimensions with specified aspect ratio mode.

        Args:
            img: PIL Image to display
            aspect_ratio: How to handle sizing:
                - 'stretch': Fill display, ignore aspect ratio
                - 'center': Center image, crop if larger than display
                - 'fit': Maintain aspect ratio, fit within display bounds
                - 'tile': Repeat image to fill display
        """
        logging.debug(f'Loading image with aspect ratio: {aspect_ratio}')
        result = Image.new('1', (self.dp.width, self.dp.height), 255)

        if aspect_ratio == 'stretch':
            result = img.resize((self.dp.width, self.dp.height))

        elif aspect_ratio == 'center':
            img_cropped = img
            if img.width > self.dp.width or img.height > self.dp.height:
                img_cropped = img.crop((
                    max(0, (img.width - self.dp.width) // 2),
                    max(0, (img.height - self.dp.height) // 2),
                    min(img.width, (img.width + self.dp.width) // 2),
                    min(img.height, (img.height + self.dp.height) // 2)
                ))
            x = max(0, (self.dp.width - img_cropped.width) // 2)
            y = max(0, (self.dp.height - img_cropped.height) // 2)
            result.paste(img_cropped, (x, y))

        elif aspect_ratio == 'fit':
            img_copy = img.copy()
            img_copy.thumbnail((self.dp.width, self.dp.height), Image.Resampling.LANCZOS)
            x = (self.dp.width - img_copy.width) // 2
            y = (self.dp.height - img_copy.height) // 2
            result.paste(img_copy, (x, y))

        elif aspect_ratio == 'tile':
            if img.width == 0 or img.height == 0:
                logging.warning(f"Cannot tile image with 0 dimensions: {img.size}")
            else:
                for y in range(0, self.dp.height, img.height):
                    for x in range(0, self.dp.width, img.width):
                        tile_width = min(img.width, self.dp.width - x)
                        tile_height = min(img.height, self.dp.height - y)
                        result.paste(img.crop((0, 0, tile_width, tile_height)), (x, y))

        self._image = result
        self._draw = ImageDraw.Draw(self._image)
    
    def clear_canvas(self) -> None:
        """Reset canvas to white"""
        if not self._draw or not self._image:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        self.buffer = ''
        self.dp.Clear()
    
    def create_qr_code(self, data: str, size: int, x: int, y: int) -> None:
        """Create QR code at (x, y). Coordinates are top-left corner of QR code."""
        if not self._image:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        if x < 0 or y < 0:
            raise IndexError('QR code position cannot be negative')
        
        if x + size > self._image.width or y + size > self._image.height:
            raise IndexError('QR code overflows canvas boundaries')
        
        qr = qrcode.QRCode(
            box_size=1, 
            border=0,
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST) # type: ignore
        
        self._image.paste(qr_img, (x, y))
        
    def set_fast_mode(self, enabled: bool) -> None:
        if self._refresh_counter >= 5 and enabled:
            self.reset_refresh_counter()
            logging.warning("Five refreseshes reached, performing a full refresh")
        
        self._fast_mode = enabled
        self._refresh_counter += 1
        logging.debug(f"Fast mode set to {enabled}, refresh counter: {self._refresh_counter}")        
    
    def render_partial(self) -> None:
        """Render using fast mode if enabled"""
        if not self._image:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        self.dp.displayPartial(self.dp.getbuffer(self._image))
        self._refresh_counter += 1
    
    def reset_refresh_counter(self) -> None:
        self._refresh_counter = 0
        logging.debug("Refresh counter reset to 0")
        self._fast_mode = False
        self.dp.Clear()
    
    def refresh_base_img(self, img: Image.Image) -> None:
        """Refreshes the base image with the provided one"""
        self.dp.displayPartBaseImage(self.dp.getbuffer(img))