import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from constant import *
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

if __name__ == "__main__":
    abnormal = set()
    #path = "C:/Users/Yuanzhe Li/PyCharmProjects/untitled/INF551/560project/"
    #"C:\Users\Yuanzhe Li\PycharmProjects\untitled\INF551\560project\abnormal_mac.json"
    def get_index(floor):
        return [2 + floor + i * 4 for i in range(24)]


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
    X = pd.read_csv(path+"input_mat.csv",sep=",",header=None).iloc[: , 2:]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=41
    )

    # modeling
    model = keras.Sequential()
    model.add(layers.Embedding(input_dim=12000, output_dim=64))

    # The output of GRU will be a 3D tensor of shape (batch_size, timesteps, 256)
    # model.add(layers.GRU(256, return_sequences=True))

    # The output of SimpleRNN will be a 2D tensor of shape (batch_size, 128)
    model.add(layers.SimpleRNN(128, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation='sigmoid'))

    #model.summary()
    model.compile(optimizer=keras.optimizers.Adam(),  # Optimizer
                  # Loss function to minimize
                  loss=keras.losses.BinaryCrossentropy())
    model.fit(np.array(X_train), np.array(y_train), batch_size=64, epochs=2, validation_split=0.1)
    y_pred = model.predict(np.array(X_test))
    y_predict_class = []
    for i in y_pred.flatten().tolist():
        if i < 0.1:
            y_predict_class.append(0)
        else:
            y_predict_class.append(1)
    confusion_matrix = confusion_matrix(y_test, y_predict_class)
    print(confusion_matrix)