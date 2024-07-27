import pandas as pd
import numpy as np
import random

from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
from sklearn.experimental import enable_iterative_imputer 
from sklearn.impute import IterativeImputer
from sklearn.linear_model import LinearRegression
from impyute.imputation.cs import mice

from sklearn.metrics import mean_squared_error

import seaborn as sns
import matplotlib.pyplot as plt

######################### Pepare paths #######################################
path = './data/pilot_iii/behavioral/' 
begin='2021-08-02'
end='2021-09-07'

sleep_cols = ['Total Sleep Time', 'Awake Time', 'Restless Sleep', 'Sleep Efficiency', 'Sleep Latency']
activity_cols = ['Target Calories', 'Steps', 'Inactive Time', 'Rest Time', 'High Activity Time', 'Non-wear Time', 'Long Periods of Inactivity']
all_cols = ['date','Total Sleep Time', 'Awake Time', 'Restless Sleep', 'Sleep Efficiency', 'Sleep Latency', 'Target Calories', 'Steps', 'Inactive Time', 'Rest Time', 'High Activity Time', 'Non-wear Time', 'Long Periods of Inactivity']

iteration = 10000

######################## Read data and remove some days ######################
pilot = pd.read_csv(f'{path}/sub-01_sensor-oura.csv')
pilot.drop(['Sleep Timing.1', 'Bedtime Start','Bedtime End', 'HRV Balance Score'], axis=1, inplace=True)
#HRV balance has some nans randomly placed and we do not know why exactly it is. This may be related to
#the Oura own algorithm and therefore, we drop the column so that it will not make us drop more rows
#when dropping nans.
pilot.dropna(axis=0, inplace=True)
pilot = pilot [all_cols]

gold = pilot.copy() 
gold.reset_index(inplace=True)
#For tetsing and comparison purposes, we will assume these values are the same as the preceeding night
#This is only for comparing the imputers' performance. 

pilot.set_index("date", inplace=True)
##############################################################################

def generate_missing(pilot):
    df = pilot.copy()
    ids = random.sample(range(1, len(df)), round(.2*len(df))) #The first observations cannot be missing
    #We have observed from the data, that usually either sleep data is lost, but not activity data.
    #Then, we will assume the same missingness structure that we have observed to create our 
    #artificial missingness.
    for i in ids:
        df.loc[df.index[i],sleep_cols] = np.nan

    index = gold.index
    condition = df["Total Sleep Time"].isna() == True
    miss_ids = index[condition].tolist()
    #We store the indices of the artificial missing data values.
    return df, miss_ids

########################### Impute the data ##################################
def impute_data(pilot, miss_ids):
    imputed_data = dict.fromkeys(['mean','common', 'zero', 'linear', 'knn', 'iterative', 'interpolation', 'imice'])

    mean_imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    imputed_data['mean'] =  mean_imp.fit_transform(pilot.values)

    common_imp = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
    imputed_data['common'] =  common_imp.fit_transform(pilot.values)

    zero_imp = SimpleImputer(missing_values=np.nan, strategy='constant')
    imputed_data['zero'] =  zero_imp.fit_transform(pilot.values)

    linear_imp = LinearRegression()
    pilot_nonmiss = pilot.dropna(axis=0)
    pilot_miss = pilot[pilot[sleep_cols[0]].isna()]
    reg = linear_imp.fit(pilot_nonmiss[activity_cols], pilot_nonmiss[sleep_cols])
    imputed_data['linear'] = reg.predict(pilot_miss[activity_cols])

    knn_imp = KNNImputer(n_neighbors=5, weights="distance")
    imputed_data['knn'] = knn_imp.fit_transform(pilot.values)

    iter_imp = IterativeImputer(random_state=0)
    imputed_data['iterative'] = iter_imp.fit_transform(pilot.values)

    interp_data = pilot.interpolate(method='linear', limit_direction='forward', axis=0)
    imputed_data['interpolation'] = interp_data.to_numpy()

    imputed_data['imice'] = mice(pilot.values)

    for key in imputed_data.keys():
        if key!='linear':
            imputed_data[key] = imputed_data[key][miss_ids,0:5]
            
    return imputed_data

######################### Iterate over many times ############################
mse = dict.fromkeys(['mean','common', 'zero', 'linear', 'knn', 'iterative', 'interpolation', 'imice'])
for key in mse.keys():
    mse[key] = []
for i in range(iteration):
    pilot_miss, miss_ids = generate_missing(pilot)
    imputed_data = impute_data(pilot_miss, miss_ids)
    y_true = gold.loc[gold.index[miss_ids],sleep_cols].values
    for key in imputed_data.keys():
        mse[key].append(mean_squared_error(y_true, imputed_data[key], squared=True))
    del pilot_miss, miss_ids, imputed_data, y_true
    
################################ Plot ########################################
to_plot = pd.DataFrame.from_dict(mse)
fig = plt.figure(figsize=(8,4),dpi=300)
sns.set_style("dark")
sns.set_context(context="paper", font_scale=.4)
ax = sns.violinplot(data=to_plot, orient="v")