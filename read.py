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
                
                # Extract packets between 0xBE and 0xFE markers
                packets = extract_packets(data)
                
                # Process each selected format
                for format_type in selected_formats:
                    decoded = decode_data(data, format_type)
                    
                    # Log and print decoded data
                    log.write(f"[{line_counter:04d}] [{baud}] {format_type}: {decoded}\n")
                    print(f"[{line_counter:04d}] [{baud}] {format_type}: {decoded}")
                
                # Process extracted packets
                if packets:
                    print(f"[{line_counter:04d}] [{baud}] Found {len(packets)} packet(s):")
                    log.write(f"[{line_counter:04d}] [{baud}] Found {len(packets)} packet(s):\n")
                    
                    for i, (packet_data, start_pos, end_pos) in enumerate(packets):
                        print(f"[{line_counter:04d}] [{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):")
                        log.write(f"[{line_counter:04d}] [{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):\n")
                        
                        # Show packet data in selected formats
                        for format_type in selected_formats:
                            packet_decoded = decode_data(packet_data, format_type)
                            print(f"[{line_counter:04d}] [{baud}]   {format_type}: {packet_decoded}")
                            log.write(f"[{line_counter:04d}] [{baud}]   {format_type}: {packet_decoded}\n")
                        
                        print()  # Empty line for readability
                        log.write("\n")
                else:
                    print(f"[{line_counter:04d}] [{baud}] No complete packets found (0xBE...0xFE)")
                    log.write(f"[{line_counter:04d}] [{baud}] No complete packets found (0xBE...0xFE)\n")
                
                print("-" * 80)  # Separator line
                log.write("-" * 80 + "\n")
except Exception as e:
    print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
