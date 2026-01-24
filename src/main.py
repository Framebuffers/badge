import os
import logging
import time 
import random
from .hw import EPD, epdconfig
from .features import DisplayRoutines, DisplayTests, HealthStatus
from PIL import Image

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
DEMO_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'demo')

def demo_show_and_tell(display: DisplayRoutines, test: DisplayTests):
    display.clear_canvas()
    display.write_message('wena cabres, bienvenidos a mi presentación', 'top text', False)
    input()
    display.write_message('este es un proyecto que llevo haciendo desde Noviembre del 2025', 'owo what\'s this', False)
    input()
    
    display.show_two_columns('es un badge', '[placeholder]', 'text', 'image', divider=True)
    input()
    display.show_text('puedo hacer cosas como: ')
    input()
    
    hs = HealthStatus()
    
    test_txt = '''According to all known laws of aviation, there is no way a bee should be able to fly.
Its wings are too small to get its fat little body off the ground.
The bee, of course, flies anyway because bees don't care what humans think is impossible.'''
    
    display.write_message(test_txt, 'Bee Movie script')
    time.sleep(3)
    display.clear_canvas()
    test_image = None 

    if test_image is None:
        test_path = os.path.join(IMG_PATH, 'test')
        image_files = [f for f in os.listdir(test_path)
                        if f.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg'))]
        if image_files:
            random_file = random.choice(image_files)
            test_image = Image.open(os.path.join(test_path, random_file))
        else:
            test_image = Image.new('1', (display.dp.width, display.dp.height), 255)
    
    for _ in range(2):
        test.image(test_image, wait=1, aspect_ratio='fit')
        test.image(test_image, wait=1, aspect_ratio='center')
        test.image(test_image, wait=1, aspect_ratio='stretch')
        test.image(test_image, wait=1, aspect_ratio='tile')
    test.image()  

    display.show_two_columns('https://www.youtube.com/watch?v=dQw4w9WgXcQ', test_image, 'qr', 'image')
    time.sleep(3)
    test.draw_shapes(3, False)
    display.show_text('bottom text')
    time.sleep(2)
    display.set_fast_mode(True)
    display.show_text('awoo')
    test.draw_shapes(1, False)
    time.sleep(2)
    test.draw_shapes(2, True)
    
    display.write_message('también puede dar info sobre la RPi en sí')
    input()
    
    hs.display_status()  
    display.clear_canvas()
    display.write_message('eso pos cabres, espero que les haya gustado', 'the end')
    input()
    
    display.show_two_columns('https://github.com/framebuffers/badge', 'Link al código acá', 'qr', 'text')
    display.clear_canvas()
    display.show_text('hasta la proximaaaaaaaa')
    input()
    
logging.basicConfig(level=logging.DEBUG)

display = None
try:
    epd = EPD()
    logging.info('init display')
    epd.init()
    display = DisplayRoutines(epd)
    test = DisplayTests(display)
    demo_show_and_tell(display, test)
except FileNotFoundError:
    logging.error('File not found')
    time.sleep(5)
    epd.Clear()
except KeyboardInterrupt:
    logging.info('interrupted by user')
    time.sleep(5)
    epd.Clear()
except Exception as e:
    logging.error(f'Error: {e}')
    if display:
        display.write_exception(e)
    time.sleep(5)
    epd.Clear()
finally:
    epdconfig.module_exit()

