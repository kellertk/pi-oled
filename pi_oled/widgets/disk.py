from luma.core.virtual import snapshot
from .common import HorizontalBarGauge
from shutil import disk_usage
from time import perf_counter

class disk(snapshot):
    def __init__(self, width: int, height: int, label='D', path='/', update_interval=1.0):
        self.interval = update_interval
        self._last_updated = -update_interval
        self.path = path
        self._usage = self.check_disk_usage(self.path)
        self._bar = HorizontalBarGauge(label, max=self._usage[1])
        self._bar.update(self._usage[0])
        super(disk, self).__init__(width, height, self._bar.render, self.interval)

    def should_redraw(self):
        _new_disk = self.check_disk_usage(self.path)
        if _new_disk != self._usage:
            self._usage = _new_disk
            self._bar.max = self._usage[1]
            self._bar.update(self._usage[0])
            return True
        else:
            return super(disk, self).should_redraw()

    def check_disk_usage(self, path):
        if perf_counter() - self._last_updated > self.interval:
            disk = disk_usage(path)
            # (used, total), in megs
            return (disk[1] / 1048576, disk[0] / 1048576)
        else:
            return self._usage

    def paste_into(self, image, xy):
        super(disk, self).paste_into(image, xy)
        self._last_updated = perf_counter()
