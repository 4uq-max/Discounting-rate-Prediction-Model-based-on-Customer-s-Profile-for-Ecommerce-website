# -*- coding: utf-8 -*-
"""Model_NN

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lj3OHp3M7P-YTcsD0Hx5BayNW6XkhhMd
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import KFold,StratifiedShuffleSplit
from sklearn import preprocessing
from keras.models import Sequential
from keras.layers import  Dense,Activation

# Code to read csv file into Colaboratory:
!pip install -U -q PyDrive
!pip install tensorflow==1.13.2
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
# Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

link='https://drive.google.com/open?id=1S0kqcUYednLGkHd6Np3MGWYfHSLWJpeW'
fluff, id = link.split('=')
print (id) # Verify that you have everything after '='
downloaded = drive.CreateFile({'id':id}) 
downloaded.GetContentFile('finaldata_v1.1.csv')  
df = pd.read_csv('finaldata_v1.1.csv',usecols=['Recency','Frequency','Monetary','CCategory','lable'])
df.head()

#global variables
ACTIVATION_HOOK='sigmoid'
CLASS_SIZE=0

def encode_target(df,target_col):
  df_temp=df.copy()
  target=df_temp[target_col].unique()
  map_2_int={name: n for n, name in enumerate(target)}
  print(map_2_int) #{'H': 0, 'L': 1, 'M': 2, 'N': 3}
  global CLASS_SIZE
  CLASS_SIZE=len(map_2_int)
  print(CLASS_SIZE)
  df_temp["Target"] = df_temp[target_col].replace(map_2_int)
  return (df_temp, target)


df2, target = encode_target(df, "lable")
df2.head()

#converting object type of CCAtegory col to int dtype
def encode_category(df,cat_col):
  df_temp1=df2.copy()
  unq_cat=df_temp1['CCategory'].unique().tolist()         #13 unique categories
  map_2_int={name: n for n, name in enumerate(unq_cat,100)}
  print(map_2_int)
  '''{'CA3203': 100, 'CA1726': 101, 'CA5616': 102, 'CA3509': 103, 
      'CA2202': 104, 'CA5619': 105, 'CA5558': 106, 'CA4401': 107, 
      'CA2119': 108, 'CA9909': 109, 'CA1703': 110, 'CA6202': 111, 'CA3504': 112}'''
  df_temp1["CCategory_int"] = df_temp1[cat_col].replace(map_2_int)
  return (df_temp1, unq_cat)

df2, unq_cat = encode_category(df2, "CCategory")
df2=df2[['Recency','Frequency','Monetary','CCategory_int','CCategory','lable','Target']]
df2.head()

dataset=df2.values
dataset

#assigning features and target
X=dataset[:,0:4]          #features
y=dataset[:,6]            #target
#stratified sampling
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=0)
sss.get_n_splits(X, y)
for train_idx, test_idx in sss.split(X, y):
    X_train,X_test=X[train_idx],X[test_idx]
    y_train,y_test=y[train_idx],y[test_idx]
print('done')

#all input feature lie between 0 and 1 inclusively
min_max_scaler = preprocessing.MinMaxScaler()
X_scale = min_max_scaler.fit_transform(X)
X_scale

#defining model structure

model = Sequential()
model.add(Dense(32, activation=ACTIVATION_HOOK, input_shape=(4,)))
model.add(Dense(64, activation=ACTIVATION_HOOK))
model.add(Dense(64, activation=ACTIVATION_HOOK))
model.add(Dense(128, activation=ACTIVATION_HOOK))
model.add(Dense(128, activation=ACTIVATION_HOOK))
model.add(Dense(256, activation=ACTIVATION_HOOK))
model.add(Dense(CLASS_SIZE,activation='softmax'))
model.summary()

#compiling model
model.compile(optimizer='adadelta',loss='sparse_categorical_crossentropy',metrics=['accuracy'])

#kfold
kf = KFold(n_splits=10)
kf.get_n_splits(X_train)
#print(kf)
score=[]
for train_index, test_index in kf.split(X_train):
  print("TRAIN:", train_index, "TEST:", test_index)
  Xv_train, Xv_test = X_train[train_index], X_train[test_index]
  yv_train, yv_test = y_train[train_index], y_train[test_index]
  model.fit(Xv_train,yv_train,epochs=128,batch_size=32)
  predict=model.predict(Xv_test)
  score.append(model.evaluate(Xv_test,yv_test)[1])
  print('score:',score[-1])

print('yes')

y_test

import pickle
filename = ''
pickle.dump(model, open(filename, 'wb'))

df=pd.DataFrame()

df['R']=[10.0]
df['F']=[4]
df['M']=[14.55]
df['C']=[100]

df

import pickle
filename = 'NuralNetworkModel_1.sav'
loaded_model = pickle.load(open(filename, 'rb'))
loaded_model.compile(optimizer='adadelta',loss='sparse_categorical_crossentropy',metrics=['accuracy'])

out=loaded_model.predict(df)

print(out)
max(out[0])

"""look for list elements
[ 0:   [ 0:     0.88263166     1:     0.0010113656     2:     0.116356984    3:     2.7247428e-35 ] ]
"""

for i in out[0]:
  print(i)

loaded_model.evaluate(X_test, y_test)

"""BIG one is in index zero so we will predicted high discount"""