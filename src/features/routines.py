import logging
import os
import textwrap
import time
from ..hw import EPD
from typing import Literal
from PIL import Image, ImageFont, ImageDraw, ImageFile
import qrcode

DEFAULT_FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'fonts', 'Font.ttc')

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
   
    def _text_justify(self, s: str, width: int = 64) -> list[str]:
        lines = s.splitlines()
        result = []
        for l in lines:
            if len(l) < width:
                result.append(l)
            else:
                breaks = textwrap.wrap( l, width, replace_whitespace=False, break_long_words=True, break_on_hyphens=False )
                for b in breaks[:-1]:
                    if len(b) == width:
                        result.append(b)
                        continue
                    insert = width-len(b)
                    words = b.split()
                    every = insert // (len(words)-1) + 1
                    extra = insert % (len(words)-1)
                    for i in range(extra):
                        words[i] += ' '
                    result.append( (' '*every).join(words) )
                result.append( breaks[-1] )
        return result
    
    def load_txt(self, txt: str) -> None:
        self.buffer = txt

    def display_txt(self, font_path: str, size: int, fill: int, x: int, y: int, justify: bool = True, justify_at: int = 32) -> None:
        """Render buffered text at coordinates. fill: 0 (black) or 255 (white)"""
        if not self._draw:
            raise RuntimeError('Canvas not created. Call create_canvas() first')
        
        font = ImageFont.truetype(font_path, size)
        if justify:
            str_buffer_justified = self._text_justify(self.buffer, justify_at)
            txt = '\n'.join(str_buffer_justified)
        else:
            txt = self.buffer

        self._draw.text((x, y), txt, font=font, fill=fill)

    def show_text(self, text: str, size: int = 12, x: int = 4, y: int = 4,
                  orientation: str = 'horizontal', font_path: str | None = None, justify: bool = False,
                  justify_length: int = 32) -> None:
        """Display text on screen with automatic canvas management.

        Args:
            text: Text to display
            size: Font size (default 12)
            x, y: Position (default 4, 4)
            orientation: 'horizontal' or 'vertical' (default 'horizontal')
            font_path: Path to font file (default uses Font.ttc)
            justify: Justify the text
            justify_length: Split words at this amount of characters. Default is 32.
        """
        self.create_canvas(orientation)
        self.load_txt(text)
        self.display_txt(font_path or DEFAULT_FONT, size, 0, x, y, justify, justify_length)
        self.render()

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

    def write_message(self, msg: str, src: str = 'Message', show_datetime: bool = True,
                      justify: bool = True, justify_at: int = 32) -> None:
        """Display message on screen in a standardised format."""
        logging.info(f"Displaying on-screen a message from {src}: {msg}")
        header = f"{src} at {time.strftime('%Y-%m-%d %H:%M:%S')}:" if show_datetime else f"{src}:"
        lines = [
            header,
            "-" * 25,
        ] + self._text_justify(msg, justify_at)
        txt = '\n'.join(lines)
        self.show_text(txt, justify=justify, justify_length=justify_at)

    def write_exception(self, e: Exception) -> None:
        """Display an exception on screen in a standardised format."""
        logging.error(f"Exception occurred: {e}", exc_info=True)
        error_lines = [
            f"An error has occurred at {time.strftime('%Y-%m-%d %H:%M:%S')}:",
            "-" * 25,
        ] + self._text_justify(str(e), 32)
        txt = '\n'.join(error_lines)
        logging.debug(f"Displaying exception on screen:\n{txt}")
        self.show_text(txt, justify=True, justify_length=32)

    def print(self, title: str, content: str | Exception, show_datetime: bool = True,
              justify: bool = True, justify_at: int = 32) -> None:
        """Unified method to display messages or exceptions on screen."""
        if isinstance(content, Exception):
            self.write_exception(content)
        else:
            self.write_message(content, title, show_datetime, justify, justify_at)

    def show_two_columns(self, left_content: str | Image.Image, right_content: str | Image.Image,
                         left_type: Literal['text', 'qr', 'image'] = 'text',
                         right_type: Literal['text', 'qr', 'image'] = 'text',
                         size: int = 12, font_path: str | None = None,
                         divider: bool = True) -> None:
        """Display content in two columns with optional divider.

        Args:
            left_content: Content for left column (str for text/qr, Image for image)
            right_content: Content for right column (str for text/qr, Image for image)
            left_type: Type of left content - 'text', 'qr', or 'image'
            right_type: Type of right content - 'text', 'qr', or 'image'
            size: Font size for text (default 12)
            font_path: Path to font file (default uses Font.ttc)
            divider: Whether to draw a vertical line between columns (default True)
        """
        self.create_canvas('horizontal')
        mid_x = self.dp_height // 2
        col_width = (mid_x - 8) // (size // 2)  # approx chars per column
        col_height = self.dp_width

        # Left column
        self._render_column_content(left_content, left_type, 4, 4, mid_x - 8, col_height,
                                    size, font_path, col_width)

        # Right column
        self._render_column_content(right_content, right_type, mid_x + 4, 4, mid_x - 8, col_height,
                                    size, font_path, col_width)

        if divider:
            self.draw_line(mid_x, 0, mid_x, self.dp_width)

        self.render()

    def _render_column_content(self, content: str | Image.Image,
                               content_type: Literal['text', 'qr', 'image'],
                               x: int, y: int, width: int, height: int,
                               size: int, font_path: str | None, col_width: int) -> None:
        """Render content within a column region."""
        if content_type == 'text':
            if not isinstance(content, str):
                raise TypeError('Content must be str for text type')
            self.load_txt(content)
            self.display_txt(font_path or DEFAULT_FONT, size, 0, x, y, justify=True, justify_at=col_width)

        elif content_type == 'qr':
            if not isinstance(content, str):
                raise TypeError('Content must be str for qr type')
            qr_size = min(width, height - y)
            self.create_qr_code(content, qr_size, x, y)

        elif content_type == 'image':
            if not isinstance(content, Image.Image):
                raise TypeError('Content must be PIL Image for image type')
            img_copy = content.copy()
            img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
            if img_copy.mode != '1':
                img_copy = img_copy.convert('1')
            self._image.paste(img_copy, (x, y))