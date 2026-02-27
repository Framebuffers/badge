import logging
import time
import signal
import sys
import psutil # type: ignore
import os
import pwd
import socket
import subprocess
from ..hw import EPD, epdconfig
from .routines import DisplayRoutines

class HealthStatus:
    def __init__(self) -> None:
        self.epd = EPD()

    def get_cpu_temp(self) -> str:
        try:
            temp_output = os.popen("vcgencmd measure_temp").readline()
            return temp_output.replace("temp=", "").strip()
        except:
            return "N/A"

    def get_hostname(self):
        try:
            return socket.gethostname()
        except Exception as e:
            return (f'An exception has been raised while trying to get hostname: {e}')
        
    def get_user(self):
        try:
            return pwd.getpwuid(os.getuid()).pw_name
        except Exception as e:
            return "N/A"
        
    def get_kernel_version(self):
        try:
            result = subprocess.run(["uname", "-r"], capture_output=True, text=True, check=True)
            kernel_version = result.stdout.strip()
            return kernel_version
        except Exception as e:
             return (f'An exception has been raised while trying to get hostname: {e}')
    
    def get_wifi_info(self) -> tuple[str, str]:
        """Returns (SSID, signal_strength) or ('N/A', 'N/A') if not connected."""
        try:
            ssid = os.popen("iwgetid -r").readline().strip()
            if not ssid:
                return ("Not connected", "N/A")

            # Get signal strength from /proc/net/wireless
            with open("/proc/net/wireless", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    # Format: Interface | status | link | level | noise | ...
                    parts = lines[2].split()
                    if len(parts) >= 3:
                        # level is in dBm, convert to percentage (rough estimate)
                        level = int(float(parts[3]))
                        # dBm typically ranges from -30 (excellent) to -90 (poor)
                        percentage = min(100, max(0, 2 * (level + 100)))
                        return (ssid, f"{percentage}% ({level}dBm)")
            return (ssid, "N/A")
        except:
            return ("N/A", "N/A")

    def get_ssh_connections(self) -> int:
        """Returns the number of active SSH connections."""
        try:
            connections = [
                conn for conn in psutil.net_connections(kind='tcp')
                if conn.laddr.port == 22 and conn.status == 'ESTABLISHED'
            ]
            return len(connections)
        except:
            return 0

    def get_ip_address(self) -> str:
        """Returns the primary IP address."""
        try:
            # Connect to a public DNS to determine outbound IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "N/A"

    def display_status(self) -> str:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        ssh_count = self.get_ssh_connections()

        lines = [
            time.strftime('%Y-%m-%d %H:%M:%S'),
            "-" * 26,
            f"{self.get_user()}@{self.get_hostname()} ",
            f"CPU: {psutil.cpu_percent(interval=1)}% {self.get_cpu_temp()}",
            f"Mem: {mem.percent}% ({mem.available / (1024**3):.1f}GB)",
            f"Disk: {disk.percent}% ({disk.free / (1024**3):.1f}GB)",
            f"{self.get_ip_address()} ({ssh_count} SSH)",
        ]
        return "\n".join(lines)

FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'fonts')

def initial_render(hs: HealthStatus, dr: DisplayRoutines) -> int:
    """Full render with QR on top, status below. Returns text_y offset."""
    dr.create_canvas('vertical')

    # QR code on top
    ip = hs.get_ip_address()
    qr_url = f"http://{ip}"
    qr_size = dr.dp_width - 8
    dr.create_qr_code(qr_url, qr_size, 4, 4)

    # Status text below QR
    text_y = qr_size + 12
    status_text = hs.display_status()
    print(status_text)

    dr.load_txt(status_text)
    dr.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'), 12, 0, 4, text_y)
    dr.render(fast=False)  # Full refresh

    return text_y


def update_text(hs: HealthStatus, dr: DisplayRoutines, text_y: int) -> None:
    """Partial refresh for text area only."""
    # Clear text area below QR (white rectangle, no outline)
    dr.draw_rectangle(0, text_y, dr.dp_width, dr.dp_height, fill=255, outline=255)

    # Redraw text
    status_text = hs.display_status()
    print(status_text)

    dr.load_txt(status_text)
    dr.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'), 12, 0, 4, text_y)
    dr.render(fast=True)  # Partial refresh


if __name__ == "__main__":
    REFRESH_INTERVAL = 30  # seconds

    def shutdown_handler(signum, frame):
        """Handle SIGTERM from systemd shutdown."""
        logging.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        hs = HealthStatus()
        hs.epd.init()
        dr = DisplayRoutines(hs.epd)

        # Initial full render with QR code
        text_x = initial_render(hs, dr)
        last_ip = hs.get_ip_address()

        # Subsequent refreshes
        while True:
            time.sleep(REFRESH_INTERVAL)
            current_ip = hs.get_ip_address()

            if current_ip != last_ip:
                # IP changed, full refresh with new QR code
                logging.info(f"IP changed: {last_ip} -> {current_ip}")
                text_x = initial_render(hs, dr)
                last_ip = current_ip
            else:
                # Same IP, partial refresh text only
                update_text(hs, dr, text_x)

    except KeyboardInterrupt:
        logging.info("Stopped by user")
    except Exception as e:
        logging.error(f'Error {e}')
        dr.write_exception(e)
    finally:
        logging.info("Clearing display...")
        hs.epd.Clear(0xFF)
        hs.epd.sleep()
        epdconfig.module_exit()