# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid white
background, a smaller black rectangle, and some white text.
"""

import board, busio, microcontroller
import digitalio, displayio, terminalio
import time
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import keypad
import hx711
import menu

displayio.release_displays()

# Define I2C
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)

## I2C Display
WIDTH = 128
HEIGHT = 32

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.show(splash)

# # Draw boarder
# color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
# color_palette = displayio.Palette(1)
# color_palette[0] = 0xFFFFFF  # White

# bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
# splash.append(bg_sprite)

# # a smaller inner rectangle
# BORDER = 5
# inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
# inner_palette = displayio.Palette(1)
# inner_palette[0] = 0x000000  # Black
# inner_sprite = displayio.TileGrid(
#     inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
# )
# splash.append(inner_sprite)

# Draw a label
text_area = label.Label(
    terminalio.FONT, scale=3, color=0xFFFFFF, x=0, y=HEIGHT // 2 - 1
)
splash.append(text_area)
#display.refresh()

# Led
# led = digitalio.DigitalInOut(board.LED)
# led.direction = digitalio.Direction.OUTPUT

# Keypad
keys = keypad.Keys((board.GP12, board.GP11, board.GP10), value_when_pressed=False, pull=True)

# Sensor
force = hx711.HX711(sda=board.GP1, scl=board.GP0)

# Build Menu

x = 0
def counter():
    global x
    x += 1
    return f"{x}"


def raw():
    v, ok = force.read_raw()
    if ok:
        return f"{v}"
    return "---"


def kg():
    v, ok = force.read()
    if ok:
        return f"{v}"
    return "---"


def tare():
    """
    Zero the scale.
    return message to be displayed
    """
    v, ok = force.read_raw()
    if ok:
        force.offset(v)
        return "OK"
    # force.ratio()
    return "error"


def on_display(string):
    text_area.text = string


mm = menu.MenuManager(on_display, menu.Menu(
    ["raw", "Kg", "tare", "tstcnt"],
    [menu.show(raw), menu.show(kg), menu.enter(menu.Cmd(tare)), menu.show(counter)]))


print("Running - Press Ctrl+C to get into the REPL")
while True:
    time.sleep(0.1)

    force.poll10Hz()

    event = keys.events.get()
    mm.poll10hz(event)

    # temperature = -1
    # if button_a.value:
    #     v, ok = force.read_raw()
    #     if ok:
    #         temperature = v
    # else:
    #     temperature =  round(microcontroller.cpu.temperature,1)
    #     # led.value = False
    #
    # temperature_string = f"{temperature}"
    # text_area.text = temperature_string
    #
    # event = keys.events.get()
    # # event will be None if nothing has happened.
    # if event:
    #     print("key", event.key_number, event.pressed)


