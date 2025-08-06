import serial
import time
import codecs

# Default common UART baud rates
baud_rates = [
    110, 300, 600, 1200, 2400, 4800, 9600, 10400, 10450, 10500, 10550, 10600, 10638, 10650, 10700, 10800,
    14400, 15000, 16000, 16200, 16250, 16300, 16350, 16400, 16600, 16800, 17000, 17600, 18000, 19000, 19200,
    20000, 22000, 24000, 25000, 26000, 28800, 38400, 57600, 115200, 128000, 256000, 460800, 921600, 1000000,
    1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000,
]

# Available decoding formats
decoding_formats = {
    1: ("RAW", "Raw bytes representation"),
    2: ("DEC", "Decimal array"),
    3: ("HEX", "Hexadecimal array"),
    4: ("HEX_ONLY", "Hexadecimal values only (space-separated)"),
    5: ("ASCII", "ASCII text (printable characters only)"),
    6: ("UTF8", "UTF-8 text decoding"),
    7: ("GBK", "Chinese GBK encoding"),
    8: ("GB2312", "Chinese GB2312 encoding"),
    9: ("BIG5", "Chinese Big5 encoding"),
    10: ("SHIFT_JIS", "Japanese Shift-JIS encoding"),
    11: ("EUC_JP", "Japanese EUC-JP encoding"),
    12: ("ISO_8859_1", "Latin-1 encoding"),
    13: ("BINARY", "Binary representation"),
    14: ("OCTAL", "Octal representation"),
    15: ("ALL", "All formats")
}

# Protocol constants based on PACKET.md
STANDARD_PACKET_SIZE = 28
PACKET_HEADER = [0x30, 0x36, 0x26]  # First 3 bytes of header
PACKET_TERMINATOR = [0xCE, 0xFE]     # Last 2 bytes

def extract_28byte_packets(data_bytes):
    """
    Extract 28-byte packets based on the real protocol structure.
    Returns list of (packet_data, start_pos, end_pos) tuples.
    """
    packets = []
    i = 0
    
    while i <= len(data_bytes) - STANDARD_PACKET_SIZE:
        # Check if this position starts with the expected header
        if (data_bytes[i] == PACKET_HEADER[0] and 
            data_bytes[i+1] == PACKET_HEADER[1] and 
            data_bytes[i+2] == PACKET_HEADER[2]):
            
            # Extract the potential 28-byte packet
            packet_data = data_bytes[i:i+STANDARD_PACKET_SIZE]
            
            # Verify it ends with the expected terminator
            if (packet_data[-2] == PACKET_TERMINATOR[0] and 
                packet_data[-1] == PACKET_TERMINATOR[1]):
                
                packets.append((packet_data, i, i+STANDARD_PACKET_SIZE))
                i += STANDARD_PACKET_SIZE  # Move to next potential packet
            else:
                i += 1  # Try next position
        else:
            i += 1
    
    return packets

def extract_single_byte_packets(data_bytes):
    """
    Extract single-byte control packets (common in the protocol).
    Returns list of single bytes that might be control signals.
    """
    single_bytes = []
    for i, byte in enumerate(data_bytes):
        # Look for common control bytes
        if byte in [0x00, 0x02, 0xFE, 0xFF, 0xFC]:
            single_bytes.append((bytes([byte]), i, i+1))
    return single_bytes

def analyze_packet_structure(packet_data):
    """
    Analyze the structure of a 28-byte packet according to PACKET.md.
    """
    if len(packet_data) != STANDARD_PACKET_SIZE:
        return "Invalid packet size"
    
    analysis = {
        "header": packet_data[:25],
        "data_byte": packet_data[25],  # Position 26 (0-indexed)
        "terminator": packet_data[26:28]
    }
    
    return analysis

def decode_data(data, format_type):
    """
    Decode data according to the specified format.
    """
    try:
        if format_type == "RAW":
            return repr(data)
        elif format_type == "DEC":
            return [str(b) for b in data]
        elif format_type == "HEX":
            return [hex(b) for b in data]
        elif format_type == "HEX_ONLY":
            return ' '.join(hex(b) for b in data)
        elif format_type == "ASCII":
            return ''.join(chr(b) if 32 <= b <= 126 else f'\\x{b:02x}' for b in data)
        elif format_type == "UTF8":
            return data.decode('utf-8', errors='replace')
        elif format_type == "GBK":
            return data.decode('gbk', errors='replace')
        elif format_type == "GB2312":
            return data.decode('gb2312', errors='replace')
        elif format_type == "BIG5":
            return data.decode('big5', errors='replace')
        elif format_type == "SHIFT_JIS":
            return data.decode('shift_jis', errors='replace')
        elif format_type == "EUC_JP":
            return data.decode('euc_jp', errors='replace')
        elif format_type == "ISO_8859_1":
            return data.decode('iso-8859-1', errors='replace')
        elif format_type == "BINARY":
            return ' '.join(f'{b:08b}' for b in data)
        elif format_type == "OCTAL":
            return [oct(b) for b in data]
        else:
            return f"Unknown format: {format_type}"
    except Exception as e:
        return f"Error decoding {format_type}: {e}"

