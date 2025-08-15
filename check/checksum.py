# Packets
packet1 = [
    0x30, 0x36, 0x26, 0x00, 0x0c, 0x30, 0x02, 0x00, 0xfc,
    0x30, 0x00, 0x80, 0x32, 0x00, 0x32, 0x30, 0x00, 0x30,
    0x82, 0x40, 0x00, 0x30, 0x0e, 0x00, 0x00, 0x32, 0x30,
    0x3e, 0xfe
]

packet2 = [
    0x30, 0x36, 0x26, 0x00, 0x0c, 0x30, 0x02, 0x02, 0xc0, 0xfc,
    0x30, 0x00, 0x80, 0x32, 0x00, 0x32, 0x30, 0x00, 0x30, 0x82,
    0x40, 0x00, 0x30, 0x0e, 0x00, 0x00, 0x32, 0x30, 0x0c
]

packet3 = [
    0x30, 0x36, 0x26, 0x00, 0x0c, 0x30, 0x02, 0x00, 0x7e,
    0x30, 0x00, 0x30, 0x42, 0x00, 0x32, 0x30, 0x00, 0x30,
    0x82, 0x40, 0x00, 0xbc, 0x0c, 0x00, 0x00, 0x32, 0x30,
    0xb2
]

def xor_checksum(bytes_seq):
    xor_val = 0
    for b in bytes_seq:
        xor_val ^= b
    return xor_val

def calculate_checksums(packet, config_start=6, config_end=9, checksum_len=2, algo='xor'):
    config_bytes = packet[config_start:config_end]
    rest_bytes = packet[:config_start] + packet[config_end:-checksum_len]
    checksum_bytes = packet[-checksum_len:]
    
    if algo == 'xor':
        xor_config = xor_checksum(config_bytes)
        xor_rest = xor_checksum(rest_bytes)
        print(f"XOR of config bytes: {xor_config:#04x}")
        print(f"XOR of rest bytes: {xor_rest:#04x}")
        print(f"Checksum bytes from packet: {[hex(b) for b in checksum_bytes]}")
    else:
        print(f"Unsupported algorithm: {algo}")

if __name__ == "__main__":
    packets = {
        'test1': packet1,
        'test2': packet2,
        'test3': packet3,
    }

    selection_map = {
        '1': 'test1',
        '2': 'test2',
        '3': 'test3',
        'test1': 'test1',
        'test2': 'test2',
        'test3': 'test3',
    }
    
    print("Select packet to analyze: 1/test1, 2/test2, 3/test3")
    selection_input = input("> ").strip().lower()
    selection = selection_map.get(selection_input)
    
    if not selection:
        print("Invalid packet selection")
        exit(1)
    
    print("Select checksum algorithm (xor):")
    algo = input("> ").strip().lower()
    if algo == '':
        algo = 'xor'  # default to xor if empty input
    
    # Default checksum length 2 bytes for tests 1 and 3, 1 byte for test2 (adjust if needed)
    checksum_len = 2
    if selection == 'test2':
        checksum_len = 1
    
    calculate_checksums(packets[selection], checksum_len=checksum_len, algo=algo)
