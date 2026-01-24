import os
import logging
import time 

from .hw import EPD, epdconfig
from .features import DisplayRoutines, DisplayTests, HealthStatus

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')

logging.basicConfig(level=logging.DEBUG)

try:
    epd = EPD()
    logging.info('init display')
    epd.init()

    logging.info('loaded routines & clear')
    display = DisplayRoutines(epd)

    # tests = DisplayTests(display)
    # tests.run_all()

    hs = HealthStatus()
    display.show_text(hs.display_status())
    time.sleep(4)
    epd.Clear(0xFF)
    logging.debug("Display cleared")
    logging.info('\ndone')

except FileNotFoundError:
    logging.error('File not found')
except KeyboardInterrupt:
    logging.info('interrupted by user')
except Exception as e:
    logging.error(f'Error: {e}')
    display.write_exception(e)
finally:
    epdconfig.module_exit()
