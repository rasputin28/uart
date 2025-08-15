import re
import csv
import os

def get_txt_files(dir_path):
    return [f for f in os.listdir(dir_path) if f.endswith('.txt')]

def main():
    dir_path = '.'  # current directory, or specify your 'preprocessing' folder here
    files = get_txt_files(dir_path)
    if not files:
        print("No .txt files found.")
        return

    print("Available log files:")
    for i, f in enumerate(files, 1):
        print(f"{i}: {f}")

    choice = input("Select file by number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
        print("Invalid selection")
        return

    log_file = files[int(choice)-1]
    csv_file = os.path.splitext(log_file)[0] + "_packets.csv"

    pattern = re.compile(r'\[(\d+)\]\s+\[\d+\]\s+HEX:\s+((?:[0-9a-fA-F]{2}(?:\s)?)+)')

    max_bytes = 0
    rows = []

    # Read lines, parse and store data in memory first to determine max bytes length
    with open(os.path.join(dir_path, log_file), 'r') as f_in:
        for line in f_in:
            match = pattern.search(line)
            if match:
                pkt_index = match.group(1)
                hex_bytes = match.group(2).strip().split()
                rows.append([pkt_index] + hex_bytes)
                if len(hex_bytes) > max_bytes:
                    max_bytes = len(hex_bytes)

    # Write CSV
    with open(os.path.join(dir_path, csv_file), 'w', newline='') as f_out:
        writer = csv.writer(f_out)
        header = ['PacketIndex'] + [f'Byte{i+1}' for i in range(max_bytes)]
        writer.writerow(header)

        for row in rows:
            # Pad row with empty strings if shorter than max_bytes
            row += [''] * (max_bytes - (len(row)-1))
            writer.writerow(row)

    print(f"CSV file '{csv_file}' created with {len(rows)} packets.")

if __name__ == '__main__':
    main()
