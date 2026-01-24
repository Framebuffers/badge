import time
from ..hw import EPD, epdconfig
from .routines import DisplayRoutines

if __name__ == "__main__":
    try:
        epd = EPD()
        routines = DisplayRoutines(epd)
        epd.Clear(0xFF)
        routines.show_text('Shutting down...')
        time.sleep(5)
        epd.Clear(0xFF)
        epd.sleep()
        epdconfig.module_exit()
    except Exception as e:
        routines.write_exception(e)
    finally:
        epd.Clear(0xFF)
        epd.sleep()
        epdconfig.module_exit()