import pandas as pd
import numpy as np
import csv
from tqdm import tqdm
from constant import *
from sklearn.linear_model import LogisticRegression
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

def get_index(floor):

    return [2 + floor + i * 4 for i in range(24)]


if __name__ == "__main__":

    abnormal = set()
    with open(ABNORMAL_MAC, "r") as f:
        # read each line in one json
        abnormal.update(json.loads(f.read()))

    wrong_floor = None
    with open(WRONG_FLOOR, "r") as f:
        wrong_floor = json.loads(f.read())

    y = list()
    with open(INPUT_MAT, "r") as f:
        line = f.readline()
        while line:
            record = line.split(",")
            if record[0] not in abnormal:
                y.append(0)
            else:
                if record[0] in wrong_floor:
                    wrong_nums = wrong_floor[record[0]]
                    indexes = []
                    for num in wrong_nums:
                        indexes.extend(get_index(num))
                    flag = True
                    for idx in indexes:
                        if record[idx] != "0":
                            y.append(1)
                            flag = False
                            break
                    if flag:
                        y.append(0)
                else:
                    y.append(1)
            line = f.readline()
    X = pd.read_csv("input_mat.csv",sep=",",header=None).iloc[: , 2:]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.1,
        random_state=42
    )
    clf = LogisticRegression(random_state=0,max_iter=1000,solver='saga',penalty="elasticnet",l1_ratio=0.5).fit(X_train, y_train)
    y_predict = clf.predict_prob(X_test)
    print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(clf.score(X_test, y_test)))

    confusion_matrix = confusion_matrix(y_test, y_predict)
    print(confusion_matrix)
    #y_pred =


