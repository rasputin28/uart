import serial
import time

BAUD_OPTIONS = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]

def choose_baud_rate():
    print("Select a baud rate:")
    for i, baud in enumerate(BAUD_OPTIONS):
        print(f"{i + 1}: {baud}")
    while True:
        choice = input(f"Enter number (1-{len(BAUD_OPTIONS)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(BAUD_OPTIONS):
            return BAUD_OPTIONS[int(choice) - 1]
        else:
            print("Invalid choice. Try again.")

def main():
    baud = choose_baud_rate()
    print(f"\nOpening /dev/ttyAMA0 at {baud} baud...")

    try:
        ser = serial.Serial("/dev/ttyAMA0", baudrate=baud, timeout=0.1)

        print("=== UART Monitor Started ===")
        print("Press Ctrl+C to exit.\n")

        with open("uart_raw_log.txt", "ab") as logfile:
            while True:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    timestamp = time.strftime("[%H:%M:%S] ").encode()
                    logline = timestamp + data
                    try:
                        # Display on terminal
                        print(data.decode('utf-8', errors='replace'), end='', flush=True)
                    except:
                        print("[!] Error decoding data")
                    # Log raw data with timestamp
                    logfile.write(logline)
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
