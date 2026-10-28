from board import D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, NEOPIXEL, A0, A1, A2, A3, A4, A5, I2C
from time import sleep, monotonic
from digitalio import DigitalInOut, Direction
import analogio
import pulseio
import pwmio
import neopixel
import touchio
from adafruit_motor.servo import Servo as AdaServo
from audiocore import WaveFile
from audioio import AudioOut
from audiomixer import Mixer
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
from adafruit_bitmap_font import bitmap_font

def wait(seconds):
    sleep(seconds)

def colorWheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

class OLED:
    """
    supports basic use of 1306 OLD display with the displayio library
    see https://learn.adafruit.com/circuitpython-display-support-using-displayio/introduction
    """

    def __init__(self, height=64, width=128):

        self._font8 = bitmap_font.load_font("lib/fonts/5x8.bdf", displayio.Bitmap)   # small font
                                                                                 # medium font is built-in
        self._font15 = bitmap_font.load_font("lib/fonts/9x15.bdf", displayio.Bitmap) # lasrge font

        displayio.release_displays()

        i2c = I2C()  # uses board.SCL and board.SDA
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

        self._display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=width, height=height)
        self._width = width
        self._height = height
        self._display.auto_refresh = False

        self._display.root_group = displayio.Group()
        self.clear()

    def clear(self):
        # remove all layers from the display_root Group (seems like there should be an easier way)
        for _ in range(len(self._display.root_group)):
            self._display.root_group.pop()
        # Create a new black bitmap and clear the display
        color_bitmap = displayio.Bitmap(self._width, self._height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self._display.root_group.append(bg_sprite)

    def draw_text(self, row, col, text, size="medium", scale=1):

        text = str(text)

        if size == 8 or size == "small":
            font = self._font8
        elif size == 12 or size == "medium":
            font = terminalio.FONT
        elif size == 15 or size == "large":
            font = self._font15
        else:
            raise ValueError("font size can only be small, medium, or large - you can also use scale")

        text_area = label.Label(font, text=text, scale=scale, color=0xFFFFFF, x=col, y=row)
        text_area.anchor_point = (0.0, 0.0)
        text_area.anchored_position = (col, row)
        self._display.root_group.append(text_area)

    def draw_rect(self, row, col, width=1, height=1):
        color_bitmap = displayio.Bitmap(width, height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=col, y=row)
        self._display.root_group.append(bg_sprite)

    def show(self):
        self._display.refresh()

class AudioFile:
    """
    plays a .wav (or maybe .mp3) file to a headphone jack
    https://learn.adafruit.com/circuitpython-essentials/circuitpython-audio-out
    """

    def __init__(self, pin):
        self._audio = AudioOut(pin)

    def play(self, file):
        self._audio.stop()
        wav_file = open(file, "rb")
        self._wave = WaveFile(wav_file)
        #self._mixer = Mixer(voice_count=1, sample_rate=self._wave.sample_rate, channel_count=self._wave.channel_count, bits_per_sample=self._wave.bits_per_sample, samples_signed=True)
        self._audio.play(self._wave)
        #self._audio.play(self._mixer)
        #self._mixer.voice[0].level = .5
        #self._mixer.voice[0].play(self._wave)
        #while self._audio.playing:
        #    pass
        #self._mixer.deinit()
        #self._audio.deinit()

    def pause(self):
        self._audio.pause()

    def resume(self):
        self._audio.resume()

    def stop(self):
        self._audio.stop()
        self._audio.deinit()

    @property
    def playing(self) -> bool:
        """
        Gets the current playing satatus for this Audio Output
        """
        return self._audio.playing

class DigitalOutput:
    """
    Allows a True/False on/off behavior on a pin
    """

    def __init__(self, pin):
        """
        Constructs a digital output on a pin

        Keyword arguments:
        pin -- the pin controlling the output.  Can be any pin
        """
        self._pin = DigitalInOut(pin)
        self._pin.direction =   Direction.OUTPUT

    @property
    def value(self) -> bool:
        """
        Gets the current setting for this digital output
        """
        return self._pin.value

    @value.setter
    def value(self, value: bool):
        self._pin.value = value


class AnalogOutput:
    """
    Allows an analog behavior on a pin
    """

    # A0 is true analog out
    # A2-A5 and D0-D13 are PWM
    # Not available for pin A1

    def __init__(self, pin):
        """
        Constructs an analog output on a pin

        Keyword arguments:
        pin -- the analog output pin.  A0 is true analog out, all other pins (even digital) are PWM. Not available on A1
        """
        self._pin = pin
        if pin == A1:
            raise ValueError("Analog output is not supported on pin metro.A1.  Use a different pin.")
        elif pin == A0:
            self._out = analogio.AnalogOut(pin)  # true analog out only on pin A0
        else:
            self._out = pwmio.PWMOut(pin, frequency=5000, duty_cycle=0)

    @property
    def value(self) -> int:
        """
        Gets the current setting for this analog output (0 - 65535)
        """
        return self._pin.value

    @value.setter
    def value(self, value: int):
        """
        Sets the current setting for this analog output  (0 - 65535)
        """
        if self._pin == A0:
            self._out.value = int(value)
        else:
            self._out.duty_cycle = int(value)


class Buzzer:
    """
    Models a piezo buzzer
    """

    def __init__(self, pin):
        """
        Constructs a piezo object

        Keyword arguments:
        pin -- the pin controlling the piezo.  Can be any digital pin or analog pin A2 through A5
        """
        if pin == A0 or pin == A1:
            raise ValueError("Piezo buzzers are not supported on pins metro.A0 or metro.A1.  Use a different pin")
        self._pin = pwmio.PWMOut(pin, duty_cycle=2 ** 15, variable_frequency=True)
        self.frequency = 0

    @property
    def frequency(self):
        """
        Returns the current frequency of the piezo buzzer
        """
        return self._pin.frequency

    @frequency.setter
    def frequency(self, value):
        """
        Sets the frequency of this piezo
        """
        if (value == 0):
            self._pin.duty_cycle = 0
        else:
            self._pin.duty_cycle = 2 ** 15
            self._pin.frequency = int(value)


class PixelStrip:
    """
    Models a PixelStrip - uses neopixel library from adafruit
    """

    def __init__(self, pin, num_pixels: int = 6, brightness: float = 0.3, auto_write: bool = True):
        """
        Constructs an LED strip instance

        Keyword arguments:
        pin -- the pin used for the control pin (D0)
        num_pixels -- the number of pixels in the LED strip
        brightness -- overall strip brightness (0.0 off - 1.0 full brightness)
        auto_write -- whether or not to update entire strip when any pixel is changed (True) or wait for .show() (False)
        """
        self._pix = neopixel.NeoPixel(pin, num_pixels, brightness=brightness, auto_write=auto_write)

    def fill(self, r, g: int = 0, b: int = 0):
        """Fills an LED strip with the same color

        Keyword arguments:
        r -- red value (0 - 255) or an rgb tuple (r, g, b)
        g -- green value (0 - 255)
        b - blue value
        """
        if type(r) == tuple:
            self._pix.fill(r)
        else:
            self._pix.fill((r, g, b))

    def set_pixel(self, pixel_num: int, r, g: int = 0, b: int = 0):
        if type(r) == tuple:
            self._pix[pixel_num] = r
        else:
            self._pix[pixel_num] = (r, g, b)

    def show(self) -> None:
        self._pix.show()

class PixelGrid:
    """
    Models a pixel grid
    """
    def __init__(self, pin, num_rows: int = 8, num_cols: int = 32, brightness: float = 0.3, auto_write: bool = False, row_major=False):

        self._grid = PixelStrip(pin, num_rows*num_cols, brightness, auto_write)
        self._num_cols = num_cols
        self._num_rows = num_rows
        self._row_major = row_major
        self._font8 = bitmap_font.load_font("lib/fonts/5x8.bdf", displayio.Bitmap)

    def _to_index(self, r, c):
        if self._row_major:
         # even rows go forward, odd rows go backward
            if r % 2 == 0:
                return r * self._num_cols + c
            else:
                return r * self._num_cols + (self._num_cols - c - 1)
        else:
            if c % 2 == 0:
                return c * self._num_rows + r
            else:
                return c * self._num_rows + (self._num_rows - r - 1)

    def fill(self, r, g: int = 0, b: int = 0):
        """Fills an LED grid with the same color

        Keyword arguments:
        r -- red value (0 - 255) or an rgb tuple (r, g, b)
        g -- green value (0 - 255)
        b - blue value
        """

        self._grid.fill(r, g, b)

    def set_pixel(self, row, col, r, g: int = 0, b: int = 0):
        self._grid.set_pixel(self._to_index(row, col), r, g, b)

    def draw_text(self, row, col, text, r, g=0, b=0):

        text = str(text)

        # use space character to get char height and width

        height = self._font8.get_glyph(32).height
        width = self._font8.get_glyph(32).width

        # loop through all chars in text to draw
        for char in text:

            glyph = self._font8.get_glyph(ord(char))

            for char_row in range(height):
                for char_col in range(width):
                    if glyph.bitmap[width*glyph.tile_index + char_col, char_row] == 1:
                        pix_row = row + char_row
                        pix_col = col + char_col
                        if pix_row < self._num_rows and pix_col < self._num_cols:
                            self._grid.set_pixel(self._to_index(pix_row, pix_col), r, g, b)

            col += width

    def draw_rect(self, top, left, width, height, r, g, b):
        for row in range(top, top+height):
            for col in range(left, left+width):
                self.set_pixel(row, col, r, g, b)

    def show(self):
        self._grid.show()

class Servo:
    """
    Models a positional servo
    """

    # pin can be any digital or analog A2-A5
    def __init__(self, pin):
        """
        Constructs a positional servo object

        Keyword arguments:
        pin -- the pin controlling the servo.  Can be any digital pin or analog pin A2 through A5
        """
        if pin == A0 or pin == A1:
            raise ValueError(
                "Servos can only be controlled with a digital pin or analog pins A2 through A5.  Use a different pin.")
        pwm = pwmio.PWMOut(pin, duty_cycle=2 ** 15, frequency=50)
        self._servo = AdaServo(pwm)

    @property
    def angle(self) -> float:
        """
        Gets the current angle from the servo
        """
        return self._servo.angle

    @angle.setter
    def angle(self, angle: float):
        """
        Rotates the servo to the specified angle - 0 - 180

        Keyword arguments:
        angle -- the angle to set the servo to 0 - 180
        """
        self._servo.angle = angle
        sleep(0.05)


#  Inputs

class DigitalInput:
    """
    Allows a True/False on/off behavior on a pin
    """

    def __init__(self, pin):
        """
        Constructs a digital input on a pin

        Keyword arguments:
        pin -- the pin controlling the servo.  Can be any pin
        """
        self._pin = DigitalInOut(pin)
        self._pin.direction =   Direction.INPUT

    @property
    def value(self) -> bool:
        """
        Gets the current setting for this digital output
        """
        return self._pin.value


class TouchSensor:
    """
    Allows capacitive touch on a pin
    """

    def __init__(self, pin):
        """
        Constructs a digital output on a pin

        Keyword arguments:
        pin -- the pin controlling the servo.  Must be an analog pin
        """
        self._touch = touchio.TouchIn(pin)

    @property
    def touched(self) -> bool:
        """
        Gets the current setting for this digital output
        """
        return self._touch.value


class AnalogInput:
    """
    Constructs an analog output on a pin

    Keyword arguments:
    pin -- the analog output pin.  A0 is true analog out, all other pins (even digital) are PWM. Not available on A1
    """

    def __init__(self, pin):
        self._in = analogio.AnalogIn(pin)

    @property
    def value(self) -> int:
        """
        Gets the current setting for this analog output (0 - 65535)
        """
        return self._in.value


class DistanceSensor:
    """
    Models an HCSR04 distance sensor
    """
    # "https://github.com/adafruit/Adafruit_CircuitPython_HCSR04.git"
    """
    sonar = metro.DistanceSensor(metro.D5, metro.D6)
    while True:
        print(sonar.distance)
        wait(0.1)
    """

    def __init__(self, trigger_pin, echo_pin, timeout=0.1):
        self._timeout = timeout
        self._trig = DigitalInOut(trigger_pin)
        self._trig.direction = Direction.OUTPUT

        self._echo = pulseio.PulseIn(echo_pin)
        self._echo.pause()
        self._echo.clear()

    def __enter__(self):
        """Allows for use in context managers."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically de-initialize after a context manager."""
        self.deinit()

    def deinit(self):
        """De-initialize the trigger and echo pins."""
        self._trig.deinit()
        self._echo.deinit()

    @property
    def distance(self):
        """the distance measured by the sensor in cm. or -1.0 if timeout """

        self._echo.clear()  # Discard any previous pulse values
        self._trig.value = True  # Set trig high
        sleep(0.00001)  # 10 micro seconds 10/1000/1000
        self._trig.value = False  # Set trig low

        pulselen = None
        timestamp = monotonic()
        self._echo.resume()
        while not self._echo:
            # Wait for a pulse
            if (monotonic() - timestamp) > self._timeout:
                self._echo.pause()
                return -1.0
        self._echo.pause()
        pulselen = self._echo[0]

        # positive pulse time, in seconds, times 340 meters/sec, then
        # divided by 2 gives meters. Multiply by 100 for cm
        # 1/1000000 s/us * 340 m/s * 100 cm/m * 2 = 0.017
        return pulselen * 0.017
