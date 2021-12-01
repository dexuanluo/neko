import pandas as pd
import numpy as np
import os
from datetime import datetime
import os
from constant import *
import json
from tqdm import tqdm
import haversine as hs

if __name__ == "__main__":

    df = {}
    # traverse each json file
    for data_file in tqdm(os.listdir(RES_PATH)):
        local_dict = dict()
        with open(RES_PATH + "/" + data_file, "r") as f:
            # read each line in one json
            for line in f:
                data = json.loads(line)
                # build a dictionary called local_dict to save {macaddress: [all data points in this file for this macaddr]}
                for key, value in data.items():
                    if key in local_dict:
                        local_dict[key].extend(value)
                    else:
                        local_dict[key] = value
        
        # traverse each macaddress and record each macaddr's hour - coordinates of lat lng
        for k, v in local_dict.items():
            # hours[i] saves all coords in hour i
            hours = {}
            # build each hour & its corresponding lat & lng
            for record in v:
                time = datetime.utcfromtimestamp(record[1]).hour
                date = datetime.utcfromtimestamp(record[1]).isocalendar()
                if time not in hours.keys():
                    hours[time] = []
                hours[time].append((date, float(record[1]), record[2], record[3]))
            # calculate average distance for each hour of current macaddress
            for time in hours:
                arr = sorted(hours[time])
                d = {}
                for date, t, x, y in arr:
                    if date not in d:
                        d[date] = []
                    d[date].append((x, y))
                hours[time] = d

            for hour in hours:
                number_of_days  = 0
                distance = 0
                for date in hours[hour]:
                    number_of_days += 1
                    coords = hours[hour][date]
                    daily_dist = 0
                    for i in range(0, len(coords) - 1):
                        first = (float(coords[i][0]), float(coords[i][1]))
                        second = float(coords[i + 1][0]), float(coords[i + 1][1])
                        daily_dist += hs.haversine(first, second, unit='m')
                    distance += daily_dist
                avg_dist = distance / number_of_days
                # save the clientMacAddr, hour, avg_dist to df
                if k not in df:
                    df[k] = ["0"] * 24
                df[k][hour] = str(avg_dist)

    with open("kmeans_input.csv","w") as f:
        for mac in tqdm(df, desc="Writing to file: "):
            s = ",".join(df[mac]) + "\n"
            f.write(mac + "," + s)