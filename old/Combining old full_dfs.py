#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 14:05:30 2022

@author: Sim
"""

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import ticker

# file naming variables
today = date.today()
last_version = today - timedelta(days=7)
location3 = '/Users/Sim/Documents/Other/Programming/Personal Projects/house_price_monitoring'

# Load last week's data
full_df1 = pd.read_csv(f'{location}/data/full_df_2022-11-06.csv')
full_df2 = pd.read_csv(f'{location}/data/full_df_2022-11-13.csv')
full_df3 = pd.read_csv(f'{location}/data/full_df_2022-11-20.csv')
full_df4 = pd.read_csv(f'{location}/data/full_df_2022-11-27.csv')
full_df5 = pd.read_csv(f'{location}/data/full_df_2022-12-04.csv')
full_df6 = pd.read_csv(f'{location}/data/full_df_2022-12-11.csv')
full_df7 = pd.read_csv(f'{location}/data/full_df_2022-12-18.csv')

full_df1 = full_df1.drop('Unnamed: 0', axis=1)
full_df2 = full_df2.drop('Unnamed: 0', axis=1)
full_df3 = full_df3.drop('Unnamed: 0', axis=1)
full_df4 = full_df4.drop('Unnamed: 0', axis=1)
full_df5 = full_df5.drop('Unnamed: 0', axis=1)
full_df6 = full_df6.drop('Unnamed: 0', axis=1)
full_df7 = full_df7.drop('Unnamed: 0', axis=1)

# Combine this week's data with past weeks' full data
full_df8 = pd.concat([full_df1, full_df2]).reset_index(drop=True)
full_df8 = pd.concat([full_df8, full_df3]).reset_index(drop=True)
full_df8 = pd.concat([full_df8, full_df4]).reset_index(drop=True)
full_df8 = pd.concat([full_df8, full_df5]).reset_index(drop=True)
full_df8 = pd.concat([full_df8, full_df6]).reset_index(drop=True)
full_df8 = pd.concat([full_df8, full_df7]).reset_index(drop=True)

full_df8['DateScraped']
full_df8.to_csv(f'{location}/data/full_df_lol.csv') 

# Adding new cols
full_df_new = pd.read_csv(f'{location3}/data/full_df_2022-12-18_oldv2.csv')
full_df_new = full_df_new.drop('Unnamed: 0', axis=1)

full_df_new['Date'] = pd.to_datetime(full_df_new['DateScraped'])
full_df_new['Year'] = full_df_new['Date'].dt.strftime('%Y')
full_df_new['Month'] = full_df_new['Date'].dt.strftime('%m')
full_df_new['MonthYear'] = full_df_new['Date'].dt.strftime('%Y-%m')
full_df_new['WeekNo'] = full_df_new['Date'].dt.strftime('%U')
full_df_new['Fortnight'] = full_df_new['WeekNo'].astype(int)//2

# Save full scrape to csv
full_df_new.to_csv(f'{location3}/data/full_df_lol.csv') 