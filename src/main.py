import logging
import time
from lib import EPD, epdconfig
from PIL import Image

FILENAME = 'doggo.bmp'
logging.basicConfig(level=logging.DEBUG)

try:
    epd = EPD()
    logging.info('loading doggo picture')
    epd.init()
    epd.Clear()
    
    doggo_image = Image.open(FILENAME)
    epd.display(epd.getbuffer(doggo_image))
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