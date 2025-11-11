import os
import logging
import time

from hw import EPD, epdconfig
from features import DisplayRoutines
from PIL import Image

FILENAME = 'doggo.bmp'
IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
DOGGO_IMG = Image.open(os.path.join(IMG_PATH, FILENAME))

logging.basicConfig(level=logging.DEBUG)

def test_text(display: DisplayRoutines, text: str, wait: int = 5) -> None:
    logging.info(f'loading text: {text}')
    display.load_txt(text)
    display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')
  
def test_image(display: DisplayRoutines, img, wait: int = 5):
    display.load_img(img)
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
    """Convert image to 1-bit BMP format suitable for e-ink displays."""
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
    test_image(ext, DOGGO_IMG)
    logging.info(f'loading text:')

    ext.load_txt('owo')
    ext.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)
    time.sleep(5)
    ext.clear_canvas()
    
    # ext.load_txt('test')
    # ext.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
    #                 20, 0, 10, 10)
    # time.sleep(5)
    # ext.clear_canvas()

    
    test_text(ext, 'hewwo owo')
    test_qr(ext, 'https://https://www.youtube.com/watch?v=dQw4w9WgXcQ', 50, 10, 10)
    
    for img in os.listdir(IMG_PATH):
        if img.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg')):
            img_path = os.path.join(IMG_PATH, img)
            logging.info(f'Testing image: {img_path}')
            image = Image.open(img_path)
            bmp_image = img_to_bmp(image, epd)
            test_image(ext, bmp_image, wait=3)
            
    epd.Clear(0xFF)
    logging.debug("Display cleared")
    epdconfig.module_exit()
    
except FileNotFoundError:
    logging.error(f'{FILENAME} not found')
    epdconfig.module_exit()
except Exception as e:
    logging.error(f'Error: {e}')
    epdconfig.module_exit()
except KeyboardInterrupt:
    logging.info('interrupted by user')
    epdconfig.module_exit()


  