##
 #  @filename   :   epd7in5.py
 #  @brief      :   Implements for Dual-color e-paper library
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     July 10 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 #

from . import epdif
from PIL import Image
import RPi.GPIO as GPIO

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

# EPD7IN5 commands
PANEL_SETTING                               = 0x00
POWER_SETTING                               = 0x01
POWER_OFF                                   = 0x02
POWER_OFF_SEQUENCE_SETTING                  = 0x03
POWER_ON                                    = 0x04
POWER_ON_MEASURE                            = 0x05
BOOSTER_SOFT_START                          = 0x06
DEEP_SLEEP                                  = 0x07
DATA_START_TRANSMISSION_1                   = 0x10
DATA_STOP                                   = 0x11
DISPLAY_REFRESH                             = 0x12
DATA_START_TRANSMISSION_2                   = 0x13
LUT_FOR_VCOM                                = 0x20
LUT_BLUE                                    = 0x21
LUT_WHITE                                   = 0x22
LUT_GRAY_1                                  = 0x23
LUT_GRAY_2                                  = 0x24
LUT_RED_0                                   = 0x25
LUT_RED_1                                   = 0x26
LUT_RED_2                                   = 0x27
LUT_RED_3                                   = 0x28
LUT_XON                                     = 0x29
PLL_CONTROL                                 = 0x30
TEMPERATURE_SENSOR_COMMAND                  = 0x40
TEMPERATURE_CALIBRATION                     = 0x41
TEMPERATURE_SENSOR_WRITE                    = 0x42
TEMPERATURE_SENSOR_READ                     = 0x43
VCOM_AND_DATA_INTERVAL_SETTING              = 0x50
LOW_POWER_DETECTION                         = 0x51
TCON_SETTING                                = 0x60
TCON_RESOLUTION                             = 0x61
SPI_FLASH_CONTROL                           = 0x65
REVISION                                    = 0x70
GET_STATUS                                  = 0x71
AUTO_MEASUREMENT_VCOM                       = 0x80
READ_VCOM_VALUE                             = 0x81
VCM_DC_SETTING                              = 0x82

class EPD:
    def __init__(self):
        self.reset_pin = epdif.RST_PIN
        self.dc_pin = epdif.DC_PIN
        self.busy_pin = epdif.BUSY_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def digital_write(self, pin, value):
        epdif.epd_digital_write(pin, value)

    def digital_read(self, pin):
        return epdif.epd_digital_read(pin)

    def delay_ms(self, delaytime):
        epdif.epd_delay_ms(delaytime)

    def send_command(self, command):
        self.digital_write(self.dc_pin, GPIO.LOW)
        # the parameter type is list but not int
        # so use [command] instead of command
        epdif.spi_transfer([command])

    def send_data(self, data):
        self.digital_write(self.dc_pin, GPIO.HIGH)
        # the parameter type is list but not int
        # so use [data] instead of data
        epdif.spi_transfer([data])

    def init(self):
        if (epdif.epd_init() != 0):
            return -1
        print("Initialization begin")
        self.reset()
        self.send_command(POWER_SETTING)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x3f)
        self.send_data(0x3f)

        print("Power on")
        self.send_command(POWER_ON)
        self.wait_until_idle()

        self.send_command(PANEL_SETTING)
        self.send_data(0x0f)
        
        self.send_command(0x15)
        self.send_data(0x00)
        
        print("VCOM and data intervals set")
        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x11)
        self.send_data(0x07)
        
        print("Tcon set")
        self.send_command(TCON_SETTING)
        self.send_data(LUT_WHITE)

    def wait_until_idle(self):
        busy = True
        while (busy):
            self.send_command(GET_STATUS)
            busy = self.digital_read(self.busy_pin) == 0x00

    def reset(self):
        self.digital_write(self.reset_pin, GPIO.LOW)         # module reset
        self.delay_ms(200)
        self.digital_write(self.reset_pin, GPIO.HIGH)
        self.delay_ms(200)    

    def get_frame_buffer(self, image):
        buf_w = [0xff] * int(self.height * self.width / 8)
        buf_r = [0x00] * int(self.height * self.width / 8)
        # Set buffer to value of Python Imaging Library image.
        # Image must be in mode L.
        image_grayscale = image.convert('L')
        imwidth, imheight = image_grayscale.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display \
                ({0}x{1}).' .format(self.width, self.height))

        pixels = image_grayscale.load()
        for y in range(self.height):
            for x in range(int(self.width / 8)):
                sign_w = 0xff
                sign_r = 0x00
                for i in range(0, 8):
                    p = pixels[x * 8 + i, y]
                    if p < 64:
                        sign_w &= ~(0x80 >> i)
                    elif p < 192:
                        sign_r |= 0x80 >> i
                index = x + int(y * self.width / 8)
                buf_w[index] = sign_w
                buf_r[index] = sign_r
        return (buf_w, buf_r)

    def display_frame(self, frame_buffer):
        buf_w, buf_r = frame_buffer

        def write_buffer(buf):
            for data in buf:
                self.send_data(data)
        self.send_command(DATA_START_TRANSMISSION_1)
        write_buffer(buf_w)
        self.send_command(DATA_START_TRANSMISSION_2)
        write_buffer(buf_r)

        self.send_command(DISPLAY_REFRESH)
        self.delay_ms(100)
        self.wait_until_idle()

    def sleep(self):
        self.send_command(POWER_OFF)
        self.wait_until_idle()
        self.send_command(DEEP_SLEEP)
        self.send_data(0xa5)

### END OF FILE ###

