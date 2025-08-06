import serial
import time

# Configuration
SERIAL_PORT = '/dev/ttyAMA0'  # LCD TX line
BAUD_RATE = 16250
START_MARKER = 0xBE
END_MARKER = 0xFE

def create_packet(command_bytes):
    """Create a complete packet with start/end markers"""
    packet = bytearray([START_MARKER])
    packet.extend(command_bytes)
    packet.append(END_MARKER)
    return bytes(packet)

def send_power_on():
    """Send power-on sequence from logs"""
    commands = [
        [0xCC],  # Basic power
        [0x42],  # Status
        [0xC2],  # Control
    ]
    
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        for cmd in commands:
            packet = create_packet(cmd)
            print(f"Sending: {' '.join(hex(b) for b in packet)}")
            ser.write(packet)
            ser.flush()
            time.sleep(0.1)

def send_throttle_command(throttle_level):
    """Send throttle command based on level (0-100)"""
    if throttle_level == 0:
        cmd = [0xCC]  # Idle
    elif throttle_level <= 25:
        cmd = [0xCC, 0xFC, 0xF2, 0x1E, 0x42]
    elif throttle_level <= 50:
        cmd = [0xCC, 0xFC, 0xF2, 0x8E, 0x42]
    elif throttle_level <= 75:
        cmd = [0xCC, 0xF4, 0xF2, 0x3A, 0x42]
    else:  # 100%
        cmd = [0xCC, 0xFC, 0xF2, 0x1E, 0xC2, 0x34, 0x7E, 0x40]
    
    packet = create_packet(cmd)
    
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Throttle {throttle_level}%: {' '.join(hex(b) for b in packet)}")
        ser.write(packet)
        ser.flush()

def send_complex_sequence():
    """Send the complex 22-byte status sequence from logs"""
    cmd = [0x42, 0x7E, 0x26, 0x40, 0xCE, 0x82] + [0x00] * 16
    packet = create_packet(cmd)
    
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Complex sequence: {' '.join(hex(b) for b in packet)}")
        ser.write(packet)
        ser.flush()

def interactive_control():
    """Interactive throttle control"""
    print("Interactive throttle control (0-100, 'q' to quit)")
    
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            try:
                user_input = input("Throttle level (0-100): ").strip()
                if user_input.lower() == 'q':
                    break
                
                level = int(user_input)
                if 0 <= level <= 100:
                    send_throttle_command(level)
                else:
                    print("Invalid level (0-100)")
                    
            except ValueError:
                print("Invalid input")
            except KeyboardInterrupt:
                break

def main():
    print("LCD Command Sender")
    print("1. Send power-on sequence")
    print("2. Send throttle command")
    print("3. Send complex sequence")
    print("4. Interactive control")
    print("5. Exit")
    
    choice = input("Select option: ").strip()
    
    if choice == "1":
        send_power_on()
    elif choice == "2":
        level = int(input("Throttle level (0-100): "))
        send_throttle_command(level)
    elif choice == "3":
        send_complex_sequence()
    elif choice == "4":
        interactive_control()
    else:
        print("Exiting")

if __name__ == "__main__":
    main()