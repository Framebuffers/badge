import os
import logging
import time

from hw import EPD, epdconfig
from features import DisplayRoutines
from PIL import Image

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')

logging.basicConfig(level=logging.DEBUG)

def test_text(display: DisplayRoutines, text: str, wait: int = 5) -> None:
    logging.info(f'loading text: {text}')
    display.load_txt(text)
    display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)
    display.render()
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')
  
def test_image(display: DisplayRoutines, img, wait: int = 5, aspect_ratio: str = 'fit'):
    img_resized = Image.new('1', (display.dp.width, display.dp.height), 255)
    
    if aspect_ratio == 'fit':
        img.thumbnail((display.dp.width, display.dp.height))
        x = (display.dp.width - img.width) // 2
        y = (display.dp.height - img.height) // 2
        img_resized.paste(img, (x, y))
    else:
        img_resized = img.resize((display.dp.width, display.dp.height))
        
    display._image = img_resized
    display.render()
    logging.debug("Rendered image")
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')

def test_canvas_create(display: DisplayRoutines, orientation: str = 'horizontal'):
    logging.debug(f'Creating canvas, orientation: {orientation}')
    display.create_canvas(orientation)
    logging.debug(f"Image exists: {display._image is not None}, Draw exists: {display._draw is not None}")

def test_qr(display: DisplayRoutines, text: str, size, x, y, wait: int = 5):
    display.create_qr_code(text, size, x, y)
    logging.debug("QR code created on canvas")
    if display._image:
        logging.debug(f"Canvas size: {display._image.size}, mode: {display._image.mode}")
        display._image.save('debug_qr_canvas.bmp')
        logging.debug("Canvas saved to debug_qr_canvas.bmp")
    ext.render()
    logging.debug("Rendered QR code")
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')

def img_to_bmp(img: Image.Image, epd: EPD) -> Image.Image:
    logging.debug("Converting image to 1-bit BMP format")
    img_1b = img.convert('1')  # Convert to 1-bit pixels, black and white
    img_resized = img_1b.resize((epd.width, epd.height)) # type: ignore
    logging.debug("Conversion and resizing complete")
    return img_resized

try:
    epd = EPD()
    logging.info('init display')
    epd.init()
    
    logging.info('loaded routines & clear')
    ext = DisplayRoutines(epd)
    
    test_canvas_create(ext)
    test_text(ext, 'hewo')
    
    for img in os.listdir(os.path.join(IMG_PATH, 'test')):
        if img.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg')):
            img_path = os.path.join(IMG_PATH, 'test', img)
            logging.info(f'Testing image: {img_path}')
            image = Image.open(img_path)
            bmp_image = img_to_bmp(image, epd)
            test_image(ext, bmp_image, wait=3)

    test_qr(ext, 'https://https://www.youtube.com/watch?v=dQw4w9WgXcQ', 50, 10, 10)
   
    epd.Clear(0xFF)
    logging.debug("Display cleared")
    epdconfig.module_exit()
    
except FileNotFoundError:
    logging.error(f'File not found')
    epdconfig.module_exit()
except Exception as e:
    logging.error(f'Error: {e}')
    epdconfig.module_exit()
except KeyboardInterrupt:
    logging.info('interrupted by user')
    epdconfig.module_exit()
  