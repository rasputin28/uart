import serial
import time

# Default common UART baud rates
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

def analyze_packet_structure(packet_data):
    """
    Analyze the structure of a packet to understand its format.
    """
    if not packet_data:
        return "Empty packet"
    
    analysis = []
    
    # Check packet length
    analysis.append(f"Length: {len(packet_data)} bytes")
    
    # Check for common patterns
    if len(packet_data) >= 1:
        first_byte = packet_data[0]
        analysis.append(f"First byte: 0x{first_byte:02x} ({first_byte})")
        
        # Common command patterns
        if 0x01 <= first_byte <= 0x7F:
            analysis.append(f"Possible command byte: 0x{first_byte:02x}")
    
    # Check for length field (common in protocols)
    if len(packet_data) >= 2:
        second_byte = packet_data[1]
        analysis.append(f"Second byte: 0x{second_byte:02x} ({second_byte})")
        
        # If second byte matches packet length, it might be a length field
        if second_byte == len(packet_data):
            analysis.append("Second byte appears to be length field")
    
    # Check for checksum (last byte often contains checksum)
    if len(packet_data) >= 2:
        last_byte = packet_data[-1]
        analysis.append(f"Last byte: 0x{last_byte:02x} ({last_byte})")
        
        # Simple checksum calculation
        calculated_checksum = sum(packet_data[:-1]) & 0xFF
        if calculated_checksum == last_byte:
            analysis.append("Last byte appears to be checksum (simple sum)")
    
    # Try to identify data types
    ascii_chars = sum(1 for b in packet_data if 32 <= b <= 126)
    if ascii_chars > len(packet_data) * 0.7:  # More than 70% printable ASCII
        analysis.append("Packet appears to contain mostly ASCII text")
    
    return " | ".join(analysis)

def decode_packet_payload(packet_data):
    """
    Try multiple decoding strategies for packet payload.
    """
    if not packet_data:
        return {"error": "Empty packet"}
    
    results = {}
    
    # Try different encodings
    encodings = ['utf-8', 'gb18030', 'gbk', 'big5', 'gb2312', 'latin-1', 'cp936']
    
    for enc in encodings:
        try:
            decoded = packet_data.decode(enc, errors='replace')
            # Count Chinese characters
            chinese_chars = sum(1 for ch in decoded if '\u4e00' <= ch <= '\u9fff')
            # Count replacement characters (decode failures)
            replacement_chars = decoded.count('')
            success_rate = ((len(decoded) - replacement_chars) / len(decoded)) * 100 if decoded else 0
            
            results[enc] = {
                'text': decoded,
                'chinese_chars': chinese_chars,
                'success_rate': round(success_rate, 1),
                'replacement_chars': replacement_chars
            }
        except Exception as e:
            results[enc] = {'error': str(e)}
    
    return results

# Prompt user for mode
# mode = input("Select mode: [a]uto baud detect or [m]anual selection? ").strip().lower()

# if mode == 'm':
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
# else:
#     print("Running auto baud rate scan (10s each)...")
#     baud_list = baud_rates

# Try each baud rate
for baud in baud_list:
    print(f"\nTrying baud rate: {baud}")
    try:
        with serial.Serial("/dev/ttyAMA0", baudrate=baud, timeout=1) as ser, open("log.txt", "a") as log:
            start = time.time()
            while time.time() - start < 25:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    raw = repr(data)
                    decimal_output = [str(b) for b in data]
                    hex_output = [hex(b) for b in data]
                    
                    # Extract packets between 0xBE and 0xFE markers
                    packets = extract_packets(data)
                    
                    # Log and print raw data
                    log.write(f"[{baud}] RAW: {raw}\n")
                    log.write(f"[{baud}] DEC: {decimal_output}\n")
                    log.write(f"[{baud}] HEX: {hex_output}\n")
                    log.write(f"[{baud}] HEX Only: {' '.join(hex(b) for b in data)}\n")
                    
                    print(f"[{baud}] RAW: {raw}")
                    print(f"[{baud}] DEC: {decimal_output}")
                    print(f"[{baud}] HEX: {hex_output}")
                    print(f"[{baud}] HEX Only: {' '.join(hex(b) for b in data)}")
                    
                    # Process extracted packets
                    if packets:
                        print(f"[{baud}] Found {len(packets)} packet(s):")
                        log.write(f"[{baud}] Found {len(packets)} packet(s):\n")
                        
                        for i, (packet_data, start_pos, end_pos) in enumerate(packets):
                            print(f"[{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):")
                            log.write(f"[{baud}] Packet {i+1} (pos {start_pos}-{end_pos}):\n")
                            
                            # Analyze packet structure
                            structure_analysis = analyze_packet_structure(packet_data)
                            print(f"[{baud}]   Structure: {structure_analysis}")
                            log.write(f"[{baud}]   Structure: {structure_analysis}\n")
                            
                            # Decode packet payload
                            decode_results = decode_packet_payload(packet_data)
                            
                            # Show best decoding results
                            best_encoding = None
                            best_score = -1
                            
                            for enc, result in decode_results.items():
                                if 'error' not in result:
                                    # Prioritize high success rate and Chinese characters
                                    score = result['success_rate'] + (result['chinese_chars'] * 10)
                                    if score > best_score:
                                        best_score = score
                                        best_encoding = enc
                            
                            if best_encoding:
                                best_result = decode_results[best_encoding]
                                print(f"[{baud}]   Best decode ({best_encoding}): {best_result['text']}")
                                print(f"[{baud}]   Success rate: {best_result['success_rate']}%, Chinese chars: {best_result['chinese_chars']}")
                                log.write(f"[{baud}]   Best decode ({best_encoding}): {best_result['text']}\n")
                                log.write(f"[{baud}]   Success rate: {best_result['success_rate']}%, Chinese chars: {best_result['chinese_chars']}\n")
                            
                            # Show all decoding attempts for debugging
                            print(f"[{baud}]   All decode attempts:")
                            log.write(f"[{baud}]   All decode attempts:\n")
                            for enc, result in decode_results.items():
                                if 'error' in result:
                                    print(f"[{baud}]     {enc}: {result['error']}")
                                    log.write(f"[{baud}]     {enc}: {result['error']}\n")
                                else:
                                    print(f"[{baud}]     {enc}: {result['text']} (success: {result['success_rate']}%, Chinese: {result['chinese_chars']})")
                                    log.write(f"[{baud}]     {enc}: {result['text']} (success: {result['success_rate']}%, Chinese: {result['chinese_chars']})\n")
                            
                            print()  # Empty line for readability
                            log.write("\n")
                    else:
                        print(f"[{baud}] No complete packets found (0xBE...0xFE)")
                        log.write(f"[{baud}] No complete packets found (0xBE...0xFE)\n")
    except Exception as e:
        print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
