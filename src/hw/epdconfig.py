import logging
import time
import spidev
import gpiozero

logger = logging.getLogger(__name__)

"""Pin definition:"""
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24
PWR_PIN = 18
MOSI_PIN = 10
SCLK_PIN = 11

"""Global HW instances"""
SPI = None
GPIO_RST_PIN = None
GPIO_DC_PIN = None
GPIO_PWR_PIN = None
GPIO_BUSY_PIN = None


def digital_write(pin, value):
    if pin == RST_PIN:
        GPIO_RST_PIN.on() if value else GPIO_RST_PIN.off() # type: ignore
    elif pin == DC_PIN:
        GPIO_DC_PIN.on() if value else GPIO_DC_PIN.off() # type: ignore
    elif pin == PWR_PIN:
        GPIO_PWR_PIN.on() if value else GPIO_PWR_PIN.off() # type: ignore

def digital_read(pin):
    if pin == BUSY_PIN:
        return GPIO_BUSY_PIN.value # type: ignore
    return 0

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)

def spi_writebyte(data):
    SPI.writebytes(data) # type: ignore

def spi_writebyte2(data):
    SPI.writebytes2(data) # type: ignore

def module_init():
    global SPI, GPIO_RST_PIN, GPIO_DC_PIN, GPIO_PWR_PIN, GPIO_BUSY_PIN
    
    GPIO_RST_PIN = gpiozero.LED(RST_PIN)
    GPIO_DC_PIN = gpiozero.LED(DC_PIN)
    GPIO_PWR_PIN = gpiozero.LED(PWR_PIN)
    GPIO_BUSY_PIN = gpiozero.Button(BUSY_PIN, pull_up=False)
    
    GPIO_PWR_PIN.on()
    
    SPI = spidev.SpiDev()
    SPI.open(0, 0)
    SPI.max_speed_hz = 4000000
    SPI.mode = 0b00
    
    return 0

def module_exit():
    logger.debug("spi end")
    SPI.close() # type: ignore
    
    GPIO_RST_PIN.off() # type: ignore
    GPIO_DC_PIN.off() # type: ignore
    GPIO_PWR_PIN.off() # type: ignore
    logger.debug("close 5V, Module enters 0 power consumption ...")
    
    GPIO_RST_PIN.close() # type: ignore
    GPIO_DC_PIN.close() # type: ignore
    GPIO_PWR_PIN.close() # type: ignore
    GPIO_BUSY_PIN.close() # type: ignore