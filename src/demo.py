import os
import logging
import time
from .hw import EPD, epdconfig
from .features import DisplayRoutines, DisplayTests, HealthStatus, startup
from .features.clear import kill_display_processes
from PIL import Image

BADGE_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'badge.png')
FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
DEFAULT_FONT = os.path.join(FONTS_PATH, 'Font.ttc')

def demo(display: DisplayRoutines, test: DisplayTests, health: HealthStatus):
    badge_img = Image.open(BADGE_IMG_PATH)

    # 1 — Show the badge image full-screen (fit)
    test.image(badge_img, wait=3, aspect_ratio='fit')

    # 2 — Two-column: badge image + repo QR
    display.show_two_columns(
        'https://github.com/framebuffers/badge',
        badge_img,
        'qr', 'image',
        divider=True
    )
    time.sleep(3)

    # 3 — System health status
    display.dp.Clear()
    startup.initial_render(health, display)
    time.sleep(3)

    # 4 — Image scaling modes
    display.dp.Clear()
    for mode in ('fit', 'center', 'stretch', 'tile'):
        test.image(badge_img, wait=2, aspect_ratio=mode)

    # 5 — Fast-mode shapes
    display.set_fast_mode(True)
    display.create_canvas('vertical')
    display.load_txt('demo mode — random shapes')
    display.display_txt(DEFAULT_FONT, 12, 0, 4, 4)
    test.draw_shapes(3, False, False)
    display.render()
    time.sleep(2)

    # 6 — QR code with label
    display.dp.Clear()
    display.show_two_columns(
        'https://github.com/framebuffers/badge',
        'framebuffers/badge',
        'qr', 'text'
    )
    time.sleep(3)

    display.dp.Clear()

logging.basicConfig(level=logging.DEBUG)

display = None
try:
    kill_display_processes()
    epd = EPD()
    logging.info('init display')
    epd.init()
    display = DisplayRoutines(epd)
    test = DisplayTests(display)
    health = HealthStatus()
    demo(display, test, health)
except KeyboardInterrupt:
    logging.info('interrupted by user')
except Exception as e:
    logging.error(f'Error: {e}')
    if display:
        display.write_exception(e)
    time.sleep(5)
finally:
    if display:
        display.dp.Clear()
    epdconfig.module_exit()
