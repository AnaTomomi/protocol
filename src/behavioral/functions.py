################################################################################
# This is the main file for preprocessing smartphone sensor data               #
#                                                                              #
# Contributors: Ana Triana                                       #
################################################################################

import numpy as np
import pandas as pd
from pandas import Series
import matplotlib.pyplot as plt
import seaborn as sns
import time
import datetime
import pytz

def ESM(path,begin=None,end=None):
    
    assert isinstance(path, str),"this is not a valid path"
    
    esm=pd.read_csv(path+"AwareESM.csv")
    esm["index"] = pd.to_datetime(esm["time"], unit="s")
    esm = esm.set_index(esm["index"])
    esm = esm.tz_localize('UTC').tz_convert('Europe/Helsinki')
    esm = esm.drop(columns=['device','user','time','time_asked','type','instructions','submit', 'notification_timeout', 'index'])
    esm['datetime'] = esm.index
    esm['datetime'] = esm['datetime'].dt.floor('d')
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = esm.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = esm.index[len(esm)-1]
    
    esm = esm.sort_index()
    esm=esm.loc[begin:end]
    
    morning = esm[(esm['id']=='am_01') | (esm['id']=='am_02') | (esm['id']=='am_03')]
    daily = esm[(esm['id']=='dq_01') | (esm['id']=='dq_02') | (esm['id']=='dq_03') | (esm['id']=='dq_04') | (esm['id']=='dq_05') | (esm['id']=='dq_06') | (esm['id']=='dq_07') | (esm['id']=='dq_08') | (esm['id']=='dq_09') | (esm['id']=='dq_10') | (esm['id']=='dq_11') | (esm['id']=='dq_12')]
    evening = esm[(esm['id']=='pm_02') | (esm['id']=='pm_03') | (esm['id']=='pm_04')]
    
    morning['answer'] = morning['answer'].map({'Yes': 1, 'No': 0})
    morning = morning.pivot_table(index='datetime', columns='id', values='answer')
    daily['answer']=pd.to_numeric(daily['answer'])
    daily = daily.pivot_table(index='datetime', columns='id', values='answer', aggfunc='mean')
    evening['answer'] = evening['answer'].map({'Yes': 1, 'No': 0, '0': 0, '1-2': 1})
    evening['datetime'] = evening.index - pd.DateOffset(hours=2)
    evening['datetime'] = evening['datetime'].dt.floor('d')
    evening = evening.pivot_table(index='datetime', columns='id', values='answer')
    
    return morning, daily, evening
    

#Application
def shutdown_info(path,begin=None,end=None):
    """ Returns a DataFrame with the timestamps of when the phone has shutdown.
    
    
    NOTE: This is a helper function created originally to preprocess the application 
    info data
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    shutdown: Dataframe
    
    """
    
    assert isinstance(path, str),"this is not a valid path"
    
    bat=pd.read_csv(path+"AwareBattery.csv")
    bat["datetime"] = pd.to_datetime(bat["time"], unit="s")
    bat = bat.set_index(bat["datetime"])
    bat = bat.tz_localize('UTC').tz_convert('Europe/Helsinki')
    bat = bat.drop(columns=['device','user','time','battery_health','battery_adaptor','battery_level','datetime'])
    #bat = bat.reset_index()
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = bat.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = bat.index[len(bat)-1]
    
    bat = bat.sort_index()
    bat=bat.loc[begin:end]
    bat['battery_status']=pd.to_numeric(bat['battery_status'])
    shutdown = bat[bat['battery_status'].between(-3, 0, inclusive=False)]
    return shutdown

