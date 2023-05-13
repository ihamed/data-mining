import pandas as pd
from datetime import datetime, timedelta
import math
import datetime as d
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pickle
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.model_selection import train_test_split # Import train_test_split function

#read used columns
data = pd.read_csv (r'CGMData.csv', usecols=['Date', 'Time', 'Sensor Glucose (mg/dL)'])

#read to get auto mode threeshold
insulin = pd.read_csv (r'InsulinData.csv', usecols=['Date', 'Time','BWZ Carb Input (grams)'])


def timePlusTwoHours(t):
    return (d.datetime.combine(d.date(1,1,1),t) + d.timedelta(hours = 2)).time()

def timeMinusHalfHour(t):
    if t < datetime.strptime('00:30:00', '%H:%M:%S').time() and t > datetime.strptime('00:00:00', '%H:%M:%S').time():
        t = datetime.strptime('00:30:00', '%H:%M:%S').time()
    return (d.datetime.combine(d.date(1,1,1),t) + d.timedelta(hours = -0.5)).time()

# function to get eleminated dates form file 1
eleminated_dates = []
def getEleminatedDates():
    length = len(data)

    countDays = 0
    i = length - 1
    countManualDays = 0
    while i > 0:
        date = data['Date'][i]
        countData = 0
        countTime = 0
        countDays += 1
        while date == data['Date'][i]:
            if not pd.isnull(data['Sensor Glucose (mg/dL)'][i]):
                countData+=1
            countTime = countTime + 1
            if i > 0:
                i = i - 1
            else:
                break
        #print (date , " -> ", countTime , " data ->", countData," ", (countData / 288)*100,"%")
        if (countData / 288) *100 < 80:
            eleminated_dates.append(date)
        elif(countData / 288) *100 > 100:
            eleminated_dates.append(date)


#print(eleminated_dates)


tm = []
dm = []
# func to set tm and dt from file 1
def getMeal():
    length_insulin = len(insulin)
    i = length_insulin - 1
    while i > 0:
        date =  insulin['Date'][i]
        if date in eleminated_dates:
            i -= 1
            continue
        #check if eaten meal
        if not pd.isnull(insulin['BWZ Carb Input (grams)'][i]) and insulin['BWZ Carb Input (grams)'][i] > 0:
            #check if there is no further meal in 2 hour advanced
            time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
            current_tm = time
            while time < timePlusTwoHours(current_tm) and not insulin['Date'][i] in eleminated_dates:
                i -= 1
                time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
                if not pd.isnull(insulin['BWZ Carb Input (grams)'][i]) and insulin['BWZ Carb Input (grams)'][i] > 0:
                    current_tm = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
            
            tm.append(current_tm)
            dm.append(insulin['Date'][i])
        i -= 1

#func to set tnm and dnm from file 1
tnm =[]
dnm= []
def getNoMael():
    length_insulin = len(insulin)
    count = 0
    i = length_insulin - 1
    while i > 0:
        date =  insulin['Date'][i]
        while date in eleminated_dates:
            i -= 1
            if i < 0:
                break
            date =  insulin['Date'][i]
        if i < 0:
            break
        #check if eaten meal
        if pd.isnull(insulin['BWZ Carb Input (grams)'][i]) or insulin['BWZ Carb Input (grams)'][i] < 1:
            #check if there is no further meal in 2 hour advanced
            time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
            current_tm = time
            while time < timePlusTwoHours(current_tm) and not insulin['Date'][i] in eleminated_dates:
                i -= 1
                time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
                if not pd.isnull(insulin['BWZ Carb Input (grams)'][i]) and insulin['BWZ Carb Input (grams)'][i] > 0:
                    #print(time, insulin['Date'][i])
                    count +=1
                    break
            if count == 0 and not insulin['Date'][i] in eleminated_dates:
                tnm.append(current_tm)
                dnm.append(insulin['Date'][i])
            elif count > 0:
                current_tm = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
                while time < timePlusTwoHours(current_tm):
                    if not pd.isnull(insulin['BWZ Carb Input (grams)'][i]) and insulin['BWZ Carb Input (grams)'][i] > 0:
                        current_tm = time
                    if i > 0:
                        i -= 1
                    else:
                        break
                    time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
                count = 0
                i += 1# as it will be mins again
        count =0
        i -= 1



