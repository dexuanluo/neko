import pandas as pd
import numpy as np
import os
from datetime import datetime
import os
from constant import *
from sklearn.cluster import KMeans
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.cluster import KMeans
from sklearn.datasets.samples_generator import make_blobs

if __name__ == "__main__":
    input = pd.read_csv("kmeans_input.csv", sep=",", header=None, index_col=0)

    # style.use("fivethirtyeight")
    #     #
    #     # # make_blobs() is used to generate sample points
    #     # # around c centers (randomly chosen)
    #     #
    #     #
    #     # cost = []
    #     # for i in range(1, 11):
    #     #     KM = KMeans(n_clusters=i, max_iter=500)
    #     #     KM.fit(input)
    #     #
    #     #     # calculates squared error
    #     #     # for the clustered points
    #     #     cost.append(KM.inertia_)
    #     #
    #     #     # plot the cost against K values
    #     # plt.plot(range(1, 11), cost, color='g', linewidth='3')
    #     # plt.xlabel("Value of K")
    #     # plt.ylabel("Squared Error (Cost)")
    #     # #plt.show()  # clear the plot

    # From the graph above, the elbow point is when k = 3
    kmeans = KMeans(n_clusters=3, random_state=0).fit(input)
    labels = kmeans.labels_
    tmp_list = list(labels)
    input['cluster'] = labels
    #print(Counter(tmp_list))
    input.to_csv("clusters.csv")

    data = pd.read_csv("clusters.csv", sep=",", header=0)
    macaddress = data['0']
    vendor_dict = dict()
    with open("code_vendor.txt",'r') as f:
        line = f.readline()
        while line:
            arr = line.split(" ")
            vendor_dict[arr[0].lower()] = " ".join(arr[1:]).rstrip()
            line = f.readline()
    # match mac address with vendor by vendor dict
    vendor = list()
    for addr in macaddress:
        vendor.append(vendor_dict.get(addr[:8]))


    data['vendor'] = vendor
    data.to_csv("vendor_clusters.csv")
    # write count
    data = pd.read_csv("vendor_clusters.csv", sep=',', index_col=0)
    count = {}
    for i in range(len(data)):
        if data["vendor"][i] not in count:
            count[data["vendor"][i]] = [0] * 3
        count[data["vendor"][i]][data["cluster"][i]] += 1
    c0 = {}
    c1 = {}
    c2 = {}
    s0 = 0
    s1 = 0
    s2 = 0
    for key in count.keys():
        s0 += count[key][0]
        s1 += count[key][1]
        s2 += count[key][2]

    for key in count.keys():
        c0[key] = count[key][0] / s0
        c1[key] = count[key][1] / s1
        c2[key] = count[key][2] / s2


