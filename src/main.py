import os
import logging
import time
from typing import Literal, List
from hw import EPD, epdconfig
from features import DisplayRoutines
from PIL import Image
import random

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')

logging.basicConfig(level=logging.DEBUG)

def test_text(display: DisplayRoutines, text: str, wait: int = 5) -> None:
    logging.info(f'loading text: {text}')
    display.load_txt(text)
    display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)
    display.render()
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')
  
def test_image(display: DisplayRoutines, img, wait: int = 5, aspect_ratio: Literal['stretch', 'center', 'fit', 'tile'] = 'fit'):
    img_resized = Image.new('1', (display.dp.width, display.dp.height), 255)
    
    if aspect_ratio == 'center':
        x = (display.dp.width - img.width) // 2
        y = (display.dp.height - img.height) // 2
        img_resized.paste(img, (x, y))
    if aspect_ratio == 'stretch':
        img_resized = img.resize((display.dp.width, display.dp.height))
    elif aspect_ratio == 'center':
        x = (display.dp.width - img.width) // 2
        y = (display.dp.height - img.height) // 2
        img_resized.paste(img, (x, y))
    elif aspect_ratio == 'fit':
        img.thumbnail((display.dp.width, display.dp.height))
        x = (display.dp.width - img.width) // 2
        y = (display.dp.height - img.height) // 2
        img_resized.paste(img, (x, y))
    elif aspect_ratio == 'tile':
        for x in range(0, display.dp.width, img.width):
            for y in range(0, display.dp.height, img.height):
                img_resized.paste(img, (x, y))
     
    display._image = img_resized
    display.render()
    logging.debug(f"Rendered image, aspect_ratio={aspect_ratio}")
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')

def test_canvas_create(display: DisplayRoutines, orientation: str = 'horizontal'):
    logging.debug(f'Creating canvas, orientation: {orientation}')
    display.create_canvas(orientation)
    logging.debug(f"Image exists: {display._image is not None}, Draw exists: {display._draw is not None}")

def test_qr(display: DisplayRoutines, text: str, size, x, y, wait: int = 5):
    display.create_qr_code(text, size, x, y)
    logging.debug("QR code created on canvas")
    if display._image:
        logging.debug(f"Canvas size: {display._image.size}, mode: {display._image.mode}")
        display._image.save('debug_qr_canvas.bmp')
        logging.debug("Canvas saved to debug_qr_canvas.bmp")
    ext.render()
    logging.debug("Rendered QR code")
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')

def img_to_bmp(img: Image.Image, epd: EPD) -> Image.Image:
    logging.debug("Converting image to 1-bit BMP format")
    img_1b = img.convert('1')  # Convert to 1-bit pixels, black and white
    img_resized = img_1b.resize((epd.width, epd.height)) # type: ignore
    logging.debug("Conversion and resizing complete")
    return img_resized

def test_refresh_base(display: DisplayRoutines, img: Image.Image, wait: int = 5):
    display.refresh_base_img(img)
    logging.debug("Performed partial refresh with new base image")
    time.sleep(wait)

def test_fast_mode(display: DisplayRoutines, img: List[Image.Image], wait: int = 5):
    for i in img:
        logging.debug(f"Fast mode test iteration {i}")
        display._image = i
        display.render(fast=True)
        time.sleep(wait)

def test_render_partial(display: DisplayRoutines, img: Image.Image, loops: int = 5):
    # using a clock to test partial refresh, taking current time and incrementing by a second each loop
    display._image = img
    clock = time.time()
    for _ in range(loops):
        display.load_txt(f'{time.time() - clock:.2f}s')
        display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                        20, 0, 10, 10)
        time.sleep(0.5)
        display.render(fast=True)
    
    display.clear_canvas()
    logging.info('Canvas cleared')

def test_draw_shapes(display: DisplayRoutines, wait: int = 5):
    display.create_canvas('horizontal')
    display.draw_line(10, 10, 200, 10)
    display.draw_rectangle(10, 20, 100, 60, fill=128, outline=0)
    display.draw_arc(120, 20, 200, 100, start=0, end=180, fill=0)
    logging.debug("Shapes drawn on canvas")
    display.render()
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')

try:
    epd = EPD()
    logging.info('init display')
    epd.init()
    
    logging.info('loaded routines & clear')
    ext = DisplayRoutines(epd)
    
    test_canvas_create(ext)
    test_text(ext, 'hewo')
    test_draw_shapes(ext)
    
    random_pic = Image.open(random.choice(os.listdir(os.path.join(IMG_PATH, 'test'))))
    
    # testing fit modes 
    for img in os.listdir(os.path.join(IMG_PATH, 'test')):
        if img.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg')):
            img_path = os.path.join(IMG_PATH, 'test', img)
            logging.info(f'Testing image: {img_path}')
            image = Image.open(img_path)
            bmp_image = img_to_bmp(image, epd)
            test_image(ext, bmp_image, wait=3, aspect_ratio='fit')
            test_image(ext, bmp_image, wait=3, aspect_ratio='center')
            test_image(ext, bmp_image, wait=3, aspect_ratio='stretch')
            test_image(ext, bmp_image, wait=3, aspect_ratio='tile')
            
    # testing partial rendering
    test_render_partial(ext, random_pic, 10)
        
    for img in os.listdir(os.path.join(IMG_PATH, 'test')):
        if img.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg')):
            img_path = os.path.join(IMG_PATH, 'test', img)
            logging.info(f'Testing refresh base image: {img_path}')
            image = Image.open(img_path)
            bmp_image = img_to_bmp(image, epd)
            test_refresh_base(ext, bmp_image, wait=2)        
    
    test_qr(ext, 'https://https://www.youtube.com/watch?v=dQw4w9WgXcQ', 50, 10, 10)
    test_fast_mode(ext, [random_pic for _ in range(10)], wait=1)
    
    epd.Clear(0xFF)
    logging.debug("Display cleared")
    epdconfig.module_exit()
    
except FileNotFoundError:
    logging.error(f'File not found')
    epdconfig.module_exit()
except Exception as e:
    logging.error(f'Error: {e}')
    epdconfig.module_exit()
except KeyboardInterrupt:
    logging.info('interrupted by user')
    epdconfig.module_exit()
  