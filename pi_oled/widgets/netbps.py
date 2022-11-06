from luma.core.virtual import snapshot
from .common import LineGraph
from time import perf_counter
from psutil import net_io_counters
from PIL import ImageDraw, Image

class netbps(snapshot):
    def __init__(self, width: int, height: int, label='N', update_interval=1.0):
        self.interval = update_interval
        self._last_updated = -update_interval
        io = net_io_counters() # sent, recv in bytes
        self._usage = (io[0], io[1])
        self._rate = (0, 0)
        self._graph_out = LineGraph()
        self._graph_in = LineGraph(label)
        self._graph_out.update(0)
        self._graph_in.update(0)
        # storing 2 graphs means we need a draw object that we manage ourselves
        self._image_in = Image.new('1', (width, height))
        self._image_out = Image.new('1', (width, height))
        self._draw_in = ImageDraw.Draw(self._image_in)
        self._draw_out = ImageDraw.Draw(self._image_out)
        self._label_width = self._draw_in.textsize(label, font=self._graph_in._font)[0] - 2
        # also need to track historical max values for each graph, to sync them
        self._max_val = 0
        super(netbps, self).__init__(width, height, self.dual_render, self.interval)

    def should_redraw(self):
        rate = self.check_net_usage()
        if rate is not None:
            self._rate = rate
            self._graph_out.update(self._rate[0])
            self._graph_in.update(self._rate[1])
            return True
        else:
            return super(netbps, self).should_redraw()

    def check_net_usage(self):
        now = perf_counter()
        if now - self._last_updated > self.interval:
            io = net_io_counters()
            # slightly complicated, need to get rate per perf_counter interval,
            # which means we must track the last perf_counter time
            time_delta = int(now - self._last_updated)
            sent_rate = (io[0] - self._usage[0]) / time_delta
            recv_rate = (io[1] - self._usage[1]) / time_delta
            self._usage = (io[0], io[1])
            return (sent_rate, recv_rate)
        else:
            return None

    def paste_into(self, image, xy):
        super(netbps, self).paste_into(image, xy)
        self._last_updated = perf_counter()

    def dual_render(self, draw: ImageDraw, width: int, height: int):
        # Rescale the graphs
        self._max_val = max(self._max_val, max(self._graph_out.datapoints), max(self._graph_in.datapoints))
        self._graph_in.max = self._max_val
        self._graph_out.max = self._max_val
        # First render the graphs into our images
        self._draw_in.rectangle((0, 0, int(width/2 + self._label_width), height), outline=0, fill=0)
        self._draw_out.rectangle((0, 0, int(width/2 - self._label_width), height), outline=0, fill=0)
        self._graph_in.render(self._draw_in, int(width/2 + self._label_width), height)
        self._graph_out.render(self._draw_out, int(width/2 - self._label_width), height)
        # Now combine the images into the draw object
        draw.bitmap((0, 0), self._image_in, fill=1)
        draw.bitmap((int(width/2 + self._label_width + 1), 0), self._image_out, fill=1)
