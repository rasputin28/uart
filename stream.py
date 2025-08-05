import serial
import time
import random

# Default common UART baud rates (same as read.py)
baud_rates = [
    110, 300, 600, 1200, 2400, 4800, 9600, 10400, 10450, 10500, 10550, 10600, 10638, 10650, 10700, 10800,
    14400, 15000, 16000, 16200, 16250, 16300, 16350, 16400, 16600, 16800, 17000, 17600, 18000, 19000, 19200,
    20000, 22000, 24000, 25000, 26000, 28800, 38400, 57600, 115200, 128000, 256000, 460800, 921600, 1000000,
    1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000,
]

# Default baud rate (will be set by user selection)
baudrate = 16250

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

def send_exact_line4_packet(port="/dev/ttyAMA0", baudrate=baudrate, duration=10, frequency=15):
    """
    Send the exact packet from line 4 of the logs repeatedly
    Packet: 0xbe 0xbe 0xfe 0xce 0x2 0xfe 0xbc 0xbe 0xbe 0xcc 0xfe 0xb2 0xfe 0xbe 0xcc 0xfc 0xf2 0xbe 0xc2 0xfe 0xb2 0xfe 0xe 0x0
    """
    # Exact packet from line 4 of the logs
    exact_packet = bytes([
        0xbe, 0xbe, 0xfe, 0xce, 0x02, 0xfe, 0xbc, 0xbe, 0xbe, 0xcc, 0xfe, 0xb2, 0xfe, 
        0xbe, 0xcc, 0xfc, 0xf2, 0xbe, 0xc2, 0xfe, 0xb2, 0xfe, 0x0e, 0x00
    ])
    
    print(f"Starting exact line 4 packet transmission...")
    print(f"  - Packet: {' '.join(hex(b) for b in exact_packet)}")
    print(f"  - Length: {len(exact_packet)} bytes")
    print(f"  - Frequency: {frequency} packets/second")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Total packets: {duration * frequency}")
    print()
    
    # Calculate interval between packets
    interval = 1.0 / frequency
    
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            start_time = time.time()
            packet_count = 0
            
            print("Starting transmission...")
            print("Press Ctrl+C to stop early")
            print()
            
            try:
                while time.time() - start_time < duration:
                    # Send the exact packet
                    ser.write(exact_packet)
                    ser.flush()
                    packet_count += 1
                    
                    # Show progress every 10 packets
                    if packet_count % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"Sent {packet_count} packets in {elapsed:.1f}s")
                    
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                print("\nStopped by user")
            
            elapsed = time.time() - start_time
            print(f"\n✓ Exact line 4 packet transmission complete!")
            print(f"  - Packets sent: {packet_count}")
            print(f"  - Duration: {elapsed:.1f} seconds")
            print(f"  - Average rate: {packet_count/elapsed:.1f} packets/second")
            
            # Check for any final response
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Final response: {[hex(b) for b in response]}")
            else:
                print("No final response received")
                
    except Exception as e:
        print(f"Error sending exact line 4 packet: {e}")

