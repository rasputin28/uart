import serial

# Initialize serial connection
ser = serial.Serial("/dev/ttyAMA0", baudrate=115200)

print("UART test started, type something for I/O or simply listen for device")

try:
    while True:
        data = input("Send: ")
        if not data:
            continue
        ser.write(data.encode())
        print("Waiting for echo...")
        echo = ser.read(len(data))
        print("Received: ", echo.decode(errors="ignore"))
except KeyboardInterrupt:
    print("Exiting (Ctrl+C pressed)")
except Exception as e:
    print("Error:", e)
finally:
    ser.close()

