import board
import digitalio
import storage
import usb_hid
import sdcardio
import busio
import os
import state

program_pin = digitalio.DigitalInOut(board.GP0)
program_pin.direction = digitalio.Direction.INPUT
program_pin.pull = digitalio.Pull.UP

print("Boot.py: Starting...")

payload_name = os.getenv("PAYLOAD_NAME")
payload_dir = os.getenv("PAYLOAD_DIRECTORY")
attack_mode = os.getenv("ATTACK_MODE")

print("PAYLOAD DIRECTORY:", repr(payload_dir))
print("PAYLOAD NAME:", repr(payload_name))
print("PAYLOAD DIR:", os.listdir(payload_dir))

print("Boot.py: Mounting SD")

SD_AVAILABLE = False

try:
    spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP4)
    cs = board.GP5

    sd = sdcardio.SDCard(spi, cs)
    vfs = storage.VfsFat(sd)
    storage.mount(vfs, "/sd")

    SD_AVAILABLE = True
    print("SD card mounted")

except (OSError, RuntimeError) as e:
    print("SD Card mount failure :", e)

print("Boot.py: Configuring USB HID")
# HID is enabled even in programming mode because that makes it easier to debug.
usb_hid.enable((usb_hid.Device.KEYBOARD,))


if not program_pin.value:
    print("Boot.py: Entering programming mode")
    state.programming_mode = False
    storage.remount("/", readonly=True)
else:
    print("Boot.py: Entering payload mode")
    state.programming_mode = True
    if attack_mode != "storage":
        storage.disable_usb_drive()
    else:
        storage.remount("/", readonly=True)

    try:
        if usb_hid.devices:
            print("Boot.py: HID keyboard enabled successfully")
        else:
            print("Boot.py: WARNING - No HID devices available after enable")
    except Exception as e:
        print(f"Boot.py: Error enabling HID: {str(e)}")

print("Boot.py: Completed")
