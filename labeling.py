from constant import *
import pandas as pd
import numpy as np
import json
from datetime import datetime
import os
from tqdm import tqdm

if __name__ == "__main__":
    data = pd.read_csv("vendor_clusters.csv", sep=',')
    mobile = data[data['cluster'] != 0].reset_index()
    mobile_mac_address = set(mobile['0'])
    g = 0
    k = 0
    abnormal = set()
    wrong_floor = {}
    # start labelling abnormal behavior based on our rules
    for data_file in tqdm(os.listdir(RES_PATH)):
        local_dict = dict()
        with open(RES_PATH + "/" + data_file, "r") as f:
            # read each line in one json
            for line in f:
                data = json.loads(line)
                # build a dictionary called local_dict to save {macaddress: [all data points in this file for this macaddr]}
                for key, value in data.items():
                    if key in mobile_mac_address:
                        if key in local_dict:
                            local_dict[key].extend(value)
                        else:
                            local_dict[key] = value
        # abnormal behavior rules:
        
        for key in local_dict:
            appearence = [0]*4
            for value in local_dict[key]:
                if value[0] == "Ground Floor":
                    appearence[1] += 1
                elif value[0] == "1st Floor":
                    appearence[1] += 1
                elif value[0] == "2nd Floor":
                    appearence[2] += 1
                else:
                    appearence[3] += 1
            total_app = sum(appearence)
            if total_app <= 500:
                g += 1
                abnormal.add(key)
            else:
                for i in range(4):
                    if 0 < appearence[i] / total_app < 0.0005:
                        abnormal.add(key)
                        if key not in wrong_floor:
                            wrong_floor[key] = []
                        wrong_floor[key].append(i)
            
        for key in local_dict:
            local_dict[key].sort(key = lambda x : x[1])
            count_days = 0
            start_day = datetime.utcfromtimestamp(local_dict[key][0][1]).day
            start_month = datetime.utcfromtimestamp(local_dict[key][0][1]).month
            start_year = datetime.utcfromtimestamp(local_dict[key][0][1]).year
            for _, t, _, _ in local_dict[key]:
                dt = datetime.utcfromtimestamp(t)
                if dt.day != start_day or dt.month != start_month or dt.year != start_year:
                    start_day = dt.day
                    start_month = dt.month
                    start_year = dt.year
                    count_days += 1
            if count_days < 2:
                if 7 <= datetime.utcfromtimestamp(local_dict[key][0][1]).hour <= 14 \
                    or 10 <= datetime.utcfromtimestamp(local_dict[key][-1][1]).hour <= 14:
                    abnormal.add(key)
                    k += 1

    with open("abnormal_mac.json", "w") as f:
        f.write(json.dumps(list(abnormal)))
    
    with open("wrong_floor.json", "w") as f:
        f.write(json.dumps(wrong_floor))
    
    
    