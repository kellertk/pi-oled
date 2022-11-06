import time
from sys import maxsize
from pathlib import Path
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import ImageDraw, Image
from pi_oled.widgets.statusbar import statusbar

from pi_oled.widgets.common import viewport_custom
from pi_oled.widgets.ip_address import ip_address
from pi_oled.widgets.hostname import hostname
from pi_oled.widgets.memory import memory
from pi_oled.widgets.disk import disk
from pi_oled.widgets.netbps import netbps
from pi_oled.widgets.cpu import cpu

# ------- main

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, height=32, rotate=0)

# Create widgets
host = hostname(64, 9)
ip = ip_address(94, 9)
status = statusbar()
mem_graph = memory(62, 4)
disk_graph = disk(62, 4, label='/:')
network_graph = netbps(62, 8, label='N')
cpu_graph = cpu(64, 8, label='C')

# Add static elements to viewport
backing_image = Image.new(device.mode, device.size)
backing_lines = ImageDraw.Draw(backing_image)
lines = [(0, 21, 127, 21), (0, 8, 64, 8), (64, 8, 64, 21), (95, 21, 95, 31)]
for l in lines:
    backing_lines.line(l, fill="white", width=1)

# Compose viewport
virtual = viewport_custom(device, device.width, device.height, backing_image=backing_image)
virtual.add_hotspot(host, (0, 10))
virtual.add_hotspot(ip, (0, 23))
virtual.add_hotspot(status, (97, 22))
virtual.add_hotspot(mem_graph, (66, 15))
virtual.add_hotspot(disk_graph, (66, 10))
virtual.add_hotspot(network_graph, (66, 0))
virtual.add_hotspot(cpu_graph, (0, 0))

try:
    while True:
        virtual.refresh()
        # A reasonable maximum framerate is 30fps, or 33.3̅ms per frame
        # Actual framerate will be (sum(widget render time) + 33.3̅ms) * 60
        time.sleep((33 + 1/3)/1000)
except KeyboardInterrupt:
    pass
finally:
    device.cleanup()