def screen_off(path,begin=None,end=None):
    """ Returns a DataFrame with the timestamps of when the screen has changed 
    to "OFF" status.
    
    
    NOTE: This is a helper function created originally to preprocess the application 
    info data
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    screen: Dataframe
    
    """
    
    assert isinstance(path, str),"this is not a valid path"
    
    screen = pd.read_csv(path+"AwareScreen.csv")
    screen["datetime"] = pd.to_datetime(screen["time"], unit="s")
    screen = screen.set_index(screen["datetime"])
    screen = screen.tz_localize('UTC').tz_convert('Europe/Helsinki')
    screen=screen.drop_duplicates(subset=['datetime'],keep='first')
    screen = screen.drop(columns=['device','user','time','datetime'])
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = screen.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = screen.index[len(screen)-1]
                         
    screen = screen.sort_index()
    screen=screen.loc[begin:end]
    screen['screen_status']=pd.to_numeric(screen['screen_status'])
    
    #Include the missing points that are due to shutting down the phone
    shutdown = shutdown_info(path,begin,end)
    shutdown=shutdown.rename(columns={'battery_status':'screen_status'})
    shutdown['screen_status']=0
    
    if not shutdown.empty:
        screen = screen.merge(shutdown, how='outer', left_index=True, right_index=True)
        screen['screen_status'] = screen.fillna(0)['screen_status_x'] + screen.fillna(0)['screen_status_y']
        screen = screen.drop(['screen_status_x','screen_status_y'], axis=1)
   
    #Detect missing data points
    screen['missing']=0
    screen['next']=screen['screen_status'].shift(-1)
    screen['dummy']=screen['screen_status']-screen['next']
    screen['missing'] = np.where(screen['dummy']==0, 1, 0)
    screen['missing'] = screen['missing'].shift(1)
    screen = screen.drop(['dummy','next'], axis=1)
    screen = screen.fillna(0)
    
    #Discard missing values
    screen = screen[screen.missing == 0]
    #Select only those OFF events
    screen = screen[screen.screen_status == 0]
    del screen['missing']
    return screen

def get_seconds(time_delta):
    """ Converts the timedelta to seconds
    
    
    NOTE: This is a helper function 
    
    Parameters:
    --------
    time_delta: Timedelta
    
    """
    
    return time_delta.dt.total_seconds()

