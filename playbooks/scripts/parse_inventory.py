#!/usr/bin/env python3
import csv
import json
import sys
import os

def parse_csv(file_path):
    hosts = []
    if not os.path.exists(file_path):
        return hosts

    with open(file_path, 'r') as f:
        lines = f.readlines()

    if len(lines) < 2:
        return hosts
        
    # Skip header
    data_lines = lines[1:]
    
    # Filter comments and empty lines
    valid_lines = [line for line in data_lines if line.strip() and not line.strip().startswith('#')]
    
    reader = csv.reader(valid_lines)
    
    for row in reader:
        # The CSV has 3 columns; type,name,ip.
        if len(row) < 3:
            continue
            
        hostname = row[1].strip()
        ip = row[2].strip()
        
        if hostname and ip:
            hosts.append({
                "hostname": hostname,
                "ip": ip,
                "fqdn": f"{hostname}.personal.systems"
            })
            
    return hosts

if __name__ == "__main__":

    csv_path = sys.argv[1]
    try:
        hosts_data = parse_csv(csv_path)
        print(json.dumps(hosts_data))
    except Exception as e:
        # In case of error, print empty list to not break ansible JSON parsing immediately,
        # or handle it better. For now, strict failure might be better but let's just return empty and log to stderr
        sys.stderr.write(f"Error parsing CSV: {e}\n")
        print(json.dumps([]))
        sys.exit(1)
