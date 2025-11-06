import os
from ..hw.epd import EPD
from PIL import Image, ImageFont
from PIL.ImageDraw import ImageDraw

class DisplayRoutines:
    def __init__(self, display: EPD) -> None:
        self.dp: EPD = display                      # the e-ink display itself, never null
        self.buffer: str = ''                       # whatever text to render
        self._image: Image.Image | None = None      # PIL Image
        self._draw: ImageDraw | None = None         # ImageDraw.Draw instance

    @property
    def dp_height(self) -> int:
        return self.dp.height
    
    @property
    def dp_width(self) -> int:
        return self.dp.width
    
    @property
    def image(self):
        if self._image is None:
            raise AttributeError('No image has been loaded.')
        return self._image
    
    @property
    def canvas(self):
        if self._draw is None:
            raise AttributeError('There is no instance of ImageDraw canvas to draw to.')
        return self._draw
    
    def create_canvas(self, orientation: str = 'horizontal') -> None:
        if orientation == 'horizontal':
            self._image = Image.new('1', (self.dp_height, self.dp_width), 255)
        else:
            self._image = Image.new('1', (self.dp_height, self.dp_width), 255)
    
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
    
    def render(self) -> None:
        """Send canvas to display"""
        if not self._image:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        self.dp.display(self.dp.getbuffer(self._image))
    
    def clear_canvas(self) -> None:
        """Reset canvas to white"""
        if self._image:
            self._draw.rectangle((0, 0, self._image.width, self._image.height), fill=255) # type: ignore