import os
import logging
import time
from typing import Literal, List
from hw import EPD, epdconfig
from features import DisplayRoutines
from PIL import Image, ImageDraw
import random

IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img')
FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')

logging.basicConfig(level=logging.DEBUG)

def test_text(display: DisplayRoutines, text: str, wait: int = 5) -> None:
    logging.info('Testing text input.')
    logging.info(f'loading text: {text}')
    display.load_txt(text)
    display.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'),
                    20, 0, 10, 10)
    display.render()
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')
  
def _change_aspect_ratio(display: DisplayRoutines, img: Image.Image, 
                         aspect_ratio: Literal['stretch', 'center', 'fit', 'tile'] = 'fit') -> Image.Image:

    logging.info(f'Changing aspect ratio: {aspect_ratio}')
    img_resized = Image.new('1', (display.dp.width, display.dp.height), 255)

    if aspect_ratio == 'stretch':
        img_resized = img.resize((display.dp.width, display.dp.height))
        
    elif aspect_ratio == 'center': # if the img is larger than the display, crop
        if img.width > display.dp.width or img.height > display.dp.height:
            img = img.crop((
                max(0, (img.width - display.dp.width) // 2),
                max(0, (img.height - display.dp.height) // 2),
                min(img.width, (img.width + display.dp.width) // 2),
                min(img.height, (img.height + display.dp.height) // 2)
            ))
        
        x = max(0, (display.dp.width - img.width) // 2)
        y = max(0, (display.dp.height - img.height) // 2)
        img_resized.paste(img, (x, y))
        
    elif aspect_ratio == 'fit':
        img_copy = img.copy()  # do not modify the original img
        img_copy.thumbnail((display.dp.width, display.dp.height), Image.Resampling.LANCZOS)
        x = (display.dp.width - img_copy.width) // 2
        y = (display.dp.height - img_copy.height) // 2
        img_resized.paste(img_copy, (x, y))
        
    elif aspect_ratio == 'tile':
        if img.width == 0 or img.height == 0:
            logging.warning(f"Cannot tile image with 0 dimensions: {img.size}")
            return img_resized  # Return blank canvas
        for y in range(0, display.dp.height, img.height):
            for x in range(0, display.dp.width, img.width):
                # if tiles are out of bounds, crop
                tile_width = min(img.width, display.dp.width - x)
                tile_height = min(img.height, display.dp.height - y)
                img_resized.paste(img.crop((0, 0, tile_width, tile_height)), (x, y))
    
    return img_resized

def test_image(display: DisplayRoutines, img: Image.Image, wait: int = 5, 
               aspect_ratio: Literal['stretch', 'center', 'fit', 'tile'] = 'fit'):
    logging.info('Loading image')
    img_resized = _change_aspect_ratio(display, img, aspect_ratio)
     
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
    ext.render()
    logging.debug("Rendered QR code")
    time.sleep(wait)
    display.clear_canvas()
    logging.info('Canvas cleared')

def img_to_bmp(img: Image.Image, epd: EPD) -> Image.Image:
    logging.debug(f"Converting image to 1-bit BMP format. Input size: {img.size}")
    logging.debug(f"Target dimensions: {epd.width}x{epd.height}")
    img_1b = img.convert('1') # 1 == black and white, 1bpp
    target_size = (int(epd.width), int(epd.height))
    img_resized = img_1b.resize(target_size) # type: ignore
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
    logging.info('Testing partial refresh with clock')
    
    # Show background once with full refresh
    display._image = img.copy()
    display.render(fast=False)
    
    start_time = time.time()
    
    for i in range(loops):
        # creates a dedicated area for the text
        draw = ImageDraw.Draw(display._image)
        draw.rectangle((10, 10, 100, 35), fill=255)
        
        elapsed = time.time() - start_time
        display.load_txt(f'{elapsed:.1f}s')
        display.display_txt(
            os.path.join(FONTS_PATH, 'Font.ttc'),
            20,
            0,
            10,
            10
        )
        
        display.render(fast=True)
        logging.debug(f'Clock update {i+1}/{loops}')
        time.sleep(1)
    
    display.clear_canvas()
    logging.info('Test complete')

def test_draw_shapes(display: DisplayRoutines, wait: int = 5):
    random.seed(621)
    display.create_canvas('horizontal')

    for _ in range(10):
        x1_temp = random.randint(0, display.dp_width - 1)
        y1_temp = random.randint(0, display.dp_height - 1)
        x2_temp = random.randint(0, display.dp_width - 1)
        y2_temp = random.randint(0, display.dp_height - 1)

        # Ensure coordinates are in correct order (top-left to bottom-right)
        x1, x2 = min(x1_temp, x2_temp), max(x1_temp, x2_temp)
        y1, y2 = min(y1_temp, y2_temp), max(y1_temp, y2_temp)

        shape_type = random.choice(['line', 'rectangle', 'arc'])

        if shape_type == 'line':
            display.draw_line(x1, y1, x2, y2, fill=random.choice([0, 255]))
        elif shape_type == 'rectangle':
            display.draw_rectangle(x1, y1, x2, y2, fill=128, outline=0)
        else:
            display.draw_arc(x1, y1, x2, y2, start=0, end=180, fill=0)

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
    
    test_path = os.path.join(IMG_PATH, 'test')
    image_files = [f for f in os.listdir(test_path)
               if f.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg'))]

    if image_files:
        random_file = random.choice(image_files)
        random_pic = Image.open(os.path.join(test_path, random_file))
        logging.debug(f"Random test image loaded: {random_file}, size={random_pic.size}, mode={random_pic.mode}")
    else:
        random_pic = Image.new('1', (epd.width, epd.height), 255)
        logging.debug("No test images found, using blank image")
    test_canvas_create(ext)

    # testing drawing text
    test_text(ext, 'hewo')
    
    # testing drawing shapes
    test_draw_shapes(ext)
   
    # testing fit modes    
    for _ in range(2):
        test_image(ext, random_pic, wait=3, aspect_ratio='fit')
        logging.debug("Tested fit mode")
        
        test_image(ext, random_pic, wait=3, aspect_ratio='center')
        logging.debug("Tested center mode")
        test_image(ext, random_pic, wait=3, aspect_ratio='stretch')
        logging.debug("Tested stretch mode")
        
        test_image(ext, random_pic, wait=3, aspect_ratio='tile')
        logging.debug("Tested tile mode")

    # testing partial rendering
    bmp_for_partial = img_to_bmp(random_pic, epd)
    test_render_partial(ext, bmp_for_partial, 10)
    logging.debug("Tested partial rendering")
    
    # test refreshing the base image
    for _ in range(2):
        bmp = img_to_bmp(random_pic, epd)
        test_refresh_base(ext, bmp, wait=3)
        logging.debug("Tested refreshing base image")
     
    # testing QR code generation
    test_qr(ext, 'https://https://www.youtube.com/watch?v=dQw4w9WgXcQ', 50, 10, 10)
    logging.debug("Tested QR code generation")
    
    # testing fast mode
    test_fast_mode(ext, [random_pic for _ in range(10)], wait=1)
    logging.debug("Tested fast mode rendering")
    
    epd.Clear(0xFF)
    logging.debug("Display cleared")
    logging.info('\ndone')
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
  