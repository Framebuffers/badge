import sys
import os
import logging
import epd2in13b_V4
from PIL import Image,ImageDraw,ImageFont
import traceback

filename = 'doggo.bmp'
logging.basicConfig(level=logging.DEBUG)

try:
    logging.info('loading doggo picture')
    epd.init()
    epd.Clear()

    doggoimage = Image.open(filename)
    epd.display(epd.getbuffer(doggoimage))
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info('interrupting...')
    epd2in13b_V4.epdconfig.module_exit(cleanup=True)
    exit()