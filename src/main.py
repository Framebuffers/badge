import os
import logging
import time

from hw import EPD, epdconfig
from features import DisplayRoutines
from PIL import Image

FILENAME = 'doggo.bmp'
IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')

logging.basicConfig(level=logging.DEBUG)

try:
    epd = EPD()
    logging.info('init display')
    epd.init()
    logging.info('loaded routines & clear')
    ext = DisplayRoutines(epd)
    ext.create_canvas('horizontal')
    logging.debug(f"Image exists: {ext._image is not None}, Draw exists: {ext._draw is not None}")

    doggo_image = Image.open(os.path.join(IMG_PATH, FILENAME))
    ext.load_txt('y so soff and squishy????????')
    ext.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)

    ext.load_img(doggo_image)
    ext.render()
    logging.debug("Rendered doggo + text")
    time.sleep(2)

    ext.clear_canvas()
    logging.debug("Canvas cleared")

    ext.create_qr_code('https://https://www.youtube.com/watch?v=dQw4w9WgXcQ', 50, 10, 10)
    logging.debug("QR code created on canvas")

    if ext._image:
        logging.debug(f"Canvas size: {ext._image.size}, mode: {ext._image.mode}")
        ext._image.save('debug_qr_canvas.bmp')
        logging.debug("Canvas saved to debug_qr_canvas.bmp")

    ext.render()
    logging.debug("Rendered QR code")
    time.sleep(2)

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