def send_corrected_20packets_packet(port="/dev/ttyAMA0", baudrate=baudrate, duration=10, frequency=20):
    """
    Send the corrected packet based on 20 packets/sec response
    Original: 0xce 0x02 → Corrected: 0xce 0xb2
    Original: 0xb2 0xfe 0xe → Corrected: 0xb2 0x4e 0xe
    Packet: 0xbe 0xbe 0xfe 0xce 0xb2 0xfe 0xbc 0xbe 0xbe 0xcc 0xfe 0xb2 0xfe 0xbe 0xcc 0xfc 0xf2 0xbe 0xc2 0xfe 0xb2 0x4e 0xe 0x0
    """
    # Corrected packet based on 20 packets/sec system response
    corrected_packet = bytes([
        0xbe, 0xbe, 0xfe, 0xce, 0xb2, 0xfe, 0xbc, 0xbe, 0xbe, 0xcc, 0xfe, 0xb2, 0xfe, 
        0xbe, 0xcc, 0xfc, 0xf2, 0xbe, 0xc2, 0xfe, 0xb2, 0x4e, 0x0e, 0x00
    ])
    
    print(f"Starting corrected 20 packets/sec packet transmission...")
    print(f"  - Packet: {' '.join(hex(b) for b in corrected_packet)}")
    print(f"  - Length: {len(corrected_packet)} bytes")
    print(f"  - Frequency: {frequency} packets/second")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Total packets: {duration * frequency}")
    print(f"  - Based on: System response to 20 packets/sec")
    print()
    
    # Calculate interval between packets
    interval = 1.0 / frequency
    
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            start_time = time.time()
            packet_count = 0
            
            print("Starting transmission...")
            print("Press Ctrl+C to stop early")
            print()
            
            try:
                while time.time() - start_time < duration:
                    # Send the corrected packet
                    ser.write(corrected_packet)
                    ser.flush()
                    packet_count += 1
                    
                    # Show progress every 10 packets
                    if packet_count % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"Sent {packet_count} packets in {elapsed:.1f}s")
                    
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                print("\nStopped by user")
            
            elapsed = time.time() - start_time
            print(f"\n✓ Corrected 20 packets/sec transmission complete!")
            print(f"  - Packets sent: {packet_count}")
            print(f"  - Duration: {elapsed:.1f} seconds")
            print(f"  - Average rate: {packet_count/elapsed:.1f} packets/second")
            
            # Check for any final response
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Final response: {[hex(b) for b in response]}")
            else:
                print("No final response received")
                
    except Exception as e:
        print(f"Error sending corrected 20 packets/sec packet: {e}")

def generate_acceleration_parameters(acceleration_level=0):
    """
    Generate acceleration parameters based on level (0-100)
    Based on the log analysis, these parameters change during acceleration
    """
    if acceleration_level == 0:
        # Idle/standby parameters (from line 4 in logs)
        return [0xC2, 0xFE, 0xB2, 0xFE, 0x0E]
    elif acceleration_level <= 25:
        # Low acceleration (from line 50 in logs)
        return [0xC2, 0xFE, 0xB2, 0xFE, 0x0E]
    elif acceleration_level <= 50:
        # Medium acceleration (from line 63 in logs)
        return [0x42, 0x8E, 0x82, 0xF2, 0x82]
    elif acceleration_level <= 75:
        # High acceleration (from line 71 in logs)
        return [0x42, 0xCE, 0x82, 0xF2, 0xC2]
    else:
        # Maximum acceleration (from line 79 in logs)
        return [0x42, 0xF2, 0x82, 0xF2, 0xFE]

def create_complete_packet_stream(acceleration_level=0):
    """
    Create the complete packet stream based on log analysis
    This simulates the exact packet structure observed in the logs
    """
    # Generate acceleration parameters
    accel_params = generate_acceleration_parameters(acceleration_level)
    
    # Complete packet stream from log analysis (line 4 pattern)
    # Pattern: 0xBE 0xBE 0xFE 0xCE 0x02 0xFE 0xBC 0xBE 0xBE 0xCC 0xFE 0xB2 0xFE 0xBE 0xCC 0xFC 0xF2 0xBE [ACCEL_PARAMS] 0x00
    packet_stream = [
        0xBE, 0xBE, 0xFE, 0xCE, 0x02, 0xFE, 0xBC, 0xBE, 0xBE, 0xCC, 0xFE, 0xB2, 0xFE, 
        0xBE, 0xCC, 0xFC, 0xF2, 0xBE,  # Fixed acceleration command header
        accel_params[0], 0xFE, accel_params[1], 0xFE, accel_params[2], 0x00  # Variable acceleration parameters
    ]
    
    return bytes(packet_stream)