# func to get stretch by date and time dm and tm
def getStretch(date, time, rang):
    data['Time'] = (data['Time'].apply(pd.Timestamp))
    x = data.loc[(data['Date'] == date) & (data['Time'] >= pd.Timestamp(time.strftime('%H:%M:%S')))]
    if len(x) > 0:
        endStretch = x['Time'][x['Time'].keys()[-1]] + pd.Timedelta(hours=rang)
        x = x.loc[x['Time'] < endStretch]
    return x

# function to set value fo meal into csv

M = []
MM = []
def setMealMatrix():
    mealLen = len(tm)
    featureTable = {'feature1':[], 'feature2':[], 'class':[], 'time':[], 'date':[]}
    global M
    i = 0
    print("Start setMealMatrix")
    while i < mealLen:
        stretch = getStretch(dm[i],tm[i], 2)
        # check data > 80%
        if len(stretch['Sensor Glucose (mg/dL)']) < 24:
            i += 1
            continue
        stretchAvg = stretch['Sensor Glucose (mg/dL)'].mean()
        M = (stretch['Sensor Glucose (mg/dL)'].fillna(stretchAvg)).tolist()
        #print(len(M),i)
        if len(M) > 24:
            M = M[0:24]
        #feature extraction
        #variance = pd.DataFrame(M).std()[0] * pd.DataFrame(M).std()[0]
        avg = np.average(M)
        if len(M) < 24:
            i += 1
            continue
        #feature1 = avg/variance
        #feature2 = (max(M)-min(M))/avg
        #remove outliers
        #if feature1 < 0.1 or feature2 < 0.1:
            #i += 1
            #continue
        
        #print(M)
        if M:
            M.append(1)
            MM.append(M)
        i += 1
    result = pd.DataFrame(MM)
    result.to_csv('MealData.csv', index=False, mode='a', header=False)
    #print('in Ecel')

# function to set value fo no meal into file

M = []
def setNoMealMatrix():
    nomealLen = len(tnm)
    featureTable = {'feature1':[], 'feature2':[], 'class':[], 'time':[], 'date':[]}
    global M
    i = 0
    print("Start setNoMealMatrix")
    while i < nomealLen:
        #print(i)
        stretch = getStretch(dnm[i],tnm[i], 2)
        #print(stretch)
        # check data > 80%
        if len(stretch['Sensor Glucose (mg/dL)']) < 20:
            i += 1
            continue
        stretchAvg = stretch['Sensor Glucose (mg/dL)'].mean()
        M = (stretch['Sensor Glucose (mg/dL)'].fillna(stretchAvg)).tolist()
        #print(len(M),i)
        if len(M) > 24:
            M = M [0:24]
        #feature extraction
        #variance = pd.DataFrame(M).std()[0] * pd.DataFrame(M).std()[0]
        #avg = np.average(M)
        if len(M) < 24:
            i += 1
            continue
        #feature1 = avg/variance
        #feature2 = (max(M)-min(M))/avg
        #remove outliers
        #if feature1 < 0.15 or feature2 > 1:
            #i += 1
            #continue
        #featureTable['feature1'].append(feature1)
        #featureTable['feature2'].append(feature2)
        #featureTable['class'].append(0)
        #featureTable['date'].append(dnm[i])
        #featureTable['time'].append(tnm[i])
        
        if M:
            M.append(0)
            MM.append(M)
        i += 1
    result = pd.DataFrame(MM)
    result.to_csv('MealData.csv', index=False, mode='a', header=False)


#call function for file 1
getEleminatedDates()
getMeal()
getNoMael()        
setMealMatrix()
setNoMealMatrix()



# set another files
data = pd.read_csv (r'CGM_patient2.csv', usecols=['Date', 'Time', 'Sensor Glucose (mg/dL)'])
insulin = pd.read_csv (r'Insulin_patient2.csv', usecols=['Date', 'Time','BWZ Carb Input (grams)'])
tm = []
dm = []
tnm = []
dnm = []
getEleminatedDates()
#print(eleminated_dates)
getMeal()
getNoMael()
setMealMatrix()
setNoMealMatrix()


print('Finished prepocessing')


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

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()
# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)
#Predict the response for test dataset
#y_pred = clf.predict(X_test)

pickle.dump(mlp, open('model.sav', 'wb'))
print(mlp.score(X_test, y_test))

#print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
