import serial
import time
import codecs
from collections import deque

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

# Known packet patterns for better detection
KNOWN_PACKET_PATTERNS = {
    "28byte_standard": {
        "header": [0x30, 0x36, 0x26],
        "size": 28,
        "terminator": [0xCE, 0xFE],
        "description": "Standard 28-byte packet"
    },
    "28byte_alt_terminator": {
        "header": [0x30, 0x36, 0x26],
        "size": 28,
        "terminator": [0xCE, 0xFF],
        "description": "28-byte packet with error terminator"
    },
    "partial_28byte": {
        "header": [0x30, 0x36, 0x26],
        "min_size": 10,
        "max_size": 27,
        "description": "Partial 28-byte packet"
    }
}

class PacketDetector:
    """
    Advanced packet detector that can handle multiple packet types,
    partial packets, and provides detailed analysis.
    """
    
    def __init__(self):
        self.buffer = deque()  # Buffer for partial packets
        self.packet_history = []  # Track packet patterns
        self.stats = {
            "total_bytes": 0,
            "packets_found": 0,
            "partial_packets": 0,
            "single_bytes": 0,
            "unknown_patterns": 0
        }
    
    def add_data(self, data_bytes):
        """Add new data to the buffer and process for packets."""
        self.buffer.extend(data_bytes)
        self.stats["total_bytes"] += len(data_bytes)
        
        packets = []
        
        # Process complete packets
        while len(self.buffer) >= 3:  # Minimum header size
            packet = self._extract_next_packet()
            if packet:
                packets.append(packet)
            else:
                break
        
        return packets
    
    def _extract_next_packet(self):
        """Extract the next complete packet from the buffer."""
        if len(self.buffer) < 3:
            return None
        
        # Look for known packet patterns
        for pattern_name, pattern in KNOWN_PACKET_PATTERNS.items():
            packet = self._try_extract_pattern(pattern_name, pattern)
            if packet:
                return packet
        
        # Look for single-byte packets
        single_byte = self._try_extract_single_byte()
        if single_byte:
            return single_byte
        
        # If no pattern matches, remove one byte and try again
        self.buffer.popleft()
        return None
    
    def _try_extract_pattern(self, pattern_name, pattern):
        """Try to extract a packet matching the given pattern."""
        if len(self.buffer) < len(pattern["header"]):
            return None
        
        # Check header
        for i, expected in enumerate(pattern["header"]):
            if self.buffer[i] != expected:
                return None
        
        # For complete packets, check size and terminator
        if "size" in pattern:
            if len(self.buffer) < pattern["size"]:
                return None  # Not enough data yet
            
            packet_data = list(self.buffer)[:pattern["size"]]
            
            # Check terminator
            if "terminator" in pattern:
                terminator = pattern["terminator"]
                if (packet_data[-len(terminator)] != terminator[0] or 
                    packet_data[-len(terminator)+1] != terminator[1]):
                    return None
            
            # Extract the packet
            packet_bytes = bytes(packet_data)
            for _ in range(pattern["size"]):
                self.buffer.popleft()
            
            self.stats["packets_found"] += 1
            return {
                "type": pattern_name,
                "data": packet_bytes,
                "size": len(packet_bytes),
                "description": pattern["description"],
                "analysis": self._analyze_packet(packet_bytes, pattern_name)
            }
        
        # For partial packets
        elif "min_size" in pattern and "max_size" in pattern:
            if len(self.buffer) >= pattern["min_size"]:
                # Extract what we have
                packet_data = list(self.buffer)[:pattern["max_size"]]
                packet_bytes = bytes(packet_data)
                
                # Remove the data we processed
                for _ in range(len(packet_data)):
                    self.buffer.popleft()
                
                self.stats["partial_packets"] += 1
                return {
                    "type": pattern_name,
                    "data": packet_bytes,
                    "size": len(packet_bytes),
                    "description": f"Partial {pattern['description']}",
                    "analysis": self._analyze_partial_packet(packet_bytes)
                }
        
        return None
    
    def _try_extract_single_byte(self):
        """Try to extract a single-byte control packet."""
        if not self.buffer:
            return None
        
        byte = self.buffer[0]
        
        # Check if this could be a valid single-byte packet
        if byte in [0x00, 0x02, 0xFE, 0xFF, 0xFC, 0x01]:
            # Validate context
            is_valid = self._validate_single_byte_context(byte)
            if is_valid:
                self.buffer.popleft()
                self.stats["single_bytes"] += 1
                return {
                    "type": "single_byte",
                    "data": bytes([byte]),
                    "size": 1,
                    "description": "Single-byte control packet",
                    "analysis": self._analyze_single_byte(byte)
                }
        
        return None
    
    def _validate_single_byte_context(self, byte):
        """Validate if a single byte is likely a control packet."""
        # Case 1: Isolated single byte
        if len(self.buffer) > 1:
            next_byte = self.buffer[1]
            if next_byte not in [0x00, 0x02, 0xFE, 0xFF, 0xFC]:
                return True
        
        # Case 2: At start of buffer
        if len(self.buffer) == 1:
            return True
        
        # Case 3: Part of control sequence
        if len(self.buffer) > 1 and self.buffer[1] in [0xFE, 0xFF]:
            return True
        
        return False
    
    def _analyze_packet(self, packet_data, pattern_name):
        """Analyze a complete packet."""
        if pattern_name == "28byte_standard" or pattern_name == "28byte_alt_terminator":
            return self._analyze_28byte_packet(packet_data)
        else:
            return {"raw_data": list(packet_data)}
    
    def _analyze_28byte_packet(self, packet_data):
        """Analyze a 28-byte packet according to PACKET.md."""
        if len(packet_data) != 28:
            return {"error": "Invalid packet size"}
        
        analysis = {
            "header": list(packet_data[:25]),
            "data_byte": packet_data[25],  # Position 26 (0-indexed)
            "terminator": list(packet_data[26:28]),
            "data_byte_hex": hex(packet_data[25]),
            "data_byte_decimal": packet_data[25]
        }
        
        # Analyze the data byte
        if packet_data[25] == 0x30:
            analysis["data_byte_meaning"] = "Normal state"
        elif packet_data[25] == 0x32:
            analysis["data_byte_meaning"] = "Alternate state"
        elif packet_data[25] == 0xF0:
            analysis["data_byte_meaning"] = "Occasional variation"
        elif packet_data[25] == 0xFE:
            analysis["data_byte_meaning"] = "Rare variation"
        elif packet_data[25] == 0xFF:
            analysis["data_byte_meaning"] = "Possible error indicator"
        else:
            analysis["data_byte_meaning"] = "Unknown"
        
        # Analyze terminator
        if packet_data[26:28] == [0xCE, 0xFE]:
            analysis["terminator_type"] = "Standard"
        elif packet_data[26:28] == [0xCE, 0xFF]:
            analysis["terminator_type"] = "Error condition"
        else:
            analysis["terminator_type"] = "Unknown"
        
        return analysis
    
    def _analyze_partial_packet(self, packet_data):
        """Analyze a partial packet."""
        return {
            "partial_size": len(packet_data),
            "has_header": len(packet_data) >= 3 and packet_data[:3] == [0x30, 0x36, 0x26],
            "raw_data": list(packet_data)
        }
    
    def _analyze_single_byte(self, byte_value):
        """Analyze a single-byte packet."""
        analysis = {
            "value": hex(byte_value),
            "decimal": byte_value,
            "likely_purpose": "Unknown"
        }
        
        # Based on PACKET.md analysis
        if byte_value == 0x02:
            analysis["likely_purpose"] = "Acknowledgment (ACK)"
        elif byte_value == 0xFE:
            analysis["likely_purpose"] = "Status update"
        elif byte_value == 0xFF:
            analysis["likely_purpose"] = "Error indicator"
        elif byte_value == 0x00:
            analysis["likely_purpose"] = "Null/empty"
        elif byte_value == 0xFC:
            analysis["likely_purpose"] = "Flow control"
        elif byte_value == 0x01:
            analysis["likely_purpose"] = "Control signal"
        
        return analysis
    
    def get_stats(self):
        """Get current statistics."""
        return self.stats.copy()
    
    def get_buffer_status(self):
        """Get current buffer status."""
        return {
            "buffer_size": len(self.buffer),
            "buffer_contents": list(self.buffer)
        }

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
    Extract single-byte control packets based on protocol analysis.
    Returns list of validated single-byte packets.
    """
    single_bytes = []
    i = 0
    
    while i < len(data_bytes):
        byte = data_bytes[i]
        
        # Check if this could be a single-byte control packet
        # Based on PACKET.md analysis of common single-byte packets
        if byte in [0x00, 0x02, 0xFE, 0xFF, 0xFC]:
            
            # Additional validation: check context
            is_valid_single_byte = False
            
            # Case 1: Isolated single byte (surrounded by non-control bytes)
            if i > 0 and i < len(data_bytes) - 1:
                prev_byte = data_bytes[i-1]
                next_byte = data_bytes[i+1]
                
                # If surrounded by non-control bytes, likely a control packet
                if prev_byte not in [0x00, 0x02, 0xFE, 0xFF, 0xFC] and \
                   next_byte not in [0x00, 0x02, 0xFE, 0xFF, 0xFC]:
                    is_valid_single_byte = True
            
            # Case 2: At start of data stream
            elif i == 0:
                is_valid_single_byte = True
            
            # Case 3: At end of data stream  
            elif i == len(data_bytes) - 1:
                is_valid_single_byte = True
            
            # Case 4: Part of a sequence of control bytes (like 0xFE 0xFE)
            elif i > 0 and data_bytes[i-1] in [0xFE, 0xFF]:
                is_valid_single_byte = True
            
            if is_valid_single_byte:
                single_bytes.append((bytes([byte]), i, i+1))
        
        i += 1
    
    return single_bytes

def analyze_single_byte_packet(byte_value):
    """
    Analyze a single-byte packet based on PACKET.md documentation.
    """
    analysis = {
        "value": hex(byte_value),
        "decimal": byte_value,
        "likely_purpose": "Unknown"
    }
    
    # Based on PACKET.md analysis
    if byte_value == 0x02:
        analysis["likely_purpose"] = "Acknowledgment (ACK)"
    elif byte_value == 0xFE:
        analysis["likely_purpose"] = "Status update"
    elif byte_value == 0xFF:
        analysis["likely_purpose"] = "Error indicator"
    elif byte_value == 0x00:
        analysis["likely_purpose"] = "Null/empty"
    elif byte_value == 0xFC:
        analysis["likely_purpose"] = "Flow control"
    elif byte_value == 0x01:
        analysis["likely_purpose"] = "Control signal"
    
    return analysis

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

# Initialize the advanced packet detector
detector = PacketDetector()

try:
    with serial.Serial("/dev/ttyAMA0", baudrate=baud, timeout=1) as ser, open("log.txt", "a") as log:
        start = time.time()
        while time.time() - start < 25:
            data = ser.read(ser.in_waiting or 1)
            if data:
                line_counter += 1
                
                # Use the advanced packet detector
                packets = detector.add_data(data)
                
                # Output hex only for raw data
                hex_data = decode_data(data, "HEX_ONLY")
                log.write(f"[{line_counter:04d}] [{baud}] HEX: {hex_data}\n")
                print(f"[{line_counter:04d}] [{baud}] HEX: {hex_data}")
        
        # Show final statistics
        stats = detector.get_stats()
        print(f"\nFinal Statistics:")
        print(f"  Total bytes processed: {stats['total_bytes']}")
        print(f"  Complete packets found: {stats['packets_found']}")
        print(f"  Partial packets found: {stats['partial_packets']}")
        print(f"  Single-byte packets: {stats['single_bytes']}")
        print(f"  Unknown patterns: {stats['unknown_patterns']}")
        
        log.write(f"\nFinal Statistics:\n")
        log.write(f"  Total bytes processed: {stats['total_bytes']}\n")
        log.write(f"  Complete packets found: {stats['packets_found']}\n")
        log.write(f"  Partial packets found: {stats['partial_packets']}\n")
        log.write(f"  Single-byte packets: {stats['single_bytes']}\n")
        log.write(f"  Unknown patterns: {stats['unknown_patterns']}\n")
        
except Exception as e:
    print(f"[{baud}] Error: {e}")

print("\nDone. Check log.txt for full output.")