def app_duration(path,begin=None,end=None,app_list_path=None):
    """ Returns two DataFrames contanining the duration and number of events per
    group of apps, e.g. number of times a person used communication apps like 
    WhatsApp, Telegram, Messenger, sms, etc. and for how long these apps were 
    used in a day (in seconds). 
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional
    app_list_path: path to the csv file where the apps are classified into groups

    
    Returns:
    --------
    duration: Dataframe
    count: Dataframe
    
    """
    
    assert isinstance(path, str),"this is not a correct path"
    
    app = pd.read_csv(path+"AwareApplicationNotifications.csv")
    app["datetime"] = pd.to_datetime(app["time"], unit="s")
    app = app.set_index(app["datetime"])
    app = app.tz_localize('UTC').tz_convert('Europe/Helsinki')
    app = app.drop_duplicates(subset=['datetime'],keep='first')
    app = app.drop(columns=['device','user','time','defaults','sound','vibrate','datetime'])
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = app.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = app.index[len(app)-1]
    if(app_list_path==None):
        app_list_path = '/u/68/trianaa1/unix/Documents/niima-code/Datastreams/Phone/apps_group.csv'  
    
    app = app.sort_index()
    app=app.loc[begin:end]
    
    #Classify the apps into groups
    app_list=pd.read_csv(app_list_path) 
    app['group']=np.nan
    for index, row in app.iterrows():
        group=app_list.isin([row['application_name']]).any()
        group=group.reset_index()
        if (not any(group[0])):
            app.loc[index,'group']=10
        else:
            app.loc[index,'group']=group.index[group[0] == True].tolist()[0]
    
    #Insert missing data due to phone being shut down
    shutdown = shutdown_info(path,begin,end)
    if not shutdown.empty:
        shutdown['group']=11
        shutdown['battery_status'] = 'off'
        app = app.merge(shutdown, how='outer', left_index=True, right_index=True)
        app['application_name'] = app['application_name'].replace(np.nan, 'off', regex=True)
        app['group_x'] = app['group_x'].replace(np.nan, 11, regex=True)
        app = app.drop(['battery_status','group_y'], axis=1)
        app=app.rename(columns={'group_x':'group'})
    
    #Insert missing data due to the screen being off
    screen=screen_off(path,begin,end)
    if not screen.empty:
        app = app.merge(screen, how='outer', left_index=True, right_index=True)
        app['application_name'] = app['application_name'].replace(np.nan, 'off', regex=True)
        app['group'] = app['group'].replace(np.nan, 11, regex=True)
        del app['screen_status']
            
    #Calculate the app duration per group
    app['duration']=np.nan
    app['datediff']=app.index
    app['duration']=app['datediff'].diff()
    app['duration'] = app['duration'].shift(-1)
    
    app['datediff'] = app['datediff'].dt.floor('d')
    
    duration=pd.pivot_table(app,values='duration',index='datediff', columns='group', aggfunc=np.sum)
    duration = duration.apply(get_seconds,axis=1)
    exist_col = list(duration.columns)
    all_cols = list(np.linspace(0,11,12))
    all_cols = [float(v) for v in all_cols]
    insert_columns = list(set(all_cols) - set(exist_col))
    for new_column in insert_columns:
        duration.insert(loc=0, column=new_column, value=0)
    duration.columns = duration.columns.map({0.0: 'app_duration_sports', 1.0: 'app_duration_games', 2.0: 'app_duration_communication', 3.0: 'app_duration_social_media', 4.0: 'app_duration_news', 5.0: 'app_duration_travel', 6.0: 'app_duration_shop', 7.0: 'app_duration_entretainment', 8.0: 'app_duration_work_study', 9.0: 'app_duration_transportation', 10.0: 'app_duration_other', 11.0: 'app_duration_off'})
    
    count=pd.pivot_table(app,values='duration',index='datediff', columns='group', aggfunc='count')
    exist_col = list(count.columns)
    all_cols = list(np.linspace(0,11,12))
    all_cols = [float(v) for v in all_cols]
    insert_columns = list(set(all_cols) - set(exist_col))
    for new_column in insert_columns:
        count.insert(loc=0, column=new_column, value=0)
    count.columns = count.columns.map({0.0: 'app_count_sports', 1.0: 'app_count_games', 2.0: 'app_count_communication', 3.0: 'app_count_social_media', 4.0: 'app_count_news', 5.0: 'app_count_travel', 6.0: 'app_count_shop', 7.0: 'app_count_entretainment', 8.0: 'app_count_work_study', 9.0: 'app_count_transportation', 10.0: 'app_count_other', 11.0: 'app_count_off'})
    
    duration = duration.fillna(0)
    count = count.fillna(0)
    return duration, count