def send_packet_stream(port="/dev/ttyAMA0", baudrate=baudrate, duration=10, frequency=15):
    """
    Send the complete packet stream at specified frequency
    """
    print(f"Starting packet stream simulation...")
    print(f"  - Frequency: {frequency} packets/second")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Total packets: {duration * frequency}")
    print(f"  - Packet structure: Complete ebike stream simulation")
    print()
    
    # Calculate interval between packets
    interval = 1.0 / frequency
    
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            start_time = time.time()
            packet_count = 0
            
            print("Starting transmission...")
            print("Press Ctrl+C to stop early")
            print()
            
            try:
                while time.time() - start_time < duration:
                    # Generate varying acceleration levels (0-100)
                    # Simulate realistic acceleration curve
                    elapsed = time.time() - start_time
                    progress = elapsed / duration
                    
                    # Create acceleration curve: start low, peak in middle, end low
                    if progress < 0.3:
                        # Ramp up
                        accel_level = int(progress * 333)  # 0 to 100
                    elif progress < 0.7:
                        # Peak acceleration
                        accel_level = 100
                    else:
                        # Ramp down
                        accel_level = int((1 - progress) * 333)  # 100 to 0
                    
                    # Create packet with current acceleration level
                    packet = create_complete_packet_stream(accel_level)
                    
                    # Send the packet
                    ser.write(packet)
                    ser.flush()
                    packet_count += 1
                    
                    # Show progress every 10 packets
                    if packet_count % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"Sent {packet_count} packets in {elapsed:.1f}s (accel: {accel_level}%)")
                    
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                print("\nStopped by user")
            
            elapsed = time.time() - start_time
            print(f"\n✓ Stream transmission complete!")
            print(f"  - Packets sent: {packet_count}")
            print(f"  - Duration: {elapsed:.1f} seconds")
            print(f"  - Average rate: {packet_count/elapsed:.1f} packets/second")
            
            # Check for any final response
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Final response: {[hex(b) for b in response]}")
            else:
                print("No final response received")
                
    except Exception as e:
        print(f"Error sending packet stream: {e}")

def send_constant_acceleration_stream(port="/dev/ttyAMA0", baudrate=baudrate, acceleration_level=50, duration=10, frequency=15):
    """
    Send packet stream with constant acceleration level
    """
    print(f"Starting constant acceleration stream...")
    print(f"  - Acceleration level: {acceleration_level}%")
    print(f"  - Frequency: {frequency} packets/second")
    print(f"  - Duration: {duration} seconds")
    print()
    
    interval = 1.0 / frequency
    
    try:
        with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
            start_time = time.time()
            packet_count = 0
            
            print("Starting transmission...")
            print("Press Ctrl+C to stop early")
            print()
            
            try:
                while time.time() - start_time < duration:
                    packet = create_complete_packet_stream(acceleration_level)
                    ser.write(packet)
                    ser.flush()
                    packet_count += 1
                    
                    if packet_count % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"Sent {packet_count} packets in {elapsed:.1f}s")
                    
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                print("\nStopped by user")
            
            elapsed = time.time() - start_time
            print(f"\n✓ Constant acceleration stream complete!")
            print(f"  - Packets sent: {packet_count}")
            print(f"  - Duration: {elapsed:.1f} seconds")
            print(f"  - Average rate: {packet_count/elapsed:.1f} packets/second")
            
    except Exception as e:
        print(f"Error sending constant acceleration stream: {e}")

