#Code created by David Encarnacion
#Last Updated: 11/4/2024 10:14

from PCB_class import PCB

pcb = PCB()

print("Displaying image...")
pcb.display_image('RaspberryPiWB128x128.raw')

count = (pcb.last_num + 2) - pcb.last_num
print("Initiating TakeMultiplePictures...")
pcb.TakeMultiplePictures('inspireFly_Capture_', '640x480', 500, count)

file_path = f"inspireFly_Capture_{pcb.last_num - 1}.jpg"
with open(file_path, "rb") as file:
    jpg_bytes = file.read()

print("Initiating data transmission with flight computer...")
pcb.communicate_with_fcb(jpg_bytes)
