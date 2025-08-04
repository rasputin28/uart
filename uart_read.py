import serial
import time

BAUD_OPTIONS = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]

def choose_baud_rate():
    print("Select a baud rate:")
    for i, baud in enumerate(BAUD_OPTIONS):
        print(f"{i + 1}: {baud}")
    while True:
        choice = input("Enter number (1-{}): ".format(len(BAUD_OPTIONS)))
        if choice.isdigit() and 1 <= int(choice) <= len(BAUD_OPTIONS):
            return BAUD_OPTIONS[int(choice) - 1]
        else:
            print("Invalid input, try again.")

def main():
    baud_rate = choose_baud_rate()
    print(f"Opening /dev/ttyAMA0 at {baud_rate} baud...")

    try:
        ser = serial.Serial("/dev/ttyAMA0", baudrate=baud_rate, timeout=0.5)
        print("Listening for UART data. Press Ctrl+C to exit.\n")

        with open("uart_log.txt", "w") as logfile:
            while True:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    decoded = data.decode(errors='ignore')
                    print(decoded, end="", flush=True)
                    logfile.write(decoded)
                    logfile.flush()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print("Error:", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
