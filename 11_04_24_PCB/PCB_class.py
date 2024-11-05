#Code created by David Encarnacion
#Last Updated: 11/4/2024 10:14

from time import sleep_ms
from ssd1351 import Display
from machine import Pin, SPI
from Camera import *
from easy_comms_micro import Easy_comms
import os

class PCB:
    def __init__(self):
        self.spi_display = SPI(0, baudrate=14500000, sck=Pin(18), mosi=Pin(19))
        self.display = Display(self.spi_display, dc=Pin(14), cs=Pin(21), rst=Pin(7))
        
        self.spi_camera = SPI(1, sck=Pin(10), miso=Pin(8), mosi=Pin(11), baudrate=8000000)
        self.cs = Pin(9, Pin.OUT)
        self.onboard_LED = Pin(25, Pin.OUT)
        self.cam = Camera(self.spi_camera, self.cs)
        
        self.com1 = Easy_comms(uart_id=1, baud_rate=14500000)
        self.com1.start()
        
        self.last_num = self.get_last_num()
    
    def get_last_num(self):
        try:
            with open('last_num.txt', 'r') as f:
                return int(f.read())
        except OSError:
            return 1

    def TakePicture(self, imageName, resolution):
        self.onboard_LED.on()
        finalImageName = f"{imageName}.jpg"
        self.cam.resolution = resolution
        sleep_ms(500)
        self.cam.capture_jpg()
        sleep_ms(500)
        self.cam.saveJPG(finalImageName)
        self.onboard_LED.off()
        
        # Update last number
        with open('last_num.txt', 'w') as f:
            f.write(str(self.last_num + 1))

    def TakeMultiplePictures(self, imageName, resolution, interval, count):
        self.cam.resolution = resolution
        for x in range(count):
            endImageName = f"{imageName}{self.last_num}"
            self.TakePicture(endImageName, resolution)
            sleep_ms(500)
            if x == 0:
                try:
                    os.remove(f"{endImageName}.jpg")
                except OSError:
                    print(f"Error removing file: {endImageName}.jpg")
            sleep_ms(interval)

    def display_image(self, image_path):
        self.display.draw_image(image_path, 0, 0, 128, 128)

    def communicate_with_fcb(self, jpg_bytes):
        while True:
            command = self.com1.overhead_read()
            if command.lower() == 'chunk':
                self.send_chunks(jpg_bytes)
            elif command.lower() == 'end':
                print('See you space cowboy...')
                break

    def send_chunks(self, jpg_bytes):
        chunksize = 66
        message = self.com1.overhead_read()
        
        if message != "Wrong":
            a, b = map(int, message.split())
            for i in range(a, b + 1):
                print("Chunk #",i)
                self.onboard_LED.off()
                chunk = jpg_bytes[i * chunksize:(i + 1) * chunksize]
                chunknum = i.to_bytes(2, 'little')
                chunk = chunknum + chunk
                
                crctagb = self.com1.calculate_crc16(chunk)
                chunk += crctagb.to_bytes(2, 'little')
                
                self.onboard_LED.on()
                self.com1.send_bytes(chunk)
                
                while (recievecheck := self.com1.overhead_read()) == "Chunk has an error.":
                    self.com1.send_bytes(chunk)
                self.onboard_LED.off()
