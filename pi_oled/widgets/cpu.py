from luma.core.virtual import snapshot
from .common import LineGraph
from time import perf_counter
from PIL import ImageDraw
from psutil import cpu_percent

class cpu(snapshot):
    def __init__(self, width: int, height: int, label='C', update_interval=1.0):
        self.interval = update_interval
        self._last_updated = -update_interval
        self._graph = LineGraph(label, max=100)
        self._usage = 0
        super(cpu, self).__init__(width, height, self._graph.render, self.interval)

    def should_redraw(self):
        usage = self.check_cpu_usage()
        if usage is not None:
            self._usage = usage
            self._graph.update(self._usage)
            return True
        else:
            return super(cpu, self).should_redraw()

    def check_cpu_usage(self):
        now = perf_counter()
        if now - self._last_updated > self.interval:
            # can't specify time delta because that makes this call blocking
            usage = cpu_percent(interval=None)
            return usage
        else:
            return None

    def paste_into(self, image, xy):
        super(cpu, self).paste_into(image, xy)
        self._last_updated = perf_counter()


