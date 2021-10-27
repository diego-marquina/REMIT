# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 17:01:00 2021

@author: Diego.Marquina
"""
#%%
import pandas as pd
import glob
from datetime import date

from energyquantified import EnergyQuantified, time

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
mapcode='FR' # 'PT', 'ES', 'FR', 'FI', 'SE3', 'SE', 'EE', 'SE1', 'NO2', 'NL', 'NO', 'HU', 'NO4', 'CZ', 'GB', 'PL', 'NO5', 'RO', 'DE_50HzT', 'DE_Amprion', 'DE_AT_LU', 'CH', 'DE_TransnetBW', 'AT', 'DE_TenneT_GER', 'IT-CNORTH', 'BE', 'IT-NORTH', 'DK2', 'IE', 'NO3', 'IT-CSOUTH', 'DK', 'DK1', 'IE_SEM', 'GR', 'IT-Sicily', 'LV', 'NO1', 'IT-Sardinia', 'SE4', 'NIE', 'LT', 'SE2', 'SK', 'IT-Priolo', 'BG', 'IT', 'IT-Rossano', 'IT-Brindisi', 'IT-Foggia', 'RS', 'IT-SOUTH', 'MK', 'ME', 'SI', 'AL', 'DE_LU', 'IT-Calabria', 'XK'
unitname='PALUEL 2'
areatype = ['CTA','BZN'] #options are CTA or BZN


df_fr = frame.loc[frame.MapCode==mapcode,:].copy()
df_unit = df_fr.loc[df_fr.UnitName.str.contains(unitname),:]
df_unit_active = df_unit.loc[df_unit.Status=='Active',:]
df_unit_active_latest = df_unit_active.loc[df_unit_active.groupby('MRID')['Version'].idxmax(),:]
df_unit_a_l_CTA = df_unit_active_latest.loc[df_unit_active_latest.AreaTypeCode.isin(areatype),:]
df_unit_a_l_CTA.loc[:,['StartTS','EndTS','UpdateTime']] = df_unit_a_l_CTA.loc[:,['StartTS','EndTS','UpdateTime']].apply(pd.to_datetime).copy()
df_unit_a_l_CTA.loc[:,['StartTS','EndTS','UpdateTime']] = df_unit_a_l_CTA.apply(lambda x: x[['StartTS','EndTS','UpdateTime']].apply(lambda y: y.tz_localize(x['TimeZone']).tz_convert('UTC')), axis=1)
df_unit_a_l_CTA = df_unit_a_l_CTA.sort_values(['StartTS','EndTS'])
df_unit_a_l_CTA = df_unit_a_l_CTA.loc[df_unit_a_l_CTA.EndTS < '2030-01-01']

#%%
df_ts = pd.DataFrame(columns=['available','iter'])
i=0
for index, row in df_unit_a_l_CTA.iterrows():
    temp_df = pd.DataFrame(columns=['available','iter'])
    temp_df.loc[pd.to_datetime(row['StartTS']),:]= [row['AvailableCapacity'], i]
    temp_df.loc[pd.to_datetime(row['EndTS']),:]= [row['AvailableCapacity'], i]
    temp_df.available = pd.to_numeric(temp_df.available)
    temp_df.iter = pd.to_numeric(temp_df.iter, downcast='integer')
    temp_df = temp_df.resample('1T').interpolate()
    df_ts = df_ts.append(temp_df)
    i+=1
    
df_ts = df_ts.loc[~df_ts.index.duplicated(keep='last')]
df_ts = df_ts.resample('1T').mean()
df_ts.available.fillna(df_unit_a_l_CTA.InstalledCapacity.max(), inplace=True)
df_ts = df_ts.resample('h').mean()

# %%
# Initialize client
eq = EnergyQuantified(api_key='0168d6-b068b6-f41124-7108d3')

# Free-text search (filtering on attributes is also supported)
curves = eq.metadata.curves(q='FR @Paluel-2 Nuclear Capacity Available MW REMIT')

# Load time series data
curve = curves[0]

periodseries = eq.period_instances.latest(
    curve,
    begin=date(2015,1,1),
    end=date(2023,1,2)
)

# timeseries = eq.timeseries.load(
#     curve,
#     begin=date(2022,1,1),
#     end=date(2023,1,2)
# )

# capacity_eq = eq.periods.load(
#     capacity_curves[0],
#     begin=date(2021,1,1),
#     end=date(2022,1,2)
# )
#%%

# Convert to Pandas data frame
df_eq = periodseries.to_timeseries(time.Frequency.PT1H).to_dataframe()
df_eq.columns=df_eq.columns.get_level_values(0)
df_eq.index = df_eq.index.tz_convert('UTC')


#%% plot
pd.concat([df_ts.available, df_eq], axis=1).plot()
# df_eq.plot()

# %%
