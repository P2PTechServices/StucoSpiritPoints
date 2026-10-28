from metro import *

# connect 5V to 5V (or 3.3V)
# connect GND to GND
# connect DI to A0-A5 or D1-D13

# create a PixelGrid that is:
#  connected to pin D6 
#  has 8 rows and 32 columns of LEDs
#  which are arranged in column_major order
#  at 30% brightness

grid = PixelGrid(D6, 8, 32, 0.3, row_major=False, auto_write=False)  

while True:
    # fill with different colors
    grid.fill(255, 0, 0)  # fill all red
    grid.show()
    wait(1.0)
    grid.fill((0, 255, 0)) # fill green using tuple
    grid.show()
    wait(1.0)


    # fill one by one in row-major order
    for r in range(8):
        for c in range(32):
            grid.set_pixel(r, c, 0, 0, 255)
            grid.show()
    wait(1.0)

    # scroll text left to right
    for c in range(33):
        grid.fill(0, 0, 0)
        grid.draw_text(0, c, "Hello", 0, 255, 0)
        grid.show()
    wait(1.0)