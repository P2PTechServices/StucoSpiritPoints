import board
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
from secrets import secrets as wifi_info

class WiFi:
    def __init__(self):
        
        esp32_cs = DigitalInOut(board.ESP_CS)
        esp32_ready = DigitalInOut(board.ESP_BUSY)
        esp32_reset = DigitalInOut(board.ESP_RESET)
    
        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        self._esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    
        requests.set_socket(socket, self._esp)
        
    def connect(self):
        if self.is_connected():
            return
            
        while not self._esp.is_connected:
            try:
                self._esp.connect_AP(wifi_info["ssid"], "")
            except OSError as e:
                print("could not connect to AP, retrying: ", e)
                continue
    
    def is_connected(self):
        return self._esp.is_connected
        
    
    def get(self, url):
        if not self.is_connected():
            raise RuntimeError("You can't get from a URL until WiFi is connected") 
            
        r = requests.get(url)
        resp = r.text
        r.close()
        
        return resp
        
    def disconnect(self):
        if self.is_connected():
            self._esp.disconnect()
        