#Communication
def call_info(path,begin=None,end=None):
    """ Returns a DataFrame contanining the duration and number of events per
    type of calls (outgoing, incoming, missed). The Dataframe summarizes the 
    duration of the incoming/outgoing calls in seconds, number of those events,
    and how long (in seconds) the person has spoken to the top 5 contacts (most
    frequent)
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    duration: Dataframe
    
    """
    
    assert isinstance(path, str),"this path is not correct"
    
    call = pd.read_csv(path+"AwareCalls.csv")
    call["dates"] = pd.to_datetime(call["time"], unit="s")
    call = call.set_index(call["dates"])
    call = call.tz_localize('UTC').tz_convert('Europe/Helsinki')
    call['datetime'] = call.index
    call = call.drop_duplicates(subset=['datetime'],keep='first')
    call = call.drop(columns=['device','user','time','dates'])
    
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = call.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = call.index[len(call)-1]
    
    call = call.sort_index()
    call = call.loc[begin:end]
    call['datetime'] = call['datetime'].dt.floor('d')
    call['call_duration']=pd.to_numeric(call['call_duration'])
    duration = call.groupby(['datetime']).sum()
    
    missed_calls = call.loc[(call['call_type'] == 'missed')].groupby(['datetime']).count()
    outgoing_calls = call.loc[(call['call_type'] == 'outgoing')].groupby(['datetime']).count()
    incoming_calls = call.loc[(call['call_type'] == 'incoming')].groupby(['datetime']).count()
    duration['call_missed'] = missed_calls['call_type']
    duration['call_outgoing'] = outgoing_calls['call_type']
    duration['call_incoming'] = incoming_calls['call_type']
    duration2 = call.pivot_table(index='datetime', columns='call_type', values='call_duration',aggfunc='sum')
    if ('incoming' in duration2.columns):
        duration2 = duration2.rename(columns={'incoming': 'call_incoming_duration'})
    if ('outgoing' in duration2.columns):
        duration2 = duration2.rename(columns={'outgoing': 'call_outgoing_duration'})
    if ('missed' in duration2.columns):
        duration2 = duration2.drop(columns=['missed'])
    duration = duration.merge(duration2, how='outer', left_index=True, right_index=True)
    duration = duration.fillna(0)
    if ('missed_y' in duration.columns):
        duration =  duration.drop(columns=['missed_y'])
    #duration.columns = ['total_call_duration', 'call_missed', 'call_outgoing', 'call_incoming', 'call_incoming_duration', 'call_outgoing_duration']
    
    #Now let's calculate something more sophisticated... Let's see 
    trace = call.groupby(['trace']).count()
    trace = trace.sort_values(by=['call_type'], ascending=False)
    top5 = trace.index.values.tolist()[:5]
    call['frequent']=0
    call = call.reset_index()
    call = call.rename(columns={'index': 'date'})
    for index, row in call.iterrows():
        if (call.loc[index,'trace'] in top5):
            call.loc[index,'frequent']=1
    call['frequent'] = call['frequent'].astype(str)
    duration2 = call.pivot_table(index='dates', columns=['call_type','frequent'], values='call_duration',aggfunc='sum')
    duration2.columns = ['_'.join(col) for col in duration2.columns]
    duration2 = duration2.reset_index() 
    
    #duration2.columns = ['datetime','incoming_0','incoming_1','missed_0','missed_1','outgoing_0','outgoing_1']
    duration2['datetime'] = duration2['dates'].dt.floor('d')
    duration2 = duration2.groupby(['datetime']).sum()
    if ('incoming_0' in duration2.columns):
        duration2 = duration2.drop(columns=['incoming_0'])
    if ('missed_0' in duration2.columns):
        duration2 = duration2.drop(columns=['missed_0'])
    if ('missed_1' in duration2.columns):
        duration2 = duration2.drop(columns=['missed_1'])
    if ('outgoing_0' in duration2.columns):
        duration2 = duration2.drop(columns=['outgoing_0'])
    duration = duration.merge(duration2, how='outer', left_index=True, right_index=True)
    duration = duration.rename(columns={'incoming_1': 'incoming_duration_top5', 'outgoing_1': 'outgoing_duration_top5'})
    return duration

