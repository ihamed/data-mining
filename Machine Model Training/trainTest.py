import pandas as pd
from datetime import datetime, timedelta
import math
import datetime as d
import numpy as np
from sklearn.neural_network import MLPClassifier
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.model_selection import train_test_split # Import train_test_split function



data = pd.read_csv (r'MealData.csv', header=None, names=['f1','f2','f3',
                                                         'f4','f5','f6',
                                                         'f7','f8','f9',
                                                         'f10','f11','f12',
                                                         'f13','f14','f15',
                                                         'f16','f17','f18',
                                                         'f19','f20','f21',
                                                         'f22','f23','f24',
                                                         'f25']).dropna()


X = data[['f1','f2','f3','f4','f5','f6','f7','f8','f9',
          'f10','f11','f12','f13','f14','f15','f16','f17',
          'f18','f19','f20','f21','f22','f23','f24']] # Features
y = data[['f25']]
#print(y)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
print("here 0")

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()
print("here 1")
# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)
print("here 2")
#Predict the response for test dataset
y_pred = clf.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, y_pred))


#clf = svm.SVC(kernel='linear') # Linear Kernel
#print("here 1")
#Train the model using the training sets
#clf.fit(X_train, y_train.values.ravel())
#print("here 2")
#Predict the response for test dataset
#y_pred = clf.predict(X_test)

#print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

#mlp = MLPClassifier(hidden_layer_sizes=(8,8,8), activation='relu', solver='adam', max_iter=500)
#mlp.fit(X_train,y_train.values.ravel())


#predict = mlp.predict(X_test)

#pickle.dump(mlp, open('model.sav', 'wb'))
#print(mlp.score(X_test, y_test))

#print(confusion_matrix(y_test,predict_test))
#print(classification_report(y_test,predict_test))
