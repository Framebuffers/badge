import os
import logging
import time

from hw import EPD, epdconfig
from features import DisplayRoutines
from PIL import Image

FILENAME = 'doggo.bmp'
IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')

logging.basicConfig(level=logging.DEBUG)

try:
    epd = EPD()
    logging.info('init display')
    epd.init()
    logging.info('loaded routines & clear')
    ext = DisplayRoutines(epd)
    epd.Clear()
    
    doggo_image = Image.open(os.path.join(IMG_PATH, FILENAME))
    ext.create_canvas('horizontal')
    ext.load_txt('hello world')
    ext.display_txt(os.path.join(IMG_PATH, FILENAME),
                    20, 0, 10, 10)
    # epd.display(epd.getbuffer(doggo_image))
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

