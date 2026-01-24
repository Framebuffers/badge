import logging
import time
import psutil # type: ignore
import os
from ..hw import EPD, epdconfig
from .routines import DisplayRoutines

class HealthStatus:
    def __init__(self) -> None:
        self.epd = EPD()

    def get_cpu_temp(self):
        try:
            temp_output = os.popen("vcgencmd measure_temp").readline()
            return temp_output.replace("temp=", "").strip()
        except:
            return "N/A"
    
    def display_status(self) -> str:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        lines = [
            time.strftime('%Y-%m-%d %H:%M:%S'),
            "-" * 26,
            f"CPU: {psutil.cpu_percent(interval=1)}% {self.get_cpu_temp()}",
            f"Mem: {mem.percent}% ({mem.available / (1024**3):.1f}GB free)",
            f"Disk: {disk.percent}% ({disk.free / (1024**3):.1f}GB free)",
        ]
        return "\n".join(lines)

FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')

try:
    hs = HealthStatus()
    hs.epd.init()

    dr = DisplayRoutines(hs.epd)
    dr.create_canvas('horizontal')

    status_text = hs.display_status()
    print(status_text)

    dr.load_txt(status_text)
    dr.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'), 12, 0, 4, 4)
    dr.render()

    time.sleep(5)
    hs.epd.Clear(0xFF)
except Exception as e:
    logging.error(f'Error {e}')
finally:
    epdconfig.module_exit()