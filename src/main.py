import sys
import os
import logging
import traceback
import time

from eink.epd2in13_V4 import epd2in13_V4
from eink.epdconfig import epdconfig
from PIL import Image,ImageDraw,ImageFont

filename = 'doggo.bmp'
logging.basicConfig(level=logging.DEBUG)

try:
    epd = epd2in13_V4.EPD()
    logging.info('loading doggo picture')
    epd.init()
    epd.Clear()

    doggoimage = Image.open(filename)
    epd.display(epd.getbuffer(doggoimage))
    time.sleep(5)
    epd.Clear(0xFF)
    epdconfig.module_exit(cleanup=True)
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info('interrupting...')
    epdconfig.module_exit(cleanup=True)
    exit()
