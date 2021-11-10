from tqdm import tqdm
import os
from constant import *
import json
from random import randint, seed

if __name__ == "__main__":

    mp = {}

    seed(996)

    for file in tqdm(os.listdir(OUTPUT_PATH)):
        with open(OUTPUT_PATH + "/" + file, "r") as f:
            data = json.loads(f.read())
            for mac in data:
                if mac not in mp:
                    mp[mac] = randint(0,PARTITION_NUM - 1)
                
    print("Number of unique mac address: " + str(len(mp)))
    with open(MAC_FILE_LOCATION, "w") as f:
        f.write(json.dumps(mp))