def sms_info(path,begin=None,end=None):
    """ Returns a DataFrame contanining the number of events per type of messages 
    SMS (outgoing, incoming). The Dataframe summarizes the number of the 
    incoming/outgoing sms and how many of those correspond to the top 5 contacts 
    (most frequent with whom the subject exchanges texts)
        
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    sms_stats: Dataframe
    
    """
    
    assert isinstance(path, str),"this path is not correct"
    
    sms = pd.read_csv(path+"AwareMessages.csv")
    sms["dates"] = pd.to_datetime(sms["time"], unit="s")
    sms = sms.set_index(sms["dates"])
    sms = sms.tz_localize('UTC').tz_convert('Europe/Helsinki')
    sms['datetime'] = sms.index
    sms = sms.drop_duplicates(subset=['datetime'],keep='first')
    sms = sms.drop(columns=['device','user','time','dates'])
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = sms.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = sms.index[len(sms)-1]
            
    sms['datetime'] = sms['datetime'].dt.floor('d')
    sms = sms.sort_index()
    sms = sms.loc[begin:end]
    if (len(sms)>0):
        sms_stats = sms.copy()
        sms_stats['dummy'] = 1
        sms_stats = sms_stats.pivot_table(index='datetime', columns='message_type', values='dummy',aggfunc='sum')
        
        #Now let's move to somethign more sophisticated
        trace = sms.groupby(['trace']).count()
        trace = trace.sort_values(by=['message_type'], ascending=False)
        top5 = trace.index.values.tolist()[:5]
        sms['frequent']=0
        sms = sms.reset_index()
        sms = sms.rename(columns={'index': 'dates'})
        for index, row in sms.iterrows():
            if (sms.loc[index,'trace'] in top5):
                sms.loc[index,'frequent']=1
                sms['frequent'] = sms['frequent'].astype(str)
                sms['dummy']=1
        dummy = sms.pivot_table(index='dates', columns=['message_type','frequent'], values='dummy',aggfunc='sum')
        dummy.columns = ['_'.join(col) for col in dummy.columns]
        dummy = dummy.reset_index() 
        dummy['datetime'] = dummy['dates'].dt.floor('d')
        dummy = dummy.groupby(['datetime']).sum()
        if ('incoming_0' in dummy.columns):
            dummy = dummy.drop(columns=['incoming_0'])
        if ('outgoing_0' in dummy.columns):
            dummy = dummy.drop(columns=['outgoing_0'])
        sms_stats = sms_stats.merge(dummy, how='outer', left_index=True, right_index=True)
        sms_stats = sms_stats.rename(columns={'incoming_1': 'sms_incoming_top5', 'outgoing_1': 'sms_outgoing_top5'})
        sms_stats = sms_stats.fillna(0)
        if ('incoming' in sms_stats.columns):
            sms_stats = sms_stats.rename(columns={'incoming': 'sms_incoming'})
        if ('outgoing' in sms_stats.columns):
            sms_stats = sms_stats.rename(columns={'outgoing': 'sms_outgoing'})
        return sms_stats
    else:
        sms_stats = pd.DataFrame()
        return sms_stats
       
