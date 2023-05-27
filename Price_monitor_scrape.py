#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 13:16:38 2022

@author: Sim
"""

## 1. Set up ------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib
from matplotlib import pyplot as plt
import math

# file naming variables
today = date.today()
last_version = today - timedelta(days=7)
location = '/Users/Sim/Documents/Other/Programming/Personal Projects/house_price_monitoring'
#location2 = '/Users/Sim/Documents/Other/Programming/Personal Projects/house_price_monitoring/test'

# Load last week's data (full data and summary stats)
summary_df = pd.read_csv(f'{location}/data/summary_df_{last_version}.csv')
full_df = pd.read_csv(f'{location}/data/full_df_{last_version}.csv')

summary_df = summary_df.drop('Unnamed: 0', axis=1)
full_df = full_df.drop('Unnamed: 0', axis=1)


## 2. Scraping ----------------------------------------------------------------
# import the scraping functions
import sys 
import os
sys.path.append(os.path.abspath('/Users/Sim/Documents/Other/Programming/Personal Projects/house_price_monitoring'))

from Monitor_funcs import scrape_results_page

"""
The scraper is currently set to the following default settings:
Scraping 2 bed properties posted in the last 7 days (to ensure they don't appear 
in last week's scrape) in the 5 following non-overlapping areas defined by a 
1 mile (or 0.5 mile) radius around the following tube stations:
- Kentish Town (1 mile)
- Royal Oak (1 mile)
- Finchley Road (1 mile)
- Angel (1 mile)
- Mornington Crescent (0.5 miles)

See Monitor_funcs.py to change these default settings.
"""

# call the scraping func
links = scrape_results_page()[1]
date_time = scrape_results_page()[2]
prices = scrape_results_page()[3]
featured = scrape_results_page()[4]


## 3. Data wrangling ----------------------------------------------------------
# create date_time vars for the df
date_time = pd.to_datetime(date_time,dayfirst = True, format = "%d/%m/%Y %H:%M")
dates = date_time.date

# convert to dataframe
data = {"Links": links,
        "DateTimeScraped": date_time,
        "DateScraped": dates,
        "Price": prices,
        "Featured": featured,
       }
full_df_new = pd.DataFrame.from_dict(data)

# Remove featured properties
full_df_new = full_df_new[full_df_new.Featured != 1]

# Sampling 120 rows
full_df_new = full_df_new.sample(n = min(120,len(full_df_new)))
latest_scrape_sample = len(full_df_new)

# Adding time variables
full_df_new['Date'] = pd.to_datetime(full_df_new['DateScraped'])
full_df_new['Year'] = full_df_new['Date'].dt.strftime('%Y')
full_df_new['Month'] = full_df_new['Date'].dt.strftime('%m')
full_df_new['MonthYear'] = full_df_new['Date'].dt.strftime('%Y-%m')
full_df_new['WeekNo'] = full_df_new['Date'].dt.strftime('%U')
full_df_new['Fortnight'] = (full_df_new['WeekNo'].astype(int) +1)//2

full_df_new['Date'] = full_df_new.Date.dt.strftime("%Y-%m-%d")

# Combine this week's data with past weeks' full data
full_df = pd.concat([full_df, full_df_new]).reset_index(drop=True)

# Save full scrape to csv
full_df.to_csv(f'{location}/data/full_df_{today}.csv') 

## 4. Summary stats -----------------------------------------------------------
# For summary stats df, first create empty dataframe for new data
summary_df2 = pd.DataFrame(
    {"Date": [],
     "Average Price": [],
     "Median Price": [],
     "10th Percentile": [],
     "90th Percentile": [],
     "Std dev": [],
     "Sample Size": []
    })

# Summary stats: Next get the new summary stats from scrape
date = datetime.strptime(str(full_df_new.iloc[len(full_df_new)-1,2]), "%Y-%m-%d").strftime("%d/%m/%Y")  # extracts date (col no. 2) from last row of new df
avg_price, n = round(np.mean(full_df_new['Price']),2), latest_scrape_sample
median_price, ten  = round(np.median(full_df_new['Price']),2), round(np.percentile(full_df_new['Price'], 10),2)
ninety, st_dev = round(np.percentile(full_df_new['Price'], 90),2), round(np.std(full_df_new['Price']),3)

# Combine and save new summary stats data
summary_df2.loc[len(summary_df2)] = [date, avg_price, median_price, ten, ninety, st_dev, n]
summary_df2 = pd.concat([summary_df, summary_df2]).reset_index(drop=True) # Combine this week's data with past weeks'
summary_df2.to_csv(f'{location}/data/summary_df_{today}.csv') # Save summary df to csv


## 5. Creating charts ---------------------------------------------------------
# Plotting function
def plot(interval = "Month", stat = "median", incl_trend = True, incl_CI90 = False, start = "2022-11-06", end = "2024-11-06", save_fig = False):
    full_df3 = full_df[(full_df['Date']>=start) & (full_df['Date']<=end)]
    full_df3 = full_df3.groupby(f'{interval}').agg({'Price': ['mean', 'median', 'std', 'count']})
    full_df3 = full_df3.reset_index()
    
    full_df3['90_CI'] = 1.645*(full_df3['Price']['std']/full_df3['Price']['count']**0.5)

    fig, ax = plt.subplots()
    
    # plot points     
    if interval == "Date":
        full_df3[f'{interval}'] = pd.to_datetime(full_df3[f'{interval}'])
        ax.plot(full_df3[f'{interval}'].apply(lambda x: x.strftime('%d/%m')),full_df3['Price'][f'{stat}'], ".", color = 'b')
        ax.set_xticks(ax.get_xticks()[::math.ceil(len(full_df3)/10)])

        # add error bars
        yerr = np.transpose(np.array(full_df3[['90_CI']]))
        if incl_CI90 == True: 
            ax.errorbar(full_df3[f'{interval}'].apply(lambda x: x.strftime('%d/%m')),full_df3['Price'][f'{stat}'], yerr=yerr, alpha = 0.5)

        # plot lines
        if incl_trend == False:
            ax.plot(full_df3[f'{interval}'].apply(lambda x: x.strftime('%d/%m')),full_df3['Price'][f'{stat}'], color = 'b')
    
    else:
        ax.plot(full_df3[f'{interval}'].astype(str),full_df3['Price'][f'{stat}'], ".", color = 'b')
        
        # add error bars
        yerr = np.transpose(np.array(full_df3[['90_CI']]))
        if incl_CI90 == True: 
            ax.errorbar(full_df3[f'{interval}'].astype(str),full_df3['Price'][f'{stat}'], yerr=yerr, alpha = 0.5)

        # plot lines
        if incl_trend == False:
            ax.plot(full_df3[f'{interval}'].astype(str),full_df3['Price'][f'{stat}'], color = 'b')
        
    # trend line
    if incl_trend == True:
        xaxis = list(range(len(full_df3)))
        yaxis = list(full_df3['Price'][f'{stat}'])
        model = np.poly1d(np.polyfit(xaxis, yaxis, 3))
        polyline = np.linspace(0, len(full_df3)-1, 100)
        ax.plot(polyline, model(polyline))

    # formatting
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: '£{:,}'.format(int(x), ',')))
    ax.yaxis.set_tick_params(which='major', labelcolor='black',labelleft=True)

    plt.ylabel(f'{stat} price')
    plt.xlabel(f'{interval}')
    plt.ylim([min(full_df3['Price'][f'{stat}'])- np.amax(yerr)+50000, max(full_df3['Price'][f'{stat}'])+np.amax(yerr)-50000])
    
    if save_fig == True:
        plt.savefig(f'{location}/charts/{interval}/{today}_{interval}_{stat}_trend_{incl_trend}.png')

# Plot the data
# Possible intervals: 'Date', 'Year', 'Month', 'MonthYear', 'WeekNo', 'Fortnight'
plot(interval = "Date", stat = "median", incl_trend=True, incl_CI90 = False, save_fig = True)

plot(interval = "MonthYear", stat = "median", incl_trend=False, incl_CI90 = False, save_fig = True)

plot(interval = "Date", stat = "mean", incl_CI90 = False, save_fig = False)


# Works: Date, Year, MonthYear
# Doesn't: Fortnight, Month, WeekNo


