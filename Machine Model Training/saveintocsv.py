import pandas as pd
from datetime import datetime, timedelta
import math
import datetime as d
import numpy as np
from sklearn.neural_network import MLPClassifier
import pickle
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.model_selection import train_test_split # Import train_test_split function

f1 = [229.0, 240.0, 248.0, 251.0, 270.0, 274.0, 278.0, 283.0, 284.0, 274.0, 267.0, 267.0, 269.0, 274.0, 277.0, 270.0, 262.0, 256.0, 243.0, 233.0, 228.0, 224.0, 223.0, 222.0, 1]
f2 = [4,5,6]
featureTable = []
featureTable.append(f1)
featureTable.append(f2)
result = pd.DataFrame(featureTable)
result.to_csv('testsave.csv', index=False, mode='a', header=False)