def communication_info(path,begin=None,end=None):
    """ Returns a DataFrame contanining all the information extracted from 
    communication's events (calls, sms, and communication apps like WhatsApp,
    Telegram, Messenger, etc.). Regarding calls, this function contains the 
    duration of the incoming/outgoing calls in seconds, number of those events,
    and how long (in seconds) the person has spoken to the top 5 contacts (most
    frequent). Regarding the SMSs, this function contains the number of incoming
    /outgoing events, and the top 5 contacts (most frequent). Aditionally, we 
    also include the calculated duration of the incoming/outgoing sms and the 
    lags (i.e. the period between receiving a message and reading/writing a 
    reply). Regarding the app, the duration of communication events is summarized. 
    
    This function also sums all the different durations (calls, SMSs, apps) and 
    provides the duration (in seconds) that a person spent communicating during
    the day. 
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    call_summary: Dataframe
    
    """
    
    assert isinstance(path, str),"this path is not correct"
    
    app = pd.read_csv(path+"AwareApplicationNotifications.csv")
    app["datetime"] = pd.to_datetime(app["time"], unit="s")
    app = app.set_index(app["datetime"])
    app = app.tz_localize('UTC').tz_convert('Europe/Helsinki')
    app = app.drop_duplicates(subset=['datetime'],keep='first')
    app = app.drop(columns=['device','user','time','defaults','sound','vibrate','datetime'])
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = app.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = app.index[len(app)-1]
    
    duration_app, count_app = app_duration(path,begin,end)
    call_summary = call_info(path,begin,end)
    sms_summary = sms_info(path,begin,end)
    
    if (not sms_summary.empty):
        call_summary = call_summary.merge(sms_summary, how='outer', left_index=True, right_index=True)
        call_summary = call_summary.fillna(0)
    
    #Now let's see if there is any info from the apps worth bringin back
    if ('app_duration_communication' in duration_app.columns): #2 is the number for communication apps
        comm_app = duration_app['app_duration_communication']#.dt.seconds
        comm_app = comm_app.fillna(0)
        comm_app = comm_app.to_frame()
    if ('app_duration_social_media' in duration_app.columns): #2 is the number for communication apps
        social_app = duration_app['app_duration_social_media']#.dt.seconds
        social_app = social_app.fillna(0)
        social_app = social_app.to_frame()
    try:
        social_app
        try:
            comm_app
            comm_app = comm_app.merge(social_app, how='outer', left_index=True, right_index=True)
        except NameError:
            comm_app = social_app
    except NameError:
        pass
    try:
        comm_app
        call_summary = call_summary.merge(comm_app, how='outer', left_index=True, right_index=True)
    except NameError:
        pass
    call_summary = call_summary.fillna(0)
    
    if ('communication' in call_summary.columns):
        call_summary['total_comm_duration'] = call_summary['call_duration']+call_summary['communication']
    if (('social_media' in call_summary.columns) and ('communication' in call_summary.columns)):
        call_summary['total_comm_duration'] = call_summary['call_duration']+call_summary['social_media']+call_summary['communication']
    if ('app_duration_communication' in call_summary.columns):
        call_summary=call_summary.rename(columns={'app_duration_communication':'comm_apps_duration'})
    if ('app_duration_social_media' in call_summary.columns):
        call_summary=call_summary.rename(columns={'app_duration_social_media':'social_apps_duration'})

        
    all_columns = ['call_duration', 'call_missed', 'call_outgoing', 'call_incoming',
                   'call_incoming_duration', 'call_outgoing_duration',
                   'incoming_duration_top5', 'outgoing_duration_top5', 'sms_incoming',
                   'sms_outgoing', 'sms_incoming_top5', 'sms_outgoing_top5']
    insert_columns = list(set(all_columns).difference(call_summary.columns))
    for new_column in insert_columns:
            call_summary.insert(loc=0, column=new_column, value=0)
    return call_summary
  
#Location
def location_data(path,begin=None,end=None):
    """ Reads the readily, preprocessed location data from the right database. 
    The data already contains the aggregation of the GPS data (more info here:
    https://github.com/CxAalto/koota-server/blob/master/kdata/converter.py). 
        
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    location: Dataframe
    
    """
    
    assert isinstance(path, str),"user not given in string format"
    
    location = pd.read_csv(path+"AwareLocationDay.csv")           
    location = location.drop(['device','user','diameter'],axis=1)
    location=location.drop_duplicates(subset=['day'],keep='first')
    location['day']=pd.to_datetime(location['day'], format='%Y-%m-%d')
    location=location.set_index('day')
    location.index = pd.to_datetime(location.index).tz_localize('Europe/Helsinki')
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = location.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = location.index[-1]
    
    location=location.sort_index()    
    location=location.loc[begin:end]
    return location

