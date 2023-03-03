import digitalio


class HX711:
    """
    Driver for HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales

    Datasheet: https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf

    :param sda string: Data input pin name.
    :param scl string: Clock output pin name.
    :param config int: Gain/channel setting for ADC readings. Defaults to :const:`1`
    :param offset int: Offset to apply to ADC readings. Defaults to :const:`0`
    :param ratio float: Ratio to convert ADC reading to desired unit. Defaults to :const:`1`
    """

    def __init__(self, sda, scl, config: int = 1, offset: int = 0, ratio: int = 1):
        self._io_data = digitalio.DigitalInOut(sda)
        self._io_data.direction = digitalio.Direction.INPUT
        self._io_data.pull = digitalio.Pull.UP

        self._io_clk = digitalio.DigitalInOut(scl)
        self._io_clk.direction = digitalio.Direction.OUTPUT

        self._config = config
        self._offset = offset
        self._ratio = ratio
        self._queue = []
    
    QUEUE_SIZE = const(5)
    
    def offset(self, offset: int) -> None:
        """:param offset: Offset to apply to ADC readings."""
        self._offset = offset

    def ratio(self, ratio: int) -> None:
        """:param ratio: Ratio to convert ADC reading to desired unit."""
        self._ratio = ratio

    def config(self, config: int) -> None:
        """Config the HX711 channel and gain.
        :param config:
            value   chan    gain    diff input voltage for full scale
            1       A       128     +/- 20mV
            2       B       32      +/- 80mV
            3       A       64      +/- 40mV
        """
        if config < 1 or config > 3:
            raise ValueError()

        self._config = config
    
    def poll10Hz(self):
        """Poll10Hz should be called 10 times per second to do internal processing."""
        if self._io_data.value:
            # no data available
            return

        d = 0
        for _ in range(24 + self._config):
            self._io_clk.value = True
            self._io_clk.value = False
            d = d << 1 | self._io_data.value
        # discard config bits
        d = d >> self._config

        # extend sign of 24bits 2-complements value
        if d > 0x7FFFFF:
            d -= 0x1000000

        self._queue.append(d)

        if len(self._queue) > QUEUE_SIZE:
            self._queue.pop(0)

    def read_raw(self) -> Tuple[int, bool]:
        """
        Raw returns the sensor value averaged over last N samples.
        :return:
        """
        if len(self._queue) < QUEUE_SIZE:
            return 0, False

        r = 0
        for v in self._queue:
            r += v

        r /= len(self._queue)

        return r, True

    def read(self) -> Tuple[float, bool]:
        """Return scaled  the average of last N raw values."""
        v, ok = self.read_raw()
        r = (v - self._offset) / self._ratio

        return r, ok