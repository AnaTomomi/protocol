import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.transforms as mtransforms
import matplotlib

######################### Pepare paths #######################################
#path = '/u/68/trianaa1/unix/trianaa1/protocol/data/pilot_i/sensors'
path = '/u/68/trianaa1/unix/trianaa1/protocol/data/pilot_iii/sensors'
begin = '2021-08-02' #'2020-07-06'
end = '2021-09-07' #'2020-07-20'

######################### Helper functions ###################################
def find_missing(df):
    indices = list(np.where(df.isnull())[0])
    return indices

def find_missing_percent(df):
    return round(100*(len(list(np.where(df.isnull())[0]))/len(df)),2)

def highlight_datetimes(indices, ax):
    i = 0
    while i < len(indices):
        if indices[i] == 0:
            ax.axvspan(df.index[indices[i]], df.index[indices[i] + 1], facecolor='tomato', edgecolor='none')
        else:
            ax.axvspan(df.index[indices[i]-1], df.index[indices[i] + 1], facecolor='tomato', edgecolor='none')
        i += 1

def create_linbins(start, end, n_bins):
    bins = np.linspace(start, end, n_bins)
    return bins

def prepare_data(path, begin, end, column):
    data = pd.read_csv(path)
    data["date"] = pd.DatetimeIndex(pd.to_datetime(data["time"], unit='s')).tz_localize('UTC').tz_convert('Europe/Helsinki')
    data.set_index('date', inplace=True)
    data = data.loc[begin:end]
    data[column] = pd.to_numeric(data[column])
    data = data[[column]].reset_index()
    if 'location' in path:
        data = data.replace(0, np.nan)
    binned = data.resample('1H', on="date").mean()
    return binned

def prepare_data_nonprocessed(path, begin, end, column):
    data = pd.read_csv(path)
    data["date"] = pd.DatetimeIndex(pd.to_datetime(data["time"], unit='s')).tz_localize('UTC').tz_convert('Europe/Helsinki')
    data.set_index('date', inplace=True)
    data = data.loc[begin:end]
    data["data"] = 0
    data.data[data[column]>0] = 1
    data = data[["data"]].reset_index()
    binned = data.resample('1H', on="date").mean()
    return binned
    

def prepare_ESM_data(path, begin, end):
    data = pd.read_csv(path)
    data = data[(data['id']=='dq_05')|(data['id']=='dq_06')|(data['id']=='dq_07')|(data['id']=='dq_08')|(data['id']=='dq_09')|(data['id']=='dq_10')|(data['id']=='dq_11')]
    data["date"] = pd.DatetimeIndex(pd.to_datetime(data["time"], unit='s')).tz_localize('UTC').tz_convert('Europe/Helsinki')
    data.set_index('date', inplace=True)
    data = data.loc[begin:end]
    data['answer'] = pd.to_numeric(data['answer'])
    data = data.drop_duplicates(subset=['time','id'], keep='first').reset_index()
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%m-%d-%y')
    data = pd.pivot_table(data, values='answer', index=['date'], columns=['id'], aggfunc=np.sum)
    data['neg affect'] = data.sum(axis=1)
    data.reset_index(inplace=True)
    data["date"] = pd.to_datetime(data["date"])
    data.set_index("date", inplace=True)
    data = data[["neg affect"]]
    return data
##############################################################################

#Daily binned
data = pd.read_csv(f'{path}/sub-01_sensor-oura.csv')
dates_d = pd.to_datetime(data["date"], infer_datetime_format=True)
data.columns = data.columns.str.replace('_',' ')
df1 = data["Restless Sleep"].to_frame()
df1.index = dates_d
df1 = df1.loc[begin:end]
df1.rename(columns={"Restless Sleep":" restless \n sleep"}, inplace=True)

df2 = data["Steps"].to_frame()
df2.index = dates_d
df2 = df2.loc[begin:end]
df2.rename(columns={"Steps":" steps"}, inplace=True)

df3 = prepare_ESM_data(f'{path}/sub-01_sensor-esm.csv', begin, end)
df3.rename(columns={"neg affect":" negative \n affect"}, inplace=True)

#Hourly binned
df4 = prepare_data(f'{path}/sub-01_sensor-battery.csv', begin, end, column='battery_level')
df4.rename(columns={"battery_level":" battery \n level"}, inplace=True)
df5 = prepare_data(f'{path}/sub-01_sensor-light.csv', begin, end, column='double_light_lux')
df5.rename(columns={"double_light_lux":" light \n intensity"}, inplace=True)
df6 = prepare_data(f'{path}/sub-01_sensor-wifi.csv', begin, end, column='rssi')
df6.rename(columns={"rssi":" wifi signal \n intensity"}, inplace=True)
df7 = prepare_data(f'{path}/sub-01_sensor-location.csv', begin, end, column='double_latitude')
df7[df7>0] = 1
df7.rename(columns={"double_latitude":" location \n data"}, inplace=True)

dfs = [df1, df2, df3, df4, df5, df6, df7]
label = ['A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.']

#two graphs
fig, axes = plt.subplots(nrows=7, ncols=1, sharex=True, figsize=(9,9))
form = md.DateFormatter("%d-%m")
font = {'family' : 'Arial','size': 14}
matplotlib.rc('font', **font)
dates_d = df1.index

for i, df in enumerate(dfs): 
    indices = find_missing(df)
    percent = find_missing_percent(df)
    trans = mtransforms.ScaledTranslation(-20/72, 7/72, fig.dpi_scale_trans)
    axes[i].text(0.0, 1.0, label[i], transform=axes[i].transAxes + trans, va='bottom')
    for v in df.columns.tolist():
        axes[i].plot(df[v], label=v, color='black', linewidth=2)
    axes[i].set_ylabel(df.columns[0].lower())
    axes[i].set_title(f'missing data={percent}%', loc="right", fontsize=14)
    axes[i].xaxis.grid(b=True, which='major', color='black', linestyle='--', alpha=1) #add xaxis gridlines
    highlight_datetimes(indices, axes[i])
axes[0].set_xlim(min(dates_d), max(dates_d))
axes[0].xaxis.set_major_formatter(form)
axes[6].set_xlabel('dates (DD-MM)')
fig.align_ylabels(axes)
fig.tight_layout()
plt.show()
plt.savefig('/u/68/trianaa1/unix/trianaa1/protocol/results/pilot_iii/sensor_missing.pdf')

##############################################################################