#Screen
def screen_duration(path,begin=None,end=None):
    """ Returns two DataFrames contanining the duration and number of events for
    the screen transitions (ON to OFF, OFF to ON, OFF to IN USE, IRRELEVANT 
    transitions). E.g. duration (in seconds) of the phone being ON during a day, 
    or number of times the screen was on during the day. 
    
    Parameters:
    --------
    database: Niimpy database
    user: string
    begin: datetime, optional
    end: datetime, optional

    
    Returns:
    --------
    duration: Dataframe
    count: Dataframe
    
    """
    
    assert isinstance(path, str),"usr not given in string format"
    
    screen = pd.read_csv(path+"AwareScreen.csv")
    screen["index"] = pd.to_datetime(screen["time"], unit="s")
    screen = screen.set_index(screen["index"])
    screen = screen.tz_localize('UTC').tz_convert('Europe/Helsinki')
    screen['datetime'] = screen.index
    screen = screen.drop_duplicates(subset=['datetime'],keep='first')
    screen = screen.drop(['device','user','time'],axis=1)
    
    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = screen.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = screen.index[len(screen)-1]  
    
    screen = screen.sort_index()
    screen=screen.loc[begin:end]
    screen['screen_status']=pd.to_numeric(screen['screen_status'])
    
    #Include the missing points that are due to shutting down the phone
    shutdown = shutdown_info(path,begin,end)
    shutdown=shutdown.rename(columns={'battery_status':'screen_status'})
    shutdown['screen_status']=0
    screen = screen.merge(shutdown, how='outer', left_index=True, right_index=True)
    screen['screen_status'] = screen.fillna(0)['screen_status_x'] + screen.fillna(0)['screen_status_y']
    screen = screen.drop(['screen_status_x','screen_status_y'],axis=1)
    screen = screen.drop(['index','datetime'],axis=1)
    screen['datetime']=screen.index
        
    #Detect missing data points
    screen['missing']=0
    screen['next']=screen['screen_status'].shift(-1)
    screen['dummy']=screen['screen_status']-screen['next']
    screen['missing'] = np.where(screen['dummy']==0, 1, 0)
    screen['missing'] = screen['missing'].shift(1)
    screen = screen.drop(['dummy','next'], axis=1)
    screen = screen.fillna(0)
    
    #Exclude missing datapoints, but keep track of how many were excluded first
    if (1 in screen['missing'].unique()):
        missing_count=(screen['missing'].value_counts()[1]/screen['missing'].value_counts()[0])*100
        print('Missing datapoints (%): ' + str(missing_count))
    else:
        print('No missing values')
    
    #Discard missing values
    screen = screen[screen.missing == 0]
    
    #Calculate the duration
    screen['duration']=np.nan
    screen['duration']=screen['datetime'].diff()
    screen['datetime'] = screen['datetime'].dt.floor('d')
    screen['duration'] = screen['duration'].shift(-1)
    
    #Classify the event 
    screen=screen.rename(columns={'missing':'group'})
    screen['next']=screen['screen_status'].shift(-1)
    screen['next']=screen['screen_status'].astype(int).astype(str)+screen['screen_status'].shift(-1).fillna(0).astype(int).astype(str)   
    screen.group[(screen.next=='01') | (screen.next=='02')]=1
    screen.group[(screen.next=='03') | (screen.next=='13') | (screen.next=='23')]=2
    screen.group[(screen.next=='12') | (screen.next=='21') | (screen.next=='31') | (screen.next=='32')]=3
    del screen['next']
    screen['group'] = screen['group'].shift(1)
    screen.loc[:1,'group']=0
    del screen['screen_status']
        
    #Discard the first and last row because they do not have all info. We do not
    #know what happened before or after these points. 
    screen = screen.iloc[1:]
    screen = screen.iloc[:-1]
    
    #Discard any datapoints whose duration in “ON” and “IRRELEVANT” states are 
    #longer than 2 hours
    thr = pd.Timedelta('2 hours')
    screen = screen[~((screen.group==1) & (screen.duration>thr))]
    
    #Finally organize everything
    duration=pd.pivot_table(screen,values='duration',index='datetime', columns='group', aggfunc=np.sum)
    #duration['total']=duration.sum(axis=1)
    #mean_hours=duration['total'].mean()
    #print('mean hours in record per day: ' + str(mean_hours))
    duration.columns = duration.columns.map({0.0: 'sc_duration_off', 1.0: 'sc_duration_on', 2.0: 'sc_duration_use', 3.0: 'sc_duration_irrelevant', 4.0: 'sc_duration_total'})
    duration = duration.apply(get_seconds,axis=1)
    count=pd.pivot_table(screen,values='duration',index='datetime', columns='group', aggfunc='count')
    count.columns = count.columns.map({0.0: 'sc_count_off', 1.0: 'sc_count_on', 2.0: 'sc_count_use', 3.0: 'sc_count_irrelevant', 4.0: 'sc_count_total'})
    return duration, count

