from constant import *
import os
from tqdm import tqdm
import json

class PartitionLayer:
    def __init__(self, size: int, location_map: dict):
        self._size : int = size
        self._location_map : dict = location_map
        self._file_mapper : dict = {}
        for i in range(size):
            self._file_mapper[i] = open(RES_PATH + "/" + str(i) + ".par.json", "w")
    
    def close(self):
        for key in self._file_mapper:
            self._file_mapper[key].close()
    
    def flush(self):
        for key in self._file_mapper:
            self._file_mapper[key].close()
            self._file_mapper[key] = open(RES_PATH + "/" + str(key) + ".par.json", "a")
    
    def writeline(self, key: str, arr: list):
        idx: int = self._location_map[key]
        self._file_mapper[idx].write(json.dumps({key: arr}) + "\n")


if __name__ == "__main__":

    files = sorted(os.listdir(OUTPUT_PATH))

    pl = None
    with open(MAC_FILE_LOCATION, "r") as f:
        pl = PartitionLayer(PARTITION_NUM, json.loads(f.read()))

    for file_idx in tqdm(range(len(files)),desc="Joining files"):
        mp1 = None
        with open(OUTPUT_PATH + "/" + files[file_idx], "r") as f:
            mp1 = json.loads(f.read())
        
        for mac in tqdm(mp1, desc="Mac addresses scanned", leave=False):
            pl.writeline(mac, mp1[mac])
        pl.flush()
    pl.close()