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


# Display
splash = displayio.Group()
text_area = label.Label(
    terminalio.FONT, scale=3, color=0xFFFFFF, x=0, y=HEIGHT // 2 - 1
)
splash.append(text_area)
display.show(splash)


def on_display(string):
    text_area.text = string


# Keypad
keys = keypad.Keys((board.GP12, board.GP11, board.GP10), value_when_pressed=False, pull=True)

# Sensor
force = hx711.HX711(sda=board.GP1, scl=board.GP0)

# Menu
x = 0
def counter() -> str:
    """
    Running counter value (for testing).
    :return: ever incrementing value.
    """
    global x
    x += 1
    return f"{x}"


def raw() -> str:
    """
    Display load cell readings.
    :return: raw load cell value.
    """
    v, ok = force.read_raw()
    if ok:
        return f"{v}"
    return "---"


def kg() -> str:
    """
    Display tension in kg.
    :return: load cell tension in kg.
    """
    v, ok = force.read()
    if ok:
        return f"{v}"
    return "---"


def tare() -> str:
    """
    Zero the scale.
    return message to be displayed
    """
    v, ok = force.read_raw()
    if ok:
        force.offset(v)
        return "OK"
    # TODO set force.ratio() ?
    return "error"


mm = menu.MenuManager(on_display, menu.Menu(
    ["raw", "Kg", "tare", "tst cnt"],
    [menu.show(raw), menu.show(kg), menu.enter(menu.Cmd(tare)), menu.show(counter)]))


print("Running - Press Ctrl+C to get into the REPL")
while True:
    time.sleep(0.1)

    force.poll10Hz()

    event = keys.events.get()
    mm.poll10hz(event)


