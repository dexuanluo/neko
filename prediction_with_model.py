import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


if __name__ == "__main__":
    # read input-mac
    model = keras.models.load_model('production-model')
    prediction = model.predict(np.array(input_mac))

    prediction_class = []
    for i in prediction.flatten().tolist():
        if i < 0.05:
            prediction_class.append(0)
        else:
            prediction_class.append(1)
    print(prediction_class)