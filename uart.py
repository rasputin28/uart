import serial
import time

# Open the serial port directly
ser = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)

print("UART loopback test started. Type something to send.")

try:
    while True:
        data = input("Send: ")
        if not data:
            continue
        ser.reset_input_buffer()  # Clear any old data
        ser.write(data.encode())  # Send data
        time.sleep(0.1)           # Give time for loopback

        incoming = ser.read(ser.in_waiting or 1)  # Read all available
        if incoming:
            print("Received:", incoming.decode(errors="ignore"))
        else:
            print("No data received.")
except KeyboardInterrupt:
    print("\nExiting.")
finally:
    ser.close()

