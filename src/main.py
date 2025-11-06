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
    ext.load_txt('hello world')
    ext.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)
    
    ext.load_img(doggo_image)
    ext.render()
    time.sleep(5)
    epd.Clear(0xFF)

    epd.sleep()
    
except FileNotFoundError:
    logging.error(f'{FILENAME} not found')
    epdconfig.module_exit()
except Exception as e:
    logging.error(f'Error: {e}')
    epdconfig.module_exit()
except KeyboardInterrupt:
    logging.info('interrupted by user')
    epdconfig.module_exit()

