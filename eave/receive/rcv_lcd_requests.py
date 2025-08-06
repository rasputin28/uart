import binascii
import serial
import datetime

# Configuration for variable-length packet protocol
BAUD_RATE = 16250
READ_TIMEOUT = 30
SERIAL_PORT = '/dev/ttyAMA0'  # LCD side

# Packet markers
START_MARKER = 0xBE
END_MARKER = 0xFE

# State variables
packet_buffer = bytearray()
in_packet = False
last_frame = datetime.datetime.now()
packet_counter = 0

def decode_flag(byte_val, position):
    return byte_val >> position & b'\x01'[0]

def decode_short(short_bytes):
    return int.from_bytes(short_bytes, byteorder='big')

def analyze_lcd_packet(packet_data):
    """
    Analyze LCD packet structure based on your protocol
    """
    if len(packet_data) < 1:
        return "Invalid packet (too short)"
    
    # Common LCD packet patterns from your logs
    if packet_data.startswith(b'\xCC'):  # Power command
        return f"LCD Power command: {[hex(b) for b in packet_data]}"
    
    elif packet_data.startswith(b'\xC2'):  # Control command
        return f"LCD Control command: {[hex(b) for b in packet_data]}"
    
    elif packet_data.startswith(b'\x42'):  # Status/response
        return f"LCD Status: {[hex(b) for b in packet_data]}"
    
    elif packet_data.startswith(b'\xCE'):  # Header data
        return f"LCD Header: {[hex(b) for b in packet_data]}"
    
    else:
        return f"LCD Unknown command: {[hex(b) for b in packet_data]}"

def extract_lcd_packet_info(packet_data):
    """
    Extract meaningful information from LCD packet
    """
    info = {
        'length': len(packet_data),
        'hex': [hex(b) for b in packet_data],
        'decimal': [str(b) for b in packet_data],
        'command_type': 'unknown',
        'parameters': []
    }
    
    if len(packet_data) >= 1:
        first_byte = packet_data[0]
        if first_byte == 0xCC:
            info['command_type'] = 'lcd_power'
        elif first_byte == 0xC2:
            info['command_type'] = 'lcd_control'
        elif first_byte == 0x42:
            info['command_type'] = 'lcd_status'
        elif first_byte == 0xCE:
            info['command_type'] = 'lcd_header'
        
        # Extract parameters (everything after first byte)
        if len(packet_data) > 1:
            info['parameters'] = [hex(b) for b in packet_data[1:]]
    
    return info

print(f"Starting LCD variable-length packet receiver on {SERIAL_PORT}")
print(f"Baud rate: {BAUD_RATE}")
print(f"Looking for packets between 0x{START_MARKER:02X} and 0x{END_MARKER:02X} markers")
print("=" * 60)

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=READ_TIMEOUT) as ser:
    while (byte := ser.read(1)):
        current_byte = byte[0]
        
        # Check for start marker
        if current_byte == START_MARKER:
            if in_packet:
                print(f"Warning: New start marker while already in packet")
            in_packet = True
            packet_buffer.clear()
            continue
        
        # Check for end marker
        elif current_byte == END_MARKER:
            if in_packet:
                in_packet = False
                packet_counter += 1
                
                # Process complete packet
                curr_time = datetime.datetime.now()
                delta_time = curr_time - last_frame
                last_frame = curr_time
                
                print(f"\n[LCD Packet {packet_counter}] Time: {delta_time}")
                print(f"Raw packet: {' '.join(hex(b) for b in packet_buffer)}")
                
                # Analyze packet
                packet_info = extract_lcd_packet_info(packet_buffer)
                analysis = analyze_lcd_packet(packet_buffer)
                
                print(f"Length: {packet_info['length']} bytes")
                print(f"Type: {packet_info['command_type']}")
                print(f"Analysis: {analysis}")
                print(f"Hex: {packet_info['hex']}")
                print(f"Decimal: {packet_info['decimal']}")
                if packet_info['parameters']:
                    print(f"Parameters: {packet_info['parameters']}")
                print("-" * 40)
                
                packet_buffer.clear()
            else:
                print(f"Warning: End marker without start marker")
        
        # Add byte to packet buffer if we're in a packet
        elif in_packet:
            packet_buffer.append(current_byte)
        
        # Ignore bytes outside of packets
        else:
            pass

print(f"\nReceived {packet_counter} complete LCD packets")