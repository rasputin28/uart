import serial
import time

# Default common UART baud rates
baud_rates = [
    110,
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    14400,
    19200,
    20000,
    22000,
    24000,
    25000,
    26000,
    28800,
    38400,
    57600,
    115200,
    128000,
    256000,
    460800,
    921600,
    1000000,
    1152000,
    1500000,
    2000000,
    2500000,
    3000000,
    3500000,
    4000000,
]

# Prompt user for mode
# mode = input("Select mode: [a]uto baud detect or [m]anual selection? ").strip().lower()

# if mode == 'm':
print("Available baud rates:")
for i, br in enumerate(baud_rates):
    print(f"{i + 1}: {br}")
try:
    index = int(input("Select baud rate number: ")) - 1
    baud = baud_rates[index]
except:
    print("Invalid selection.")
    exit(1)
baud_list = [baud]
# else:
#     print("Running auto baud rate scan (10s each)...")
#     baud_list = baud_rates

# Try each baud rate
for baud in baud_list:
    print(f"\nTrying baud rate: {baud}")
    try:
        with serial.Serial("/dev/ttyAMA0", baudrate=baud, timeout=1) as ser, open("log.txt", "a") as log:
            start = time.time()
            while time.time() - start < 10:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    raw = repr(data)
                    decoded_utf8 = data.decode(errors="replace")
                    decoded_latin1 = data.decode('latin-1')
                    hex_output = [hex(b) for b in data]
                    log.write(f"[{baud}] RAW: {raw}\n")
                    log.write(f"[{baud}] DEC UTF-8 (with replacement): {decoded_utf8}\n")
                    log.write(f"[{baud}] DEC Latin-1: {decoded_latin1}\n")
                    log.write(f"[{baud}] HEX: {hex_output}\n")
                    print(f"[{baud}] RAW: {raw}")
                    print(f"[{baud}] HEX: {hex_output}")
                    print(f"[{baud}] DEC UTF-8 (with replacement): {decoded_utf8}")
                    print(f"[{baud}] DEC Latin-1: {decoded_latin1}")
    except Exception as e:
        print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
