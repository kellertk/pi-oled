from typing import Tuple
from luma.core.virtual import snapshot
from time import perf_counter
from .common import ScrollyText
import subprocess as sp
import re

class ntp(snapshot):
    def __init__(self, width: int, height: int, update_interval=5, scroll_speed=3.0):
        self.interval = update_interval
        self._speed = scroll_speed
        self._last_updated = -update_interval
        self.width = width
        self.height = height
        self._status = self.get_status()
        self._scroller = ScrollyText(self.format(), speed=self._speed)
        super(ntp, self).__init__(self.width, self.height, self._scroller.render, self.interval)

    @property
    def stratum(self):
        return self._status[0]
    @property
    def refid(self):
        return self._status[1]

    def should_redraw(self):
        _new_status = self.get_status()
        if _new_status != self._status:
            self._status = _new_status
            self._scroller.text = self.format()
            return True
        else:
            return super().should_redraw()

    def get_status(self) -> Tuple[int, str]:
        try: self._status
        except AttributeError: return (16, ".INIT.")
        if perf_counter() - self._last_updated > self.interval:
            # update status
            stratum = sp.getoutput('ntpq -c "rv 0 stratum"')
            refid = sp.getoutput('ntpq -c "rv 0 refid"')
            return (int(re.findall(r'\d', stratum)[0]), re.split('=', refid)[1])
        else:
            return self._status

    def format(self) -> str:
        return f"S: {self.stratum:2} REF: {self.refid} "

    def paste_into(self, image, xy):
        super(ntp, self).paste_into(image, xy)
        self._last_updated = perf_counter()
