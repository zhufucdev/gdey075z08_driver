# GDEY075Z08 Driver

## What's this

I was doing some hobby project when I found that
my newly bought e-ink display has no driver implemented
in python, which is the best choice for me to accomplish
the project

## How to use

Here's an example

```python
import gdey075z08_driver as driver
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#import imagedata

EPD_WIDTH = 800
EPD_HEIGHT = 480


def main(epd):

    # For simplicity, the arguments are explicit numerical coordinates
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), 255)    # 255: clear the frame
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)
    draw.rectangle((0, 6, 640, 40), fill = 127)
    draw.text((200, 10), 'e-Paper demo', font = font, fill = 255)
    draw.rectangle((200, 80, 600, 280), fill = 127)
    draw.chord((240, 120, 580, 220), 0, 360, fill = 255)
    draw.rectangle((20, 80, 160, 280), fill = 0)
    draw.chord((40, 80, 180, 220), 0, 360, fill = 127)
    epd.display_frame(epd.get_frame_buffer(image))

    #image = Image.open('800x480.bmp')
    #epd.display_frame(epd.get_frame_buffer(image))

    # You can get frame buffer from an image or import the buffer directly:
    #epd.display_frame(imagedata.MONOCOLOR_BITMAP)

if __name__ == '__main__':
    epd = driver.EPD()
    epd.init()
    try:
        main(epd)
    finally:
        epd.sleep()
```

If you break your display when using this library,
please raise an issue so that I won't break my own

## License
`
MIT License

Copyright (c) 2023 zhufucdev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
`
