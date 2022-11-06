from luma.core.virtual import snapshot
from time import perf_counter
from platform import node
from .common import ScrollyText

class hostname(snapshot):
    def __init__(self, width: int, height: int, update_interval = 0.25, scroll_speed = 3.0, hostname_check_interval = 1.0):
        self._speed = scroll_speed
        self._hostname_interval = hostname_check_interval
        self.interval = update_interval
        self._last_updated = -update_interval
        self._hostname = self.check_hostname()
        self._scroller = ScrollyText(self._hostname, speed=self._speed)
        super(hostname, self).__init__(width, height, self._scroller.render, self.interval)

    def should_redraw(self):
        _new_hostname = self.check_hostname()
        if _new_hostname != self._hostname:
            self._hostname = _new_hostname
            self._scroller.text = self._hostname
            return True
        else:
            return super(hostname, self).should_redraw()

    def check_hostname(self):
        if perf_counter() - self._last_updated > self._hostname_interval:
            return node()
        else:
            return self._hostname

    def paste_into(self, image, xy):
        super(hostname, self).paste_into(image, xy)
        self._last_updated = perf_counter()
