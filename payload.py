import serial
import time

# Default common UART baud rates (same as read.py)
baud_rates = [
    110,
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    10400,
    10450,
    10500,
    10550,
    10600,
    10638,
    10650,
    10700,
    10800,
    14400,
    15000,
    16000,
    16200,
    16250,
    16300,
    16350,
    16400,
    16600,
    16800,
    17000,
    17600,
    18000,
    19000,
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

# Default baud rate (will be set by user selection)
baudrate = 16250

def send_power_on_packet(port="/dev/ttyAMA0", baudrate=baudrate):
    """
    Send the power-on command packet: 0xBE 0xCC 0xFE
    This packet was observed during bootup at position (0-2)
    """
    power_on_packet = bytes([0xBE, 0xCC, 0xFE])
    
    print(f"Sending power-on packet: {[hex(b) for b in power_on_packet]}")
    print(f"Packet bytes: {power_on_packet}")
    print(f"Expected effect: Turn on the ebike")
    
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            # Send the packet
            ser.write(power_on_packet)
            ser.flush()  # Ensure all data is sent
            
            print(f"✓ Power-on packet sent successfully!")
            print(f"  - Start marker: 0xBE")
            print(f"  - Command: 0xCC (suspected power-on)")
            print(f"  - End marker: 0xFE")
            
            # Wait a moment to see if there's any response
            time.sleep(2)
            
            # Check for any response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Response received: {[hex(b) for b in response]}")
                print(f"Response as bytes: {response}")
            else:
                print("No immediate response received (this is normal for power commands)")
                
    except Exception as e:
        print(f"Error sending power-on packet: {e}")

def send_manual_packet(port="/dev/ttyAMA0", baudrate=baudrate):
    """
    Send a completely manual packet - user types in every byte
    """
    print("Enter the complete packet bytes (hex format)")
    print("Example: BE CC FE (for power-on packet)")
    print("Example: BE 01 02 03 FE (for command with data)")
    print("Example: AA BB CC DD (for custom protocol)")
    
    packet_input = input("Enter packet bytes (space-separated hex): ").strip()
    
    try:
        # Parse the hex bytes
        packet_bytes = [int(x, 16) for x in packet_input.split()]
        packet = bytes(packet_bytes)
        
        print(f"Sending manual packet: {[hex(b) for b in packet]}")
        print(f"Packet as bytes: {packet}")
        print(f"Packet length: {len(packet)} bytes")
        
        # Show packet structure analysis
        if len(packet) >= 1:
            print(f"First byte: 0x{packet[0]:02X}")
            if len(packet) >= 2:
                print(f"Last byte: 0x{packet[-1]:02X}")
            if len(packet) > 2:
                print(f"Middle bytes: {[hex(b) for b in packet[1:-1]]}")
        
        # Confirm before sending
        confirm = input("Send this packet? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Packet cancelled.")
            return
        
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            ser.write(packet)
            ser.flush()
            
            print(f"✓ Manual packet sent successfully!")
            
            # Wait for response
            time.sleep(2)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Response: {[hex(b) for b in response]}")
                print(f"Response as bytes: {response}")
            else:
                print("No response received")
                
    except ValueError as e:
        print(f"Invalid hex format: {e}")
        print("Make sure to use space-separated hex values (e.g., 'BE CC FE')")
    except Exception as e:
        print(f"Error sending manual packet: {e}")

def select_baud_rate():
    """
    Let user select baud rate from the list
    """
    while True:
        print("Available baud rates:")
        for i, br in enumerate(baud_rates):
            print(f"{i + 1:2d}: {br}")
        
        try:
            index = int(input("Select baud rate number: ")) - 1
            if 0 <= index < len(baud_rates):
                selected_baud = baud_rates[index]
                print(f"Selected baud rate: {selected_baud}")
                return selected_baud
            else:
                print("Invalid selection. Please try again.")
                print()
        except ValueError:
            print("Invalid input. Please enter a number.")
            print()



def main():
    print("Ebike Power-On Packet Injection Tool")
    print("=" * 40)
    print("This tool tests the suspected power-on command: 0xBE 0xCC 0xFE")
    print("WARNING: This may turn on your ebike!")
    print()
    
    # Select baud rate
    global baudrate
    baudrate = select_baud_rate()
    print()
    
    # Get user confirmation
    confirm = input("Do you want to proceed? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    print("\nSelect operation:")
    print("1. Send power-on packet (0xBE 0xCC 0xFE)")
    print("2. Send manual packet (type in complete packet)")
    print("3. Exit")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        send_power_on_packet()
    elif choice == "2":
        send_manual_packet()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice.")

# Example usage functions
def examples():
    """
    Example commands you can run directly
    """
    print("Example commands you can run:")
    print()
    print("# Power on the ebike")
    print("send_power_on_packet()")
    print()
    print("# Send manual packet")
    print("send_manual_packet()")

if __name__ == "__main__":
    main()
