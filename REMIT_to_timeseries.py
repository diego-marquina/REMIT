# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 17:01:00 2021

@author: Diego.Marquina
"""
#%%
import pandas as pd
import glob
from plotly.offline import init_notebook_mode, iplot
from plotly.graph_objs import *
from plotly.subplots import make_subplots
init_notebook_mode(connected=True) 
pd.options.plotting.backend = "plotly"

#%%
path = r'./entsoe/UnavailabilityOfGenerationUnits_15.1.A_B' # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, sep='\t')
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

#%%
df_fr = frame.loc[frame.MapCode=='FR',:].copy()
df_flamanville2 = df_fr.loc[df_fr.UnitName.str.contains('FLAMANVILLE 2'),:]
df_flam_active = df_flamanville2.loc[df_flamanville2.Status=='Active',:]
df_flam_active_latest = df_flam_active.loc[df_flam_active.groupby('MRID')['Version'].idxmax(),:]
df_flam_a_l_CTA = df_flam_active_latest.loc[df_flam_active_latest.AreaTypeCode=='CTA',:]
df_flam_a_l_CTA.loc[:,['StartTS','EndTS','UpdateTime']] = df_flam_a_l_CTA.loc[:,['StartTS','EndTS','UpdateTime']].apply(pd.to_datetime).copy()
df_flam_a_l_CTA = df_flam_a_l_CTA.sort_values(['StartTS','EndTS'])


#%%
new_df = pd.DataFrame(columns=['available','iter'])
i=0
for index, row in df_flam_a_l_CTA.iterrows():
    temp_df = pd.DataFrame(columns=['available','iter'])
    temp_df.loc[pd.to_datetime(row['StartTS']),:]= [row['AvailableCapacity'], i]
    temp_df.loc[pd.to_datetime(row['EndTS']),:]= [row['AvailableCapacity'], i]
    temp_df.available = pd.to_numeric(temp_df.available)
    temp_df.iter = pd.to_numeric(temp_df.iter, downcast='integer')
    temp_df = temp_df.resample('h').interpolate()
    new_df = new_df.append(temp_df)
    i+=1
    
new_df = new_df.loc[~new_df.index.duplicated(keep='last')]
new_df = new_df.resample('h').fillna('backfill')
new_df.available.fillna(df_flam_a_l_CTA.InstalledCapacity.max(), inplace=True)

# %%
new_df.available.plot()
# %%
