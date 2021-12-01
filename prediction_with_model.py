import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from kmeans_group_by_mac import parse_line
from constant import INPUT_MAT
from sys import argv
from datetime import datetime
import haversine as hs
from constant import *

def cached_mobile():
    mobile = set()

    with open("vendor_clusters.csv", "r") as f:
        line = f.readline()
        line = f.readline()
        while line:
            l = line.split(",")
            mobile.add(l[1])
            line = f.readline()
    return mobile

def get_index(floor):
    return [2 + floor + i * 4 for i in range(24)]

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

def get_lstm_input(df):
    res_mp = {}
    for k, v in df.items():
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
        res_mp[k] = dates
    return res_mp

def get_kmeans_input(df):
    kmeans_mat = {}
    for k, v in df.items():
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
            if k not in kmeans_mat:
                kmeans_mat[k] = [0] * 24
            kmeans_mat[k][hour] = avg_dist
    return kmeans_mat
    
def kmeans_predict_is_mobile(point, centroids):
    smalles_dist = float("Inf")
    res = -1
    for i in range(len(centroids)):
        dist = sum([(point[j] - centroids[i][j])**2 for j in range(len(centroids[i]))])
        if dist < smalles_dist:
            res = dist
            smalles_dist = dist
    return res != 0

if __name__ == "__main__":
    # read input-mac
    
    INPUT_PATH = argv[1]
    centroids = []
    with open("kmeans.csv", "r") as f:
        line = f.readline()
        while line:
            centroids.append([float(s) for s in line.split(",")])
            line = f.readline()

    cached_mobile_mac = cached_mobile()
    mobile = set()
    df = {}
    
    with open(INPUT_PATH, "r") as f:
        line = f.readline()
        while line:
            if "Site,Level,ClientMacAddr,lat,lng,localtime" not in line:
                client_mac_addr, level, localtime,lat, lng = parse_line(line)
                if client_mac_addr not in df:
                    df[client_mac_addr] = []
                df[client_mac_addr].append([level, localtime,lat, lng])
            line = f.readline()
    
    kmeans_mat = get_kmeans_input(df)

    for k in kmeans_mat:
        if k in cached_mobile_mac or kmeans_predict_is_mobile(kmeans_mat[k], centroids):
            mobile.add(k)
    
    lstm_df = get_lstm_input(df)

    abnormal = []
    lstm_idx = []
    lstm_mat = []

    model = keras.models.load_model('production-model')
    for key in lstm_df:
        if key in mobile:
            for d in lstm_df[key]:
                lstm_idx.append((key, d))
                lstm_mat.append(lstm_df[key][d])

    prediction = model.predict(np.array(lstm_mat))
    for i in prediction.flatten().tolist():
        if i < 0.05:
            abnormal.append(lstm_idx[i])
    
    for a in abnormal:
        print(a)