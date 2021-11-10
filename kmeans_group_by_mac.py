from constant import *
import os
from datetime import datetime
from tqdm import tqdm
import json

def parse_line(s: str):
    site, level, client_mac_addr, lat, lng, localtime = s.rstrip().split(",")
    try:
        localtime = datetime.strptime(localtime, "%Y-%m-%d %H:%M:%S.%f %Z")
    except:
        localtime = datetime.strptime(localtime, "%Y-%m-%d %H:%M:%S %Z")
    return client_mac_addr, level, localtime.timestamp(),lat, lng

if __name__ == "__main__":

    counter = 0
    print("Processing files")
    for data_file in tqdm(os.listdir(DATA_PATH)):
        mp = {}
        with open(DATA_PATH + "/" + data_file, "r") as f:
            line: str = f.readline()
            line = f.readline()
            while line:
                client_mac_addr, level, localtime,lat, lng = parse_line(line)
                if client_mac_addr not in mp:
                    mp[client_mac_addr] = []
                mp[client_mac_addr].append((level, localtime, lat, lng))
                line = f.readline()
        with open(OUTPUT_PATH + "/" + str(counter) + ".tmp.json", "w") as f:
            f.write(json.dumps(mp))
        counter += 1
    
    