def print_decoding_formats():
    """Print available decoding formats."""
    print("\nAvailable decoding formats:")
    for key, (format_name, description) in decoding_formats.items():
        print(f"{key:2d}: {format_name:<12} - {description}")

def get_user_selections():
    """Get user selections for baud rate and decoding formats."""
    # Get baud rate selection
    print("Available baud rates:")
    for i, br in enumerate(baud_rates):
        print(f"{i + 1}: {br}")
    
    try:
        index = int(input("Select baud rate number: ")) - 1
        baud = baud_rates[index]
    except:
        print("Invalid selection.")
        exit(1)
    
    # Get decoding format selections
    print_decoding_formats()
    print("\nEnter format numbers separated by commas (e.g., 1,3,5,7) or 'all' for all formats:")
    format_input = input("Select decoding formats: ").strip().lower()
    
    selected_formats = []
    if format_input == 'all':
        selected_formats = [format_name for _, (format_name, _) in decoding_formats.items()]
    else:
        try:
            format_indices = [int(x.strip()) for x in format_input.split(',')]
            for idx in format_indices:
                if idx in decoding_formats:
                    selected_formats.append(decoding_formats[idx][0])
                else:
                    print(f"Warning: Invalid format number {idx}")
        except:
            print("Invalid format selection. Using default formats.")
            selected_formats = ["RAW", "DEC", "HEX", "HEX_ONLY"]
    
    if not selected_formats:
        print("No valid formats selected. Using default formats.")
        selected_formats = ["RAW", "DEC", "HEX", "HEX_ONLY"]
    
    return baud, selected_formats

# Get user selections
baud, selected_formats = get_user_selections()

print(f"\nSelected baud rate: {baud}")
print(f"Selected formats: {', '.join(selected_formats)}")

# Try the selected baud rate
line_counter = 0
print(f"\nTrying baud rate: {baud}")
try:
    with serial.Serial("/dev/ttyAMA0", baudrate=baud, timeout=1) as ser, open("log.txt", "a") as log:
        start = time.time()
        while time.time() - start < 25:
            data = ser.read(ser.in_waiting or 1)
            if data:
                line_counter += 1
                
                # Extract 28-byte packets based on real protocol
                packets_28byte = extract_28byte_packets(data)
                
                # Extract single-byte control packets
                packets_single = extract_single_byte_packets(data)
                
                # Process each selected format
                for format_type in selected_formats:
                    decoded = decode_data(data, format_type)
                    
                    # Log and print decoded data
                    log.write(f"[{line_counter:04d}] [{baud}] {format_type}: {decoded}\n")
                    print(f"[{line_counter:04d}] [{baud}] {format_type}: {decoded}")
                
                # Process extracted 28-byte packets
                if packets_28byte:
                    print(f"[{line_counter:04d}] [{baud}] Found {len(packets_28byte)} 28-byte packet(s):")
                    log.write(f"[{line_counter:04d}] [{baud}] Found {len(packets_28byte)} 28-byte packet(s):\n")
                    
                    for i, (packet_data, start_pos, end_pos) in enumerate(packets_28byte):
                        print(f"[{line_counter:04d}] [{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):")
                        log.write(f"[{line_counter:04d}] [{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):\n")
                        
                        # Analyze packet structure
                        analysis = analyze_packet_structure(packet_data)
                        print(f"[{line_counter:04d}] [{baud}]   Structure: {analysis}")
                        log.write(f"[{line_counter:04d}] [{baud}]   Structure: {analysis}\n")
                        
                        # Show packet data in selected formats
                        for format_type in selected_formats:
                            packet_decoded = decode_data(packet_data, format_type)
                            print(f"[{line_counter:04d}] [{baud}]   {format_type}: {packet_decoded}")
                            log.write(f"[{line_counter:04d}] [{baud}]   {format_type}: {packet_decoded}\n")
                        
                        print()  # Empty line for readability
                        log.write("\n")
                
                # Process single-byte packets
                if packets_single:
                    print(f"[{line_counter:04d}] [{baud}] Found {len(packets_single)} single-byte packet(s):")
                    log.write(f"[{line_counter:04d}] [{baud}] Found {len(packets_single)} single-byte packet(s):\n")
                    
                    for i, (packet_data, start_pos, end_pos) in enumerate(packets_single):
                        print(f"[{line_counter:04d}] [{baud}] Single-byte {i+1} (pos {start_pos}): {hex(packet_data[0])}")
                        log.write(f"[{line_counter:04d}] [{baud}] Single-byte {i+1} (pos {start_pos}): {hex(packet_data[0])}\n")
                
                if not packets_28byte and not packets_single:
                    print(f"[{line_counter:04d}] [{baud}] No standard packets found")
                    log.write(f"[{line_counter:04d}] [{baud}] No standard packets found\n")
                
                print("-" * 80)  # Separator line
                log.write("-" * 80 + "\n")
except Exception as e:
    print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
