import argparse
import logging
import os
import sys
import time

from PIL import Image

from .hw import EPD, epdconfig
from .features import DisplayRoutines, DisplayTests, HealthStatus, startup
from .features.clear import kill_display_processes

TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'img', 'test')


def cmd_text(args, display, **_):
    display.show_text(args.message, size=args.size, justify=args.justify)


def cmd_message(args, display, **_):
    display.write_message(args.message, src=args.title, show_datetime=not args.no_datetime)


def cmd_qr(args, display, **_):
    display.create_canvas('horizontal')
    qr_size = min(display.dp_width, display.dp_height) - 8
    if args.size:
        qr_size = args.size
    display.create_qr_code(args.data, qr_size, 4, 4, rotate=not args.no_rotate)
    display.render()


def cmd_image(args, display, **_):
    img = Image.open(args.path)
    display.load_img_scaled(img, aspect_ratio=args.mode)
    display.render()


def cmd_two_columns(args, display, **_):
    left_type = args.left_type
    right_type = args.right_type

    left = _resolve_content(args.left, left_type)
    right = _resolve_content(args.right, right_type)

    display.show_two_columns(
        left, right,
        left_type=left_type, right_type=right_type,
        divider=not args.no_divider,
    )


def _resolve_content(value, content_type):
    if content_type == 'image':
        return Image.open(value)
    return value


def cmd_status(args, health, display, **_):
    status_text = health.display_status()
    display.show_text(status_text)


def cmd_status_loop(args, health, display, **_):
    interval = args.interval
    text_x = startup.initial_render(health, display)
    last_ip = health.get_ip_address()
    try:
        while True:
            time.sleep(interval)
            current_ip = health.get_ip_address()
            if current_ip != last_ip:
                logging.info(f"IP changed: {last_ip} -> {current_ip}")
                text_x = startup.initial_render(health, display)
                last_ip = current_ip
            else:
                startup.update_text(health, display, text_x)
    except KeyboardInterrupt:
        logging.info("Stopped by user")


def cmd_shapes(args, test, **_):
    test.draw_shapes(args.count, clear_canvas=True, refresh=True)


def cmd_clear(args, display, **_):
    display.dp.Clear()


def cmd_test(args, test, **_):
    test.run_all()


def build_parser():
    parser = argparse.ArgumentParser(prog='badge', description='Badge e-ink display CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    # text
    p = sub.add_parser('text', help='Display text on screen')
    p.add_argument('message', help='Text to display')
    p.add_argument('--size', type=int, default=12, help='Font size (default: 12)')
    p.add_argument('--justify', action='store_true', help='Justify text')

    # message
    p = sub.add_parser('message', help='Formatted message with header/timestamp')
    p.add_argument('message', help='Message body')
    p.add_argument('--title', default='Message', help='Header title (default: Message)')
    p.add_argument('--no-datetime', action='store_true', help='Omit timestamp from header')

    # qr
    p = sub.add_parser('qr', help='Generate and display a QR code')
    p.add_argument('data', help='Data to encode')
    p.add_argument('--size', type=int, default=None, help='QR code size in pixels')
    p.add_argument('--no-rotate', action='store_true', help='Do not rotate QR 90 degrees')

    # image
    p = sub.add_parser('image', help='Show an image file')
    p.add_argument('path', help='Path to image file')
    p.add_argument('--mode', choices=['fit', 'stretch', 'center', 'tile'], default='fit',
                   help='Scaling mode (default: fit)')

    # two-columns
    p = sub.add_parser('two-columns', help='Two-column layout')
    p.add_argument('left', help='Left column content (text/URL or image path)')
    p.add_argument('right', help='Right column content (text/URL or image path)')
    p.add_argument('--left-type', choices=['text', 'qr', 'image'], default='text',
                   help='Left content type (default: text)')
    p.add_argument('--right-type', choices=['text', 'qr', 'image'], default='text',
                   help='Right content type (default: text)')
    p.add_argument('--no-divider', action='store_true', help='Hide column divider')

    # status
    sub.add_parser('status', help='Show system health status')

    # status-loop
    p = sub.add_parser('status-loop', help='QR + status cycling loop')
    p.add_argument('--interval', type=int, default=30, help='Refresh interval in seconds (default: 30)')

    # shapes
    p = sub.add_parser('shapes', help='Draw random shapes')
    p.add_argument('--count', type=int, default=5, help='Iterations (default: 5)')

    # clear
    sub.add_parser('clear', help='Clear the display')

    # test
    sub.add_parser('test', help='Run full display test suite')

    return parser


COMMANDS = {
    'text': cmd_text,
    'message': cmd_message,
    'qr': cmd_qr,
    'image': cmd_image,
    'two-columns': cmd_two_columns,
    'status': cmd_status,
    'status-loop': cmd_status_loop,
    'shapes': cmd_shapes,
    'clear': cmd_clear,
    'test': cmd_test,
}


def main():
    logging.basicConfig(level=logging.INFO)
    parser = build_parser()
    args = parser.parse_args()

    kill_display_processes()

    epd = EPD()
    epd.init()
    display = DisplayRoutines(epd)
    test = DisplayTests(display)
    health = HealthStatus()

    try:
        handler = COMMANDS[args.command]
        handler(args, display=display, test=test, health=health)
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
        epd.Clear()
    except Exception as e:
        logging.error(f"Error: {e}")
        display.write_exception(e)
        time.sleep(5)
        epd.Clear()
    finally:
        epdconfig.module_exit()


if __name__ == '__main__':
    main()
