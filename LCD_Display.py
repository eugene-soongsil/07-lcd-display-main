import os
import time
import Adafruit_DHT

# GPIO path
GPIO_BASE_PATH = "/sys/class/gpio"
GPIO_EXPORT_PATH = os.path.join(GPIO_BASE_PATH, "export")
GPIO_UNEXPORT_PATH = os.path.join(GPIO_BASE_PATH, "unexport")

# GPIO pin control function
def gpio_export(pin):
    if not os.path.exists(os.path.join(GPIO_BASE_PATH, f"gpio{pin}")):
        with open(GPIO_EXPORT_PATH, 'w') as f:
            f.write(str(pin))

def gpio_unexport(pin):
    with open(GPIO_UNEXPORT_PATH, 'w') as f:
        f.write(str(pin))

def gpio_set_direction(pin, direction):
    direction_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "direction")
    with open(direction_path, 'w') as f:
        f.write(direction)

def gpio_write(pin, value):
    value_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "value")
    with open(value_path, 'w') as f:
        f.write(str(value))

def gpio_read(pin):
    value_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "value")
    with open(value_path, 'r') as f:
        return f.read().strip()

# LCD Pin Definitions
LCD_RS = 117  
LCD_E  = 121  
LCD_D4 = 114  
LCD_D5 = 113   
LCD_D6 = 112   
LCD_D7 = 61  

LCD_WIDTH = 16  
LCD_CHR = "1"
LCD_CMD = "0"

LCD_LINE_1 = 0x80  
LCD_LINE_2 = 0xC0 

E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_init():
    gpio_export(LCD_E)
    gpio_export(LCD_RS)
    gpio_export(LCD_D4)
    gpio_export(LCD_D5)
    gpio_export(LCD_D6)
    gpio_export(LCD_D7)

    gpio_set_direction(LCD_E, "out")
    gpio_set_direction(LCD_RS, "out")
    gpio_set_direction(LCD_D4, "out")
    gpio_set_direction(LCD_D5, "out")
    gpio_set_direction(LCD_D6, "out")
    gpio_set_direction(LCD_D7, "out")

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    gpio_write(LCD_RS, mode)
    gpio_write(LCD_D4, "0")
    gpio_write(LCD_D5, "0")
    gpio_write(LCD_D6, "0")
    gpio_write(LCD_D7, "0")

    if bits & 0x10 == 0x10:
        gpio_write(LCD_D4, "1")
    if bits & 0x20 == 0x20:
        gpio_write(LCD_D5, "1")
    if bits & 0x40 == 0x40:
        gpio_write(LCD_D6, "1")
    if bits & 0x80 == 0x80:
        gpio_write(LCD_D7, "1")

    lcd_toggle_enable()

    gpio_write(LCD_D4, "0")
    gpio_write(LCD_D5, "0")
    gpio_write(LCD_D6, "0")
    gpio_write(LCD_D7, "0")

    if bits & 0x01 == 0x01:
        gpio_write(LCD_D4, "1")
    if bits & 0x02 == 0x02:
        gpio_write(LCD_D5, "1")
    if bits & 0x04 == 0x04:
        gpio_write(LCD_D6, "1")
    if bits & 0x08 == 0x08:
        gpio_write(LCD_D7, "1")

    lcd_toggle_enable()

def lcd_toggle_enable():
    time.sleep(E_DELAY)
    gpio_write(LCD_E, "1")
    time.sleep(E_PULSE)
    gpio_write(LCD_E, "0")
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def get_current_time():
    # Get current time in HH:MM:SS format
    return time.strftime("%H:%M:%S", time.localtime())

# Main program
if __name__ == "__main__":
    DHT_SENSOR = Adafruit_DHT.DHT11  # DHT11 센서를 사용
    DHT_PIN = 4  # GPIO 핀 번호

    try:
        lcd_init()
        while True:
            # 현재 시간 가져오기
            current_time = get_current_time()

            # DHT 센서에서 온도와 습도 읽기
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

            if humidity is not None and temperature is not None:
                # LCD에 시간과 온습도 표시
                lcd_string(f"Time: {current_time}", LCD_LINE_1)
                lcd_string(f"T:{temperature:.1f}C H:{humidity:.1f}%", LCD_LINE_2)
            else:
                lcd_string("Sensor Error!", LCD_LINE_1)

            time.sleep(2)  # 2초마다 갱신
    except KeyboardInterrupt:
        print("\nProgram stopped by User")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        gpio_unexport(LCD_E)
        gpio_unexport(LCD_RS)
        gpio_unexport(LCD_D4)
        gpio_unexport(LCD_D5)
        gpio_unexport(LCD_D6)
        gpio_unexport(LCD_D7)
