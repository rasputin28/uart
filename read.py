import serial
import time

# Default common UART baud rates
baud_rates = [
    110, 300, 600, 1200, 2400, 4800, 9600, 10400, 10450, 10500, 10550, 10600, 10638, 10650, 10700, 10800,
    14400, 15000, 16000, 16200, 16250, 16300, 16350, 16400, 16600, 16800, 17000, 17600, 18000, 19000, 19200,
    20000, 22000, 24000, 25000, 26000, 28800, 38400, 57600, 115200, 128000, 256000, 460800, 921600, 1000000,
    1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000,
]

def extract_packets(data_bytes):
    """
    Extract packets between 0xBE and 0xFE markers.
    Returns list of (packet_data, start_pos, end_pos) tuples.
    """
    packets = []
    start_marker = 0xBE
    end_marker = 0xFE
    
    i = 0
    while i < len(data_bytes):
        # Find start marker
        if data_bytes[i] == start_marker:
            start_pos = i
            # Find corresponding end marker
            for j in range(i + 1, len(data_bytes)):
                if data_bytes[j] == end_marker:
                    # Extract payload (exclude the markers themselves)
                    payload = data_bytes[start_pos + 1:j]
                    packets.append((payload, start_pos, j))
                    i = j + 1  # Continue from after the end marker
                    break
            else:
                # No end marker found, skip this start marker
                i += 1
        else:
            i += 1
    
    return packets

# Prompt user for mode
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

# Try each baud rate
line_counter = 0
for baud in baud_list:
    print(f"\nTrying baud rate: {baud}")
    try:
        with serial.Serial("/dev/ttyAMA0", baudrate=baud, timeout=1) as ser, open("log.txt", "a") as log:
            start = time.time()
            while time.time() - start < 25:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    line_counter += 1
                    raw = repr(data)
                    decimal_output = [str(b) for b in data]
                    hex_output = [hex(b) for b in data]
                    
                    # Extract packets between 0xBE and 0xFE markers
                    packets = extract_packets(data)
                    
                    # Log and print raw data with line number
                    log.write(f"[{line_counter:04d}] [{baud}] RAW: {raw}\n")
                    log.write(f"[{line_counter:04d}] [{baud}] DEC: {decimal_output}\n")
                    log.write(f"[{line_counter:04d}] [{baud}] HEX: {hex_output}\n")
                    log.write(f"[{line_counter:04d}] [{baud}] HEX Only: {' '.join(hex(b) for b in data)}\n")
                    
                    print(f"[{line_counter:04d}] [{baud}] RAW: {raw}")
                    print(f"[{line_counter:04d}] [{baud}] DEC: {decimal_output}")
                    print(f"[{line_counter:04d}] [{baud}] HEX: {hex_output}")
                    print(f"[{line_counter:04d}] [{baud}] HEX Only: {' '.join(hex(b) for b in data)}")
                    
                    # Process extracted packets
                    if packets:
                        print(f"[{line_counter:04d}] [{baud}] Found {len(packets)} packet(s):")
                        log.write(f"[{line_counter:04d}] [{baud}] Found {len(packets)} packet(s):\n")
                        
                        for i, (packet_data, start_pos, end_pos) in enumerate(packets):
                            print(f"[{line_counter:04d}] [{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):")
                            log.write(f"[{line_counter:04d}] [{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):\n")
                            
                            # Show packet data in hex and decimal
                            packet_hex = [hex(b) for b in packet_data]
                            packet_dec = [str(b) for b in packet_data]
                            
                            print(f"[{line_counter:04d}] [{baud}]   HEX: {packet_hex}")
                            print(f"[{line_counter:04d}] [{baud}]   DEC: {packet_dec}")
                            log.write(f"[{line_counter:04d}] [{baud}]   HEX: {packet_hex}\n")
                            log.write(f"[{line_counter:04d}] [{baud}]   DEC: {packet_dec}\n")
                            
                            print()  # Empty line for readability
                            log.write("\n")
                    else:
                        print(f"[{line_counter:04d}] [{baud}] No complete packets found (0xBE...0xFE)")
                        log.write(f"[{line_counter:04d}] [{baud}] No complete packets found (0xBE...0xFE)\n")
    except Exception as e:
        print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
