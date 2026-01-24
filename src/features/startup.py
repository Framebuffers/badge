import logging
import time
import psutil # type: ignore
import os
from ..hw import EPD, epdconfig

class HealthStatus:
    def __init__(self) -> None:
        self.epd = EPD()

    def get_cpu_temp(self):
        try:
            temp_output = os.popen("vcgencmd measure_temp").readline()
            return temp_output.replace("temp=", "").strip()
        except:
            return "N/A"
    
    def display_status(self):

        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 30)

        # CPU
        print(f"CPU Load: {psutil.cpu_percent(interval=1)}%")
        print(f"CPU Temperature: {self.get_cpu_temp()}")

        # Memory
        mem = psutil.virtual_memory()
        print(f"Memory Usage: {mem.percent}%")
        print(f"Total Memory: {mem.total / (1024**3):.2f} GB")
        print(f"Available Memory: {mem.available / (1024**3):.2f} GB")

        # Disk
        disk = psutil.disk_usage('/')
        print(f"Disk Usage: {disk.percent}%")
        print(f"Total Disk Space: {disk.total / (1024**3):.2f} GB")

try:
    hs = HealthStatus()
    hs.display_status()
    time.sleep(2)
    hs.epd.Clear(0xFF)
        
except Exception as e:
    logging.error(f'Error {e}')