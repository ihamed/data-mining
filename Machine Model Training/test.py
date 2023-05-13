import pickle
import pandas as pd
import numpy as np

data = pd.read_csv (r'test.csv', header=None, names=['f1','f2','f3',
                                                         'f4','f5','f6',
                                                         'f7','f8','f9',
                                                         'f10','f11','f12',
                                                         'f13','f14','f15',
                                                         'f16','f17','f18',
                                                         'f19','f20','f21',
                                                         'f22','f23','f24']).dropna()


#print(data.columns)
data = data.dropna()
X = data[['f1','f2','f3','f4','f5','f6','f7','f8','f9',
          'f10','f11','f12','f13','f14','f15','f16','f17',
          'f18','f19','f20','f21','f22','f23','f24']] # Features
#print (X)
loaded_model = pickle.load(open('model.sav', 'rb'))
result = loaded_model.predict(X)
#print(result)

result = pd.DataFrame(result)
result.to_csv('Result.csv', index=False, header=False)

print("Done Test")
