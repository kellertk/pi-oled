from typing import Union
from PIL import ImageFont, ImageDraw, Image
from pathlib import Path
from luma.core.virtual import viewport
from luma.oled import device

class ScrollyText():
    WAITING_TO_SCROLL = 1
    SCROLLING = 2
    WAITING_TO_REWIND = 3
    REWINDING = 4

    def __init__(self, text: str, font: ImageFont = None, scroll_delay: int = 0, reverse_delay: Union[int, None] = None, speed: int = 1):
        self.text = text
        self.speed = speed
        self.font = font if font is not None else default_font
        self.scroll_delay = scroll_delay
        self.reverse_delay = reverse_delay if reverse_delay is not None else scroll_delay
        self._state = self.WAITING_TO_REWIND
        self._ticks = 0
        self._x_pos = 0

    def tick(self, text_width: int, viewport_width: int):
        if self._state == self.WAITING_TO_SCROLL:
            if not self.is_waiting():
                self._state = self.SCROLLING
        elif self._state == self.SCROLLING:
            if self._x_pos < 0:
                if not self.is_waiting():
                    self._x_pos += self.speed
            else:
                self._state = self.WAITING_TO_REWIND
        elif self._state == self.WAITING_TO_REWIND:
            if not self.is_waiting_to_reverse():
                self._state = self.REWINDING
        elif self._state == self.REWINDING:
            if self._x_pos > -(text_width - viewport_width):
                if not self.is_waiting():
                    self._x_pos -= self.speed
            else:
                self._state = self.WAITING_TO_SCROLL

    def render(self, draw: ImageDraw, width: int, height: int):
        text_width, text_height = draw.textsize(self.text, font=self.font)
        self.tick(text_width, width)
        draw.rectangle((0, 0, width, height), fill='black')
        draw.text((self._x_pos, 0), self.text, 'white', self.font)

    def is_waiting(self):
        self._ticks += 1
        if self._ticks > self.scroll_delay:
            self._ticks = 0
            return False
        return True
    def is_waiting_to_reverse(self):
        self._ticks += 1
        if self._ticks > self.reverse_delay:
            self._ticks = 0
            return False
        return True

class LineGraph():
    def __init__(self, label: str = '', font: ImageFont = None, max: Union[int, None] = None, min = 0, history = 30):
        self.label = label
        self.max = max
        self.min = min
        self.history = history
        self.datapoints = []
        self.update(min)
        self._font = font if font is not None else default_font
        self._historical_max = max

    def update(self, value):
        self.datapoints.append(value)
        if len(self.datapoints) > self.history:
            self.datapoints.pop(0)

    def render(self, draw: ImageDraw, width: int, height: int, x_offset=0):
        # left aligned, vertical bottom text
        label_width, label_height = draw.textsize(self.label, font=self._font)
        draw.text((x_offset, height - label_height - 1), self.label, 'white')
        # outline of graph field
        max_x = width - 1 + x_offset
        max_y = height - 1
        draw.line((label_width + 1, 0, label_width + 1, max_y), fill='white')
        draw.line((label_width + 1, max_y, max_x, max_y), fill='white')
        # bail out here if we have no data
        if len(self.datapoints) == 0: return
        # find ticks per division
        data_width = max_x - label_width
        data_height = max_y
        quantize_x = data_width / len(self.datapoints)
        if self.max is None:
            # implement auto scaling
            self._historical_max = 0 if self._historical_max is None else max(self._historical_max, max(self._datapoints))
            quantize_y = 0 if self._historical_max == 0 else data_height / self._historical_max
        else:
            quantize_y = data_height / self.max
        # plot the values
        last_y = data_height
        last_x = label_width + 1
        for value in self.datapoints:
            draw.line((last_x, last_y, last_x + quantize_x, data_height - (value * quantize_y)), fill='white')
            last_y = data_height - (value * quantize_y)
            last_x = last_x + quantize_x


class viewport_custom(viewport):
    def __init__(self, device: device, width: int, height: int, mode=None,
                 dither=False, backing_image: Union[Image.Image, None] = None):
        super(viewport_custom, self).__init__(device, width, height, mode, dither)
        if backing_image is not None:
            self._backing_image = backing_image

class HorizontalBarGauge():
    def __init__(self, label: str = '', font: ImageFont = None, max = 100, min = 0):
        self.label = label
        self.max = max
        self.min = min
        self.update(min)
        self._font = font if font is not None else default_font

    def update(self, value: int):
        self.value = value
        if value > self.max:
            self.max = value

    def render(self, draw: ImageDraw, width: int, height: int):
        # left aligned, vertical center text
        label_width, label_height = draw.textsize(self.label, font=self._font)
        draw.text((0, (height / 2) - (label_height / 2) - 1 ), self.label, 'white', self._font)
        # outline of bar
        bar_start_x = label_width
        bar_start_y = 0
        bar_end_x = width - 1
        bar_end_y = height - 1
        draw.rectangle((bar_start_x, bar_start_y, bar_end_x, bar_end_y), outline='white', fill='black')
        # fill the bar
        available_width = (width - 2) - (label_width + 1)
        value_percent = float(self.value) / float(self.max)
        value_width = round(available_width * value_percent)
        bar_start_x = bar_start_x + 1
        bar_start_y = bar_start_y + 1
        bar_end_x = bar_start_x + value_width
        bar_end_y = bar_end_y - 1
        draw.rectangle((bar_start_x, bar_start_y, bar_end_x, bar_end_y), outline='white', fill='white')

def make_font(name: str, size):
    font_path = str(Path(__file__).resolve().parent.parent.joinpath('font', name))
    return ImageFont.truetype(font_path, size)

default_font = make_font('PixeloidSans.ttf', 9)
