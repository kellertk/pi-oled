from typing import List, Union
from luma.core.virtual import snapshot
from .common import ScrollyText
from time import perf_counter
import ifaddr

class ip_address(snapshot):
    def __init__(self, width: int, height: int, update_interval=0.25, scroll_speed=3.0, ip_check_interval=1.0,
                 exclude_adapters: Union[List[str], None] = None):
        self._speed = scroll_speed
        self._ip_address_interval = ip_check_interval
        self.interval = update_interval
        self._last_updated = -update_interval
        self._exclude_adapters = exclude_adapters if exclude_adapters is not None else []
        self._ip_address = self.check_ip_address()
        self._scroller = ScrollyText(self._ip_address, speed=self._speed)
        super(ip_address, self).__init__(width, height, self._scroller.render, self.interval)

    def should_redraw(self):
        _new_ip_address = self.check_ip_address()
        if _new_ip_address != self._ip_address:
            self._ip_address = _new_ip_address
            self._scroller.text = self._ip_address
            return True
        else:
            return super().should_redraw()

    def check_ip_address(self):
        if perf_counter() - self._last_updated > self._ip_address_interval:
            # always exclude loopback adapter
            _adapters = list(filter(lambda e: e.name != 'lo', list(ifaddr.get_adapters())))
            _ips: List[str] = list(filter(lambda e: e is not None,
                                          map(lambda e: str(e.ips[0].ip)
                                              if not any(x in e.name for x in self._exclude_adapters) else None,
                                          _adapters)))
            if len(_ips) > 1:
                return ', '.join(_ips)
            elif len(_ips) == 1:
                return _ips[0]
            else:
                return "No IP Address"
        elif self._ip_address is not None:
            return str(self._ip_address)
        else:
            return "No IP Address"

    def paste_into(self, image, xy):
        super(ip_address, self).paste_into(image, xy)
        self._last_updated = perf_counter()
