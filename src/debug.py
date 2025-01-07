import time
import sys
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Define the dimensions of the LED matrix
canvas_width = 64
canvas_height = 32

# Create a simple static image (red background)
static_image = Image.new("RGB", (canvas_width, canvas_height), (255, 0, 0))  # Red image

# Initialize the RGBMatrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.brightness = 100
options.pixel_mapper_config = "U-mapper;Rotate:180"
options.gpio_slowdown = 1
options.pwm_lsb_nanoseconds = 80
options.limit_refresh_rate_hz = 150
options.hardware_mapping = "regular"  # If you have an Adafruit HAT: 'adafruit-hat'
options.drop_privileges = False
options.led_no_hardware_pulse = True  # Add this line to use the flag

# Create the RGBMatrix instance
matrix = RGBMatrix(options=options)

# Display the static image
matrix.SetImage(static_image)

# Keep the script running to display the image
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Interrupted with Ctrl-C")
    sys.exit(0)
