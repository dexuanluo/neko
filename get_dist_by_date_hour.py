import pandas as pd
import numpy as np
import os
from datetime import datetime
import os
from constant import *
import json
from tqdm import tqdm
import haversine as hs

def floor_to_int(value: str) -> int:
    if value == "Ground Floor":
        return 0
    elif value == "1st Floor":
        return 1
    elif value == "2nd Floor":
        return 2
    return 3

def hour_floor_index_map(hour: int, floor: int) -> int:
    return hour * 4 + floor

def date_tuple_to_idx(date: tuple) -> int:
    return date[0] * 10000 + date[1] * 100 + date[2]

if __name__ == "__main__":

    mobile = set()

    with open("vendor_clusters.csv", "r") as f:
        line = f.readline()
        line = f.readline()
        while line:
            l = line.split(",")
            mobile.add(l[1])
            line = f.readline()

    
    file_count = 0
    # traverse each json file
    for data_file in tqdm(os.listdir(RES_PATH)):
        file_count += 1
        local_dict = {}
        df = {}
        with open(RES_PATH + "/" + data_file, "r") as f:
            # read each line in one json
            for line in f:
                data = json.loads(line)
                # build a dictionary called local_dict to save {macaddress: [all data points in this file for this macaddr]}
                for key, value in data.items():
                    if key in mobile:
                        if key in local_dict:
                            local_dict[key].extend(value)
                        else:
                            local_dict[key] = value
    
        for k, v in local_dict.items():
            dates = {}
            for record in v:
                ts = datetime.utcfromtimestamp(record[1])
                hour = ts.hour
                date = date_tuple_to_idx((ts.year, ts.month, ts.day))
                if date not in dates:
                    dates[date] = []
                dates[date].append((floor_to_int(record[0]), hour, float(record[1]), record[2], record[3]))
            for date in dates:
                arr = sorted(dates[date])
                cols = {}
                for floor, hour, t, x, y in arr:
                    idx = hour_floor_index_map(hour, floor)
                    if idx not in cols:
                        cols[idx] = []
                    cols[idx].append((x, y))
                dates[date] = cols
            for date in dates:
                for idx in dates[date]:
                    number_of_access = 0
                    floor_hour_distance = 0
                    logs = dates[date][idx]
                    for i in range(0, len(logs) - 1):
                        x1, y1 = logs[i]
                        x2, y2 = logs[i + 1]
                        first = (float(x1), float(y1))
                        second = (float(x2), float(y2))
                        floor_hour_distance += hs.haversine(first, second, unit='m')
                    dates[date][idx] = floor_hour_distance
            for date in dates:
                res = [0] * 96
                for idx in dates[date]:
                    res[idx] = dates[date][idx]
                dates[date] = tuple(res)
            df[k] = dates
            
        if file_count < 2:
            with open("input_mat.csv", "w") as f:
                for mac in df:
                    for date in df[mac]:
                        d_str = ",".join([str(d) for d in df[mac][date]])
                        f.write("{m},{d},{dist}\n".format(m=mac, d=date,dist=d_str))
        else:
            with open("input_mat.csv", "a") as f:
                for mac in df:
                    for date in df[mac]:
                        d_str = ",".join([str(d) for d in df[mac][date]])
                        f.write("{m},{d},{dist}\n".format(m=mac, d=date,dist=d_str))

        
    