import pandas as pd
import numpy as np
import os
from datetime import datetime
import csv
from sklearn import linear_model
from sklearn.cluster import KMeans
import os
from constant import *
import json
from tqdm import tqdm
import haversine as hs

if __name__ == "__main__":

    df = pd.DataFrame(columns=['ClientMacAddr', 'Hour', 'avg_dist'])
    # traverse each json file
    for data_file in tqdm(os.listdir(RES_PATH)):
        with open(RES_PATH + "/" + data_file, "r") as f:
            # read each line in one json
            for line in f:
                data = json.loads(line)
                # build a dictionary called local_dict to save {macaddress: [all data points in this file for this macaddr]}
                local_dict = dict()
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
                        # print(record[0])
                        time = datetime.utcfromtimestamp(record[1]).hour
                        # print(record[1])
                        if time not in hours.keys():
                            hours[time] = []
                        hours[time].append([record[2], record[3]])
                    # calculate average distance for each hour of current macaddress
                    for hour, coords in hours.items():
                        n = len(coords)
                        distance = 0
                        for i in range(0, n - 1):
                            first = (float(coords[i][0]), float(coords[i][1]))
                            second = float(coords[i + 1][0]), float(coords[i + 1][1])
                            distance += hs.haversine(first, second, unit='m')
                        avg_dist = distance / n
                        # save the clientMacAddr, hour, avg_dist to df
                        df = df.append({'ClientMacAddr': k, 'Hour': hour, 'avg_dist': avg_dist}, ignore_index=True)
    df.set_index('ClientMacAddr')
    mac_address = df['ClientMacAddr'].unique()
    tmp_dict = {}
    for i in mac_address:
        tmp_dict[i] = [0]*24
    for r in df.iterrows():
        tmp_dict[r[1][0]][r[1][1]] = r[1][2]
    kmeans_data_input = pd.DataFrame.from_dict(tmp_dict,orient='index')
    kmeans_data_input.to_csv("kmeans_input",)