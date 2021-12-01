import pandas as pd
import numpy as np
import os
from datetime import datetime
from constant import *
from sklearn.cluster import KMeans
from sklearn.cluster import KMeans
import pickle
from sklearn.datasets.samples_generator import make_blobs

if __name__ == "__main__":
    input = pd.read_csv("kmeans_input.csv", sep=",", header=None, index_col=0)

    # From the graph above, the elbow point is when k = 3
    kmeans = KMeans(n_clusters=3, random_state=0).fit(input)
    labels = kmeans.labels_
    tmp_list = list(labels)
    input['cluster'] = labels
    # save centroids of each clusters
    centroids = kmeans.cluster_centers_
    np.savetxt("kmeans.csv", centroids, delimiter=",")

    # build vendor_cluster.csv
    data = input
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