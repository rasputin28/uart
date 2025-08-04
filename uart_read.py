import serial
import time

# === Configure your serial connection ===
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200
TIMEOUT = 1  # seconds

# === Optional: log file ===
LOG_TO_FILE = True
LOG_FILE = "uart_log.txt"

# === Open UART ===
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")
except Exception as e:
    print("Failed to open serial port:", e)
    exit(1)

# === Monitor Loop ===
try:
    with open(LOG_FILE, "a") if LOG_TO_FILE else open("/dev/null", "w") as f:
        while True:
            data = ser.readline().decode(errors="ignore").strip()
            if data:
                print("[UART]", data)
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
                f.flush()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
