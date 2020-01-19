from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

# init 8x8 matrix led
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial)