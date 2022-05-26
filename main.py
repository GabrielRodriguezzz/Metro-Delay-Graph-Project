# -*- coding: utf-8 -*-
"""
Created on Sun May  9 14:54:39 2021

@author: Gabriel Rodriguez
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

pd.set_option("display.max_columns", None)

#
### load the dataframe from a file in the directory
#
df = pd.read_csv('MetroData.csv',usecols=["Type d'incident","Ligne","Heure de l'incident","Heure de reprise"])


#
### Only using the type Train incidents, because the majority of Station incidents don't cause delays and last for hours
#
df = df.groupby("Type d'incident").get_group('T')



#
### changing time set of 2:00-25:59 to 0:00-23:59 (IDK why they have it like that in the original dataset)
# 
# The time in the dataframe makes it so I cannot convert with to_datetime with pandas normaly this would work:
    #df['Hour of incident'] = pd.to_datetime(df["Heure de l'incident"], format='%H:%M')
# A solution is to change all the strings of 12:30 into 2 sets of floats, hour 12 and minute 30, to then change 24h and 25h to 0h and 1h


# Making the str of time into a float
df["Heure de l'incident"] = (df["Heure de l'incident"].str.replace(':','').astype('float'))
df["Heure de reprise"] = df["Heure de reprise"].str.replace(':','').astype('float')

# # seperating minutes and hours
df["Minute de l'incident"] = (df["Heure de l'incident"] -(((df["Heure de l'incident"]/100) // 1)*100)).astype(int)
df["Minute de reprise"] = (df["Heure de reprise"] -(((df["Heure de reprise"]/100) // 1)*100)).astype(int)

df["Heure de l'incident"] = (df["Heure de l'incident"]/100) // 1
df["Heure de reprise"] = (df["Heure de reprise"]/100) // 1

# # Changing the 24,25 hour entrees to 0 and 1

df["Heure de l'incident"] = np.where(df["Heure de l'incident"]>=24,df["Heure de l'incident"]-24,df["Heure de l'incident"]).astype(int)
df["Heure de reprise"] = np.where(df["Heure de reprise"]>=24,df["Heure de reprise"]-24,df["Heure de reprise"]).astype(int)



#
### Making the delay time
#

# Issue with dealing with negative hours when incident hour is 22-23hour and recovery is at 0-1hour
# Solution: add 24h to the recovery time when it is negative before calculating the time delays

df["Heure de reprise"] = np.where(df["Heure de reprise"]-df["Heure de l'incident"] < 0,df["Heure de reprise"]+24,df["Heure de reprise"])

# Creating time delay
df['Delay'] = (df["Heure de reprise"]-df["Heure de l'incident"])*60 + df["Minute de reprise"]-df["Minute de l'incident"]

# getting rid of all the 0 minute delays (a bit of data culling )
df = df.drop(df[df.Delay <1].index)

#
### Getting the data to plot the graphs
#

# seperating the dataframe into the 4 lines, this excludes weird line entrees like (Ligne 1,3,5; Ligne 1,2) that were not specified in the dataset
# website
dforange = df.groupby('Ligne').get_group('Ligne orange')
dfgreen = df.groupby('Ligne').get_group('Ligne verte')
dfyellow = df.groupby('Ligne').get_group('Ligne jaune')
dfblue = df.groupby('Ligne').get_group('Ligne bleue')

# Getting the delay amount of each line for less than 5min, 5-10min, 10-30min and 30+

#less than 5 minutes
orange5 = dforange.drop(dforange[dforange.Delay>5].index).size
green5 = dfgreen.drop(dfgreen[dfgreen.Delay>5].index).size
yellow5 = dfyellow.drop(dfyellow[dfyellow.Delay>5].index).size
blue5 = dfblue.drop(dfblue[dfblue.Delay>5].index).size

# between 5 and 10 minutes
orange10 = dforange.drop(dforange[dforange.Delay<6].index).drop(dforange[dforange.Delay>10].index).size
green10 = dfgreen.drop(dfgreen[dfgreen.Delay<6].index).drop(dfgreen[dfgreen.Delay>10].index).size
yellow10 = dfyellow.drop(dfyellow[dfyellow.Delay<6].index).drop(dfyellow[dfyellow.Delay>10].index).size
blue10 = dfblue.drop(dfblue[dfblue.Delay<6].index).drop(dfblue[dfblue.Delay>10].index).size

# between 10 and 30 minutes
orange30 = dforange.drop(dforange[dforange.Delay<11].index).drop(dforange[dforange.Delay>30].index).size
green30 = dfgreen.drop(dfgreen[dfgreen.Delay<11].index).drop(dfgreen[dfgreen.Delay>30].index).size
yellow30 = dfyellow.drop(dfyellow[dfyellow.Delay<11].index).drop(dfyellow[dfyellow.Delay>30].index).size
blue30 = dfblue.drop(dfblue[dfblue.Delay<11].index).drop(dfblue[dfblue.Delay>30].index).size

# 30+ minutes
orange31 = dforange.drop(dforange[dforange.Delay<31].index).size
green31 = dfgreen.drop(dfgreen[dfgreen.Delay<31].index).size
yellow31 = dfyellow.drop(dfyellow[dfyellow.Delay<31].index).size
blue31 = dfblue.drop(dfblue[dfblue.Delay<31].index).size


#
### Plotting
# 

lines = ('Orange','Green','Yellow','Blue')

delays5 = (orange5,green5,yellow5,blue5)
delays10 = (orange10,green10,yellow10,blue10)
delays30 = (orange30,green30,yellow30,blue30)
delays31 = (orange31,green31,yellow31,blue31)
pos10 = (orange5,green5,yellow5,blue5)
pos30 = (orange5+orange10,green5+green10,yellow5+yellow10,blue5+blue10)
pos31 = (orange5+orange10+orange30,green5+green10+green30,yellow5+yellow10+yellow30,blue5+blue10+yellow30)

ind = np.arange(len(lines))
width = 0.35

fig = plt.figure()

ax = fig.add_axes([0,0,1,1])
ax.bar(lines,delays5,width,color='y')
ax.bar(lines,delays10,width,bottom=pos10,color='b')
ax.bar(lines,delays30,width,bottom=pos30,color='g')
ax.bar(lines,delays31,width,bottom=pos31,color='r')
ax.legend(labels=['1-5min', '6-10min','11-30min','31+min'])

plt.ylabel('Delays')
plt.xlabel('Metro Lines')
plt.title('Metro Delays in 2019')


plt.show()



#for i in range(0,new_df.shape[0]):
#  if (new_df.iloc[i,2][0:2] == '24'):
#    new_df.iloc[i,2]='00'+new_df.iloc[i,2][2:]
