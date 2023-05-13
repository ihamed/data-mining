import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix

data = pd.read_csv (r'MealData.csv', usecols=[0,1,2])

#print(data.columns)
data = data.dropna()
X = data[['f1','f2']] # Features
y = data['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=13) # 70% training and 30% test

# Create Decision Tree classifer object
#clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
#clf = clf.fit(X_train,y_train)

#Predict the response for test dataset
#y_pred = clf.predict(X_test)

#print("Accuracy:",metrics.accuracy_score(y_test, y_pred))


#Create a svm Classifier
clf = svm.SVC(kernel='linear') # Linear Kernel

#Train the model using the training sets
clf.fit(X_train, y_train)

#Predict the response for test dataset
y_pred = clf.predict(X_test)
#print(y_pred)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

#clf = MLPClassifier(random_state=1, max_iter=300).fit(X_train, y_train)
#print(clf.score(X_test, y_test))


mlp = MLPClassifier(hidden_layer_sizes=(8,8,8), activation='relu', solver='adam', max_iter=500)
mlp.fit(X_train,y_train)

#predict_train = mlp.predict(X_train)
predict_test = mlp.predict(X_test)

print(mlp.score(X_test, y_test))
#print(confusion_matrix(y_train,predict_train))
#print(classification_report(y_train,predict_train))

print(confusion_matrix(y_test,predict_test))
print(classification_report(y_test,predict_test))
