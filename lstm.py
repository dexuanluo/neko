import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from constant import *
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

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
        test_size=0.2,
        random_state=41
    )

    # modeling
    lstm = keras.Sequential()
    lstm.add(layers.Embedding(input_dim=12000, output_dim=64))

    # The output of GRU will be a 3D tensor of shape (batch_size, timesteps, 256)
    # model.add(layers.GRU(256, return_sequences=True))

    # The output of SimpleRNN will be a 2D tensor of shape (batch_size, 128)
    lstm.add(layers.LSTM(128, activation='tanh'))
    lstm.add(layers.Dropout(0.2))
    lstm.add(layers.Dense(1, activation='sigmoid'))

    lstm.compile(optimizer=keras.optimizers.Adam(clipvalue=0.1),  # Optimizer
                 # Loss function to minimize
                 loss="mean_squared_error")
    y_pred_lstm = lstm.predict(np.array(X_test))
    y_predict_lstm_class = []
    for i in y_pred_lstm.flatten().tolist():
        if i < 0.05:
            y_predict_lstm_class.append(0)
        else:
            y_predict_lstm_class.append(1)
    confusion_matrix = confusion_matrix(y_test, y_predict_lstm_class)
    print(confusion_matrix)

    # save the model
    lstm.save('production-model')