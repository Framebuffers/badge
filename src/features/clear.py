import logging
import os
import signal
import time

import psutil

from ..hw import EPD, epdconfig
from .routines import DisplayRoutines


def kill_display_processes():
    """Kill other processes using the SPI display so we can take over GPIO."""
    current_pid = os.getpid()
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.pid == current_pid:
            continue
        try:
            for f in proc.open_files():
                if '/dev/spidev' in f.path:
                    logging.info(f"Killing process {proc.pid} ({proc.name()}) using {f.path}")
                    os.kill(proc.pid, signal.SIGTERM)
                    proc.wait(timeout=5)
                    killed.append(proc.pid)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except psutil.TimeoutExpired:
            logging.warning(f"Process {proc.pid} did not exit, sending SIGKILL")
            os.kill(proc.pid, signal.SIGKILL)
            killed.append(proc.pid)
    if killed:
        logging.info(f"Killed {len(killed)} process(es) using the display: {killed}")
        time.sleep(1)  # wait for GPIO release