def battery_discharge(path, begin=None, end=None):
    """ Returns a DataFrame with battery data for a user.
    Parameters:
    --------
    database: Niimpy database
    user: string
    start: datetime, optional
    end: datetime, optional
    """
    
    assert isinstance(path, str),"this path is not correct"

    bat = pd.read_csv(path+"AwareBattery.csv")
    bat["index"] = pd.to_datetime(bat["time"], unit="s")
    bat = bat.set_index(bat["index"])
    bat = bat.tz_localize('UTC').tz_convert('Europe/Helsinki')
    bat['datetime'] = bat.index

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = bat.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = bat.index[len(bat)-1]  

    bat = bat[(bat['datetime']>=begin) & (bat['datetime']<=end)]    
        
    bat['battery_level'] = pd.to_numeric(bat['battery_level'])

    bat = bat.drop_duplicates(subset=['datetime','user','device'],keep='last')
    bat = bat.drop(['user','device','time','index'],axis=1)
    bat['battery_level'] = pd.to_numeric(bat['battery_level'])
    bat['tvalue'] = bat.index
    bat['tdelta'] = (bat['tvalue']-bat['tvalue'].shift()).fillna(pd.Timedelta(seconds=0))    
    bat['bdelta'] = (bat['battery_level']-bat['battery_level'].shift()).fillna(0)
    bat['charge']= ((bat['bdelta'])/((bat['tdelta']/ pd.Timedelta(seconds=1))))
    bat = bat.drop(['battery_level','battery_status','battery_health','tvalue','tdelta','bdelta'],axis=1)
    bat['datetime'] = bat['datetime'].dt.floor('d')
    
    bat =  bat.groupby(['datetime']).sum()
    bat = bat.drop(['battery_adaptor'],axis=1)
    
    return bat

def smartwatch(path, begin=None, end=None):
    """ Returns a DataFrame with data from smartwatch for a user.
    Parameters:
    --------
    path: string
    start: datetime, optional
    end: datetime, optional
    """
    
    assert isinstance(path, str),"this path is not correct"

    sw = pd.read_csv(path+"garmin.csv")
    sw['Date'] = pd.to_datetime(sw["Date"])
    sw = sw.set_index(sw["Date"])
    sw = sw.tz_localize('Europe/Helsinki')
    sw = sw.drop(['Date'],axis=1)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = sw.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = sw.index[len(sw)-1]  
    
    sw = sw.sort_index()
    sw = sw.loc[begin:end]    
            
    return sw

def oura(path, begin=None, end=None):
    """ Returns a DataFrame with data from oura for a user.
    Parameters:
    --------
    path: string
    start: datetime, optional
    end: datetime, optional
    """
    
    assert isinstance(path, str),"this path is not correct"

    oura = pd.read_csv(path+"oura.csv")
    oura['date'] = pd.to_datetime(oura["date"])
    oura = oura.set_index(oura["date"])
    oura = oura.tz_localize('Europe/Helsinki')
    if 'Sleep_Timing.1' in oura:
        oura = oura.drop(['date', 'Sleep_Timing.1', 'Bedtime_Start', 'Bedtime_End'],axis=1)
    if 'Sleep Timing.1' in oura:
        oura = oura.drop(['date', 'Sleep Timing.1', 'Bedtime Start', 'Bedtime End'],axis=1)

    if(begin!=None):
        assert isinstance(begin,pd.Timestamp),"begin not given in timestamp format"
    else:
        begin = oura.index[0]
    if(end!= None):
        assert isinstance(end,pd.Timestamp),"end not given in timestamp format"  
    else:
        end = oura.index[len(oura)-1]  
    
    oura = oura.sort_index()
    oura = oura.loc[begin:end] 
    oura = oura.interpolate()
            
    return oura
