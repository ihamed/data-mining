import pandas as pd
from datetime import datetime, timedelta
import math
import datetime as d
import numpy as np
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation
from sklearn.metrics import confusion_matrix
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

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
vm = []
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
            carb = insulin['BWZ Carb Input (grams)'][i]
            #check if there is no further meal in 2 hour advanced
            time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
            current_tm = time
            while time < timePlusTwoHours(current_tm) and not insulin['Date'][i] in eleminated_dates:
                i -= 1
                time = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
                if not pd.isnull(insulin['BWZ Carb Input (grams)'][i]) and insulin['BWZ Carb Input (grams)'][i] > 0:
                    current_tm = datetime.strptime(insulin['Time'][i], '%H:%M:%S').time()
                    carb = insulin['BWZ Carb Input (grams)'][i]
            
            tm.append(current_tm)
            dm.append(insulin['Date'][i])
            vm.append(carb)
        i -= 1



# func to get stretch by date and time dm and tm
def getStretch(date, time, rang):
    data['Time'] = (data['Time'].apply(pd.Timestamp))
    x = data.loc[(data['Date'] == date) & (data['Time'] >= (pd.Timestamp(time.strftime('%H:%M:%S'))) - pd.Timedelta(hours=0.5))]
    if len(x) > 0:
        endStretch = x['Time'][x['Time'].keys()[-1]] + pd.Timedelta(hours=rang)
        #print((pd.Timestamp(time.strftime('%H:%M:%S'))) - pd.Timedelta(hours=0.5), time, endStretch)
        x = x.loc[x['Time'] < endStretch]
        #print(len(x))
    return x


# set bins
def getBin(val):
    if val > n*20:
        return n
    else:
        return (int((val-min(vm))/20)+1)
    
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
        stretch = getStretch(dm[i],tm[i], 2.5)
        # check data > 80%
        #print(stretch.isna().sum())
        if stretch['Sensor Glucose (mg/dL)'].count() < 24:
            i += 1
            continue
        stretchAvg = stretch['Sensor Glucose (mg/dL)'].mean()
        M = (stretch['Sensor Glucose (mg/dL)'].fillna(stretchAvg)).tolist()
        #print(len(M),i)
        if len(M) > 30:
            M = M[0:30]
        #feature extraction
        variance = pd.DataFrame(M).std()[0] * pd.DataFrame(M).std()[0]
        avg = np.average(M)
        if len(M) < 30:
            i += 1
            continue
        feature1 = avg/variance
        feature2 = (max(M)-min(M))/avg
        #remove outliers
        #if feature1 < 0.1 or feature2 < 0.1:
            #i += 1
            #continue
        M = [feature1]
        M.append(feature2)
        #print(M)
        #print(vm[i])
        if M:
            M.append(vm[i])
            M.append(getBin(vm[i])-1)
            MM.append(M)
        i += 1
    result = pd.DataFrame(MM)
    result.to_csv('MealData.csv', index=False, header=False)
    #print('in Ecel')


#call function for file 1
getEleminatedDates()
getMeal()
n = int((max(vm)-min(vm))/20)
setMealMatrix()




#print('Finished prepocessing')


data = pd.read_csv (r'MealData.csv', header=None, names=['f1','f2','f3','f4']).dropna()
X = data[['f1','f2','f3']] # Features
y = data[['f4']]
kmeans = KMeans(n_clusters=n, random_state=0, n_init= 1).fit(X)# n = 5
k = kmeans.fit_predict(X)
mat = confusion_matrix(y, k)

def purity(matrix):
    total = np.sum(matrix)
    total_purity = 0
    for i in range(len(matrix)):
        weight = np.sum(matrix[i])/total
        if np.sum(matrix[i]) == 0:
            continue
        purity = max(matrix[i])/np.sum(matrix[i])
        total_purity = total_purity + (purity*weight)
    return total_purity

def entropy(matrix):
    total_entropy = 0
    total = np.sum(matrix)
    for i in range(len(matrix)):
        sum = np.sum(matrix[i])
        entropy = 0
        weight = np.sum(matrix[i])/total
        for j in range(len(matrix[i])):
            if matrix[i][j] != 0:
                p = matrix[i][j]/sum
                entropy += p * math.log(p,2)
        
        total_entropy +=  (entropy*weight)
    return (-total_entropy)

dbscan = DBSCAN(eps=1, min_samples=13).fit(X)
dbscan_predict = dbscan.fit_predict(X)
#print(dbscan_predict)
dbscan_mat = confusion_matrix(y, dbscan_predict)
#print(dbscan_mat)
labels = dbscan.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
#print(n_clusters_)
#calculate SSE
def SSE():
    data.loc[:,'label'] = pd.Series(labels, index=data.index)
    sse = 0
    for i in range(n_clusters_):
        label = data.loc[(data['label'] == i)]
        total_mean = label.mean()[0:3]
        f1 = label['f1'].apply(lambda x: x-total_mean['f1'])
        f1 = f1.apply(lambda x: x*x)
        f2 = label['f2'].apply(lambda x: x-total_mean['f2'])
        f2 = f2.apply(lambda x: x*x)
        f3 = label['f3'].apply(lambda x: x-total_mean['f3'])
        f3 = f3.apply(lambda x: x*x)
        f123 = f2 + f1 + f3
        sse += f123.sum()
    return sse

dataDic = [[kmeans.inertia_,SSE(),entropy(mat),entropy(dbscan_mat),purity(mat),purity(dbscan_mat)]]
result = pd.DataFrame(dataDic)
result.to_csv('Result.csv', header=False, index=False)
#print("k-means entropy: ",entropy(mat))
#print("k-means purity:",purity(mat))
#print("k-means SSE", kmeans.inertia_)

#print("DBScan entropy: ",entropy(dbscan_mat))
#print("DBScan purity:",purity(dbscan_mat))
#print("DBScan SSE", SSE())
