import time
import json
from WiFi import WiFi
from metro import *

wifi = WiFi()
grid = PixelGrid(D6, 8, 32, 0.1, row_major=False, auto_write=False)  

grid.fill(0, 0, 0)
grid.draw_text(0, 0,"Wait...", 255, 0, 0)
grid.show()

while True:
    print ("Connecting to Wifi")
    wifi.connect()
    print("Connected")
    
    print("Fetching text from pumas.dev")
    text = wifi.get("https://www.pumas.dev/public/stuco.txt")
    points = json.loads(text)
    
    for keyVal in points.items():
        print(keyVal[0], keyVal[1])
    
    print("Disconnecting...")
    wifi.disconnect()

    grid.fill(0, 0, 0)
    if "fpoints" in points:
        grid.draw_text(0, 0, "9th", 0, 255, 255)
        grid.draw_text(0, 14, ":", 0, 255, 255)
        grid.draw_text(0, 17, points["fpoints"], 255, 0, 255)
    else:
        grid.draw_text(0, 0, "Error", 255, 0, 0)

    grid.show()

    print("Wait and try again")
    time.sleep(10)  # 10 minutes
    