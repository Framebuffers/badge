import logging
import time
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
            f"Mem: {mem.percent}% ({mem.available / (1024**3):.1f}GB free)",
            f"Disk: {disk.percent}% ({disk.free / (1024**3):.1f}GB free)",
            f"WLAN: {self.get_ip_address()} ({ssh_count} SSH)",
        ]
        return "\n".join(lines)

FONTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'fonts')

if __name__ == "__main__":
    try:
        hs = HealthStatus()
        hs.epd.init()

        dr = DisplayRoutines(hs.epd)
        dr.create_canvas('horizontal')

        # QR code on the left
        ip = hs.get_ip_address()
        qr_url = f"http://{ip}"
        qr_size = dr.dp_width - 8  # Leave 4px margin top/bottom
        dr.create_qr_code(qr_url, qr_size, 4, 4)

        # Text to the right of QR code
        text_x = qr_size + 12  # QR size + margin
        status_text = hs.display_status()
        print(status_text)

        dr.load_txt(status_text)
        dr.display_txt(os.path.join(FONTS_PATH, 'Font.ttc'), 12, 0, text_x, 4)
        dr.render()
    except Exception as e:
        logging.error(f'Error {e}')
    finally:
        epdconfig.module_exit()