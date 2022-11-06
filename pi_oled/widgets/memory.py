from luma.core.virtual import snapshot
from .common import HorizontalBarGauge
from psutil import virtual_memory
from time import perf_counter

class memory(snapshot):
    def __init__(self, width: int, height: int, label='M', update_interval=1.0):
        self.interval = update_interval
        self._last_updated = -update_interval
        self._usage = self.check_mem_usage()
        self._bar = HorizontalBarGauge(label, max=self._usage[1])
        self._bar.update(self._usage[0])
        super(memory, self).__init__(width, height, self._bar.render, self.interval)

    def should_redraw(self):
        _new_mem = self.check_mem_usage()
        if _new_mem != self._usage:
            self._usage = _new_mem
            self._bar.update(self._usage[0])
            return True
        else:
            return super(memory, self).should_redraw()

    def check_mem_usage(self):
        if perf_counter() - self._last_updated > self.interval:
            memory = virtual_memory()
            # (used, total), in megs
            return (memory[3] / 1048576, memory[0] / 1048576)
        else:
            return self._usage

    def paste_into(self, image, xy):
        super(memory, self).paste_into(image, xy)
        self._last_updated = perf_counter()
