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
                    
                    # Try multiple encodings for Chinese text with error handling
                    encodings = ['utf-8', 'gb18030', 'gbk', 'big5', 'gb2312', 'latin-1', 'cp936']
                    decoded_results = {}
                    
                    def score_chinese(decoded):
                        """Score how many Chinese characters are in the decoded text"""
                        return sum(1 for ch in decoded if '\u4e00' <= ch <= '\u9fff')
                    
                    def calculate_decode_percentage(decoded, original_length):
                        """Calculate percentage of successfully decoded characters"""
                        if original_length == 0:
                            return 0.0
                        # Count replacement characters () which indicate decode failures
                        replacement_chars = decoded.count('')
                        successful_chars = original_length - replacement_chars
                        percentage = (successful_chars / original_length) * 100
                        return round(percentage, 1)
                    
                    def try_advanced_decoding(data_bytes):
                        """Try advanced decoding strategies"""
                        results = {}
                        
                        # Strategy 1: Try with different error handling
                        for enc in ['utf-8', 'gb18030', 'gbk']:
                            try:
                                # Try with 'ignore' instead of 'replace'
                                decoded_ignore = data_bytes.decode(enc, errors='ignore')
                                score_ignore = score_chinese(decoded_ignore)
                                results[f"{enc}_ignore"] = f"{decoded_ignore} [score: {score_ignore}]"
                            except:
                                pass
                        
                        # Strategy 2: Try byte-by-byte analysis for patterns
                        if len(data_bytes) > 0:
                            # Check if data starts with common patterns
                            first_byte = data_bytes[0]
                            if first_byte in [0x02, 0x03, 0x06, 0x07]:  # Common control bytes
                                results["control_analysis"] = f"Starts with control byte 0x{first_byte:02x}"
                        
                        # Strategy 3: Try different byte alignments (skip first byte if it's garbage)
                        if len(data_bytes) > 1:
                            for enc in ['utf-8', 'gbk']:
                                try:
                                    # Skip first byte and try decoding
                                    decoded_skip = data_bytes[1:].decode(enc, errors='replace')
                                    score_skip = score_chinese(decoded_skip)
                                    if score_skip > 0:
                                        results[f"{enc}_skip1"] = f"{decoded_skip} [score: {score_skip}]"
                                except:
                                    pass
                        
                        return results
                    
                    for enc in encodings:
                        try:
                            # Use errors='replace' to avoid crashes and see partial results
                            decoded = data.decode(enc, errors='replace')
                            score = score_chinese(decoded)
                            percentage = calculate_decode_percentage(decoded, len(data))
                            decoded_results[enc] = f"{decoded} [score: {score}, decode: {percentage}%]"
                        except Exception as e:
                            decoded_results[enc] = f"[decode failed: {e}]"
                    
                    # Try advanced decoding strategies
                    advanced_results = try_advanced_decoding(data)
                    decoded_results.update(advanced_results)
                    
                    # Log and print all results
                    log.write(f"[{baud}] RAW: {raw}\n")
                    log.write(f"[{baud}] DEC: {decimal_output}\n")
                    log.write(f"[{baud}] HEX: {hex_output}\n")
                    log.write(f"[{baud}] HEX Only: {' '.join(hex(b) for b in data)}\n")
                    for enc, result in decoded_results.items():
                        log.write(f"[{baud}] DEC ({enc}): {result}\n")
                    
                    print(f"[{baud}] RAW: {raw}")
                    print(f"[{baud}] DEC: {decimal_output}")
                    print(f"[{baud}] HEX: {hex_output}")
                    print(f"[{baud}] HEX Only: {' '.join(hex(b) for b in data)}")
                    for enc, result in decoded_results.items():
                        print(f"[{baud}] DEC ({enc}): {result}")
    except Exception as e:
        print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
