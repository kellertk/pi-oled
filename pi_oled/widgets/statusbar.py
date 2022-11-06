from typing import Tuple
from luma.core.virtual import snapshot
from time import perf_counter
from psutil import net_if_stats
from PIL import ImageDraw
import subprocess as sp
import re

# Note: This class is Raspberry Pi OS specific. It might not work on other
#       Linux distributions, and it absolutely will not work on Windows.
#       If you update this too fast it will hang the UI.
class statusbar(snapshot):
    def __init__(self, update_interval=5, eth_name: str = 'eth0', wlan_name: str = 'wlan0'):
        self.interval = update_interval
        self._last_updated = -update_interval
        self._eth_name = eth_name
        self._wlan_name = wlan_name
        self._status = self.get_status()
        self._width = 30
        self._height = 10
        super(statusbar, self).__init__(self._width, self._height, self.render, self.interval)

    @property
    def w(self):
        return self._width
    @property
    def h(self):
        return self._height

    def should_redraw(self):
        _new_status = self.get_status()
        if _new_status != self._status:
            self._status = _new_status
            return True
        else:
            return super().should_redraw()

    def get_status(self) -> Tuple[bool, bool, bool]:
        try: self._status
        except AttributeError: return (False, False, False)
        if perf_counter() - self._last_updated > self.interval:
            stats = net_if_stats()
            if stats.get(self._eth_name) is not None:
                eth_connected = True if stats[self._eth_name].isup else False
            else:
                eth_connected = False
            if stats.get(self._wlan_name) is not None:
                wifi_connected = True if stats[self._wlan_name].isup else False
            else:
                wifi_connected = False
            bt_std_out = sp.getoutput('hcitool con')
            bt_connected = True if re.search('(?:\[[:xdigit:]\]{2}([-:]))(?:\[[:xdigit:]\]{2}\\1){4}\[[:xdigit:]\]{2}',
                                             bt_std_out) else False
            return (eth_connected, wifi_connected, bt_connected)
        else:
            return self._status

    def paste_into(self, image, xy):
        super(statusbar, self).paste_into(image, xy)
        self._last_updated = perf_counter()

    def render(self, draw: ImageDraw, width: int, height: int):
        # Draw ethernet icon
        draw.rectangle((2, 1, 6, 3), fill='black', outline='white')
        draw.line((4, 4, 4, 6), fill='white')
        draw.line((1, 5, 7, 5), fill='white')
        draw.line((1, 5, 1, 6), fill='white')
        draw.line((7, 5, 7, 6), fill='white')
        draw.rectangle((0, 7, 1, 8), fill='white')
        draw.rectangle((3, 7, 5, 8), fill='white')
        draw.rectangle((7, 7, 8, 8), fill='white')
        # Draw wifi icon
        draw.line((15, 7, 15, 7), fill='white')
        draw.line((13, 6, 13, 6), fill='white')
        draw.line((17, 6, 17, 6), fill='white')
        draw.line((14, 5, 16, 5), fill='white')
        draw.line((11, 4, 11, 4), fill='white')
        draw.line((19, 4, 19, 4), fill='white')
        draw.line((12, 3, 12, 3), fill='white')
        draw.line((18, 3, 18, 3), fill='white')
        draw.line((13, 2, 17, 2), fill='white')
        # Draw bluetooth icon
        draw.line((24, 3, 26, 5), fill='white')
        draw.line((24, 7, 26, 5), fill='white')
        draw.line((26, 1, 26, 9), fill='white')
        draw.line((27, 1, 29, 3), fill='white')
        draw.line((27, 5, 29, 3), fill='white')
        draw.line((27, 5, 29, 7), fill='white')
        draw.line((27, 9, 29, 7), fill='white')
        eth, wifi, bt = self._status
        if not eth:
            draw.line((0, 9, 9, 1), fill='white')
            draw.line((9, 9, 0, 1), fill='white')
        if not wifi:
            draw.line((10, 9, 20, 1), fill='white')
            draw.line((20, 9, 10, 1), fill='white')
        if not bt:
            draw.line((21, 9, 30, 1), fill='white')
            draw.line((30, 9, 21, 1), fill='white')
        return draw