def show_packet_analysis():
    """
    Show analysis of the packet structure
    """
    print("Packet Stream Analysis")
    print("=" * 50)
    print("Based on log analysis, the complete packet structure is:")
    print()
    
    # Show example packet
    example_packet = create_complete_packet_stream(50)
    print(f"Example packet (50% acceleration):")
    print(f"  HEX: {' '.join(hex(b) for b in example_packet)}")
    print(f"  Length: {len(example_packet)} bytes")
    print()
    
    print("Packet structure breakdown:")
    print("  [0-2]   0xBE 0xBE 0xFE     - Start markers")
    print("  [3-5]   0xCE 0x02 0xFE     - Header data")
    print("  [6]     0xBC               - Separator")
    print("  [7-9]   0xBE 0xBE 0xCC     - Power/status command")
    print("  [10]    0xFE               - End marker")
    print("  [11]    0xB2               - Status parameter")
    print("  [12]    0xFE               - End marker")
    print("  [13-16] 0xBE 0xCC 0xFC 0xF2 - Acceleration command header")
    print("  [17]    0xBE               - Start marker")
    print("  [18]    [VAR]              - Acceleration command")
    print("  [19]    0xFE               - Separator")
    print("  [20]    [VAR]              - Acceleration parameter 1")
    print("  [21]    0xFE               - Separator")
    print("  [22]    [VAR]              - Acceleration parameter 2")
    print("  [23]    0x00               - End marker")
    print()
    
    print("Acceleration parameter mapping (from actual logs):")
    print("  0% (idle):     [0xC2, 0xFE, 0xB2, 0xFE, 0x0E]")
    print("  25% (low):     [0xC2, 0xFE, 0xB2, 0xFE, 0x0E]")
    print("  50% (medium):  [0x42, 0x8E, 0x82, 0xF2, 0x82]")
    print("  75% (high):    [0x42, 0xCE, 0x82, 0xF2, 0xC2]")
    print("  100% (max):    [0x42, 0xF2, 0x82, 0xF2, 0xFE]")
    print()

def main():
    print("Ebike Packet Stream Simulator")
    print("=" * 40)
    print("This tool simulates the complete packet stream observed in ebike logs")
    print("WARNING: This may control your ebike!")
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
    print("1. Send exact line 4 packet (repeated)")
    print("2. Send corrected 20 packets/sec packet (system-suggested)")
    print("3. Send variable acceleration stream (realistic simulation)")
    print("4. Send constant acceleration stream (fixed level)")
    print("5. Show packet analysis")
    print("6. Exit")
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == "1":
        try:
            duration = float(input("Enter duration in seconds (e.g., 10): ").strip())
        except ValueError:
            duration = 10.0
        
        try:
            frequency = float(input("Enter frequency in packets/second (e.g., 15): ").strip())
        except ValueError:
            frequency = 15.0
        
        send_exact_line4_packet(duration=duration, frequency=frequency)
        
    elif choice == "2":
        try:
            duration = float(input("Enter duration in seconds (e.g., 10): ").strip())
        except ValueError:
            duration = 10.0
        
        try:
            frequency = float(input("Enter frequency in packets/second (e.g., 20): ").strip())
        except ValueError:
            frequency = 20.0
        
        send_corrected_20packets_packet(duration=duration, frequency=frequency)
        
    elif choice == "3":
        try:
            duration = float(input("Enter duration in seconds (e.g., 10): ").strip())
        except ValueError:
            duration = 10.0
        
        try:
            frequency = float(input("Enter frequency in packets/second (e.g., 15): ").strip())
        except ValueError:
            frequency = 15.0
        
        send_packet_stream(duration=duration, frequency=frequency)
        
    elif choice == "4":
        try:
            accel_level = int(input("Enter acceleration level (0-100): ").strip())
            accel_level = max(0, min(100, accel_level))
        except ValueError:
            accel_level = 50
        
        try:
            duration = float(input("Enter duration in seconds (e.g., 10): ").strip())
        except ValueError:
            duration = 10.0
        
        try:
            frequency = float(input("Enter frequency in packets/second (e.g., 15): ").strip())
        except ValueError:
            frequency = 15.0
        
        send_constant_acceleration_stream(acceleration_level=accel_level, duration=duration, frequency=frequency)
        
    elif choice == "5":
        show_packet_analysis()
        
    elif choice == "6":
        print("Exiting...")
        
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()