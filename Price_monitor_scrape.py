#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 13:16:38 2022

@author: Sim
"""

## Set up --------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib
from matplotlib import pyplot as plt

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


## Scraping ------------------------------------------------------------------
# import the scraping functions
from Monitor_funcs import scrape_results_page

"""
The scraper Loops through rightmove results pages of 5 London areas extracting link, 
price and featured property status of each property


**What areas?**

5 relevant, non-overlapping areas defined by a 1 mile (or 0.5 mile) radius around the 
following tube stations:
- Kentish Town (1 mile)
- Royal Oak (1 mile)
- Finchley Road (1 mile)
- Angel (1 mile)
- Mornington Crescent (0.5 miles)


**What search criteria are used?**

I specify that properties must:
- have exactly 2 bedrooms and be a house/flat/apartment to ensure we compare like with like
- have been posted in last 7 days to ensure they don't appear in last week's scrape


**Why are there two scrapers?**

The first scraper loops through the 4 stations with 1mile radii. Due to the much lower 
number of properties in 0.5 miles around Mornington Crescent, results rarely go onto a 
second page. Therefore I simply created a specific scraping code for it.
"""

# call the scraping func
links = scrape_results_page()[1]
date_time = scrape_results_page()[2]
prices = scrape_results_page()[3]
featured = scrape_results_page()[4]


## Data wrangling ------------------------------------------------------------
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
full_df2 = pd.DataFrame.from_dict(data)

# Remove featured properties
full_df2 = full_df2[full_df2.Featured != 1]

# Sampling 120 rows
full_df2 = full_df2.sample(n = min(120,len(full_df2)))
latest_scrape_sample = len(full_df2)

# Adding time variables
full_df2['Date'] = pd.to_datetime(full_df2['DateScraped'])
full_df2['Year'] = full_df2['Date'].dt.strftime('%Y')
full_df2['Month'] = full_df2['Date'].dt.strftime('%m')
full_df2['MonthYear'] = full_df2['Date'].dt.strftime('%Y-%m')
full_df2['WeekNo'] = full_df2['Date'].dt.strftime('%U')
full_df2['Fortnight'] = (full_df2['WeekNo'].astype(int) +1)//2

full_df2['Date'] = full_df2.Date.dt.strftime("%Y-%m-%d")

# Combine this week's data with past weeks' full data
full_df2 = pd.concat([full_df, full_df2]).reset_index(drop=True)

# Save full scrape to csv
full_df2.to_csv(f'{location}/data/full_df_{today}.csv') 

#full_df2['Fortnight2'] = full_df2['Fortnight'].apply('str')
#m = full_df2['Fortnight2'].str.len().max()
#full_df2['Fortnight2'] = full_df2['Fortnight2'].str.rjust(m,'0')

#full_df2['Fortnight2'] = '0' + full_df2['Fortnight2'].astype(str)


## Summary stats -------------------------------------------------------------
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
date = datetime.strptime(str(full_df2.loc[len(full_df2)-1,'DateScraped']), "%Y-%m-%d").strftime("%d/%m/%Y")
avg_price, n = round(np.mean(full_df2['Price']),2), latest_scrape_sample
median_price, ten  = round(np.median(full_df2['Price']),2), round(np.percentile(full_df2['Price'], 10),2)
ninety, st_dev = round(np.percentile(full_df2['Price'], 90),2), round(np.std(full_df2['Price']),3)

# Combine and save new summary stats data
summary_df2.loc[len(summary_df2)] = [date, avg_price, median_price, ten, ninety, st_dev, n]
summary_df2 = pd.concat([summary_df, summary_df2]).reset_index(drop=True) # Combine this week's data with past weeks'
summary_df2.to_csv(f'{location}/data/summary_df_{today}.csv') # Save summary df to csv


## Creating charts -----------------------------------------------------------
# Plotting functions
def plot(interval = "Month", stat = "median", incl_CI90 = False, start = "2022-11-06", end = "2024-11-06", save_fig = False):
    full_df3 = full_df2[(full_df2['Date']>=start) & (full_df2['Date']<=end)]
    full_df3 = full_df3.groupby(f'{interval}').agg({'Price': ['mean', 'median', 'std', 'count']})
    full_df3 = full_df3.reset_index()
    
    full_df3['90_CI'] = 1.645*(full_df3['Price']['std']/full_df3['Price']['count']**0.5)

    fig, ax = plt.subplots()
    
    # plot points     
    if interval == "Date":
        full_df3[f'{interval}'] = pd.to_datetime(full_df3[f'{interval}'])
        ax.plot(full_df3[f'{interval}'].apply(lambda x: x.strftime('%d/%m')),full_df3['Price'][f'{stat}'], ".", color = 'b')

        # add error bars
        yerr = np.transpose(np.array(full_df3[['90_CI']]))
        if incl_CI90 == True: 
            ax.errorbar(full_df3[f'{interval}'].apply(lambda x: x.strftime('%d/%m')),full_df3['Price'][f'{stat}'], yerr=yerr, alpha = 0.5)

        # plot lines
        ax.plot(full_df3[f'{interval}'].apply(lambda x: x.strftime('%d/%m')),full_df3['Price'][f'{stat}'], color = 'b')

    else:
        ax.plot(full_df3[f'{interval}'].astype(str),full_df3['Price'][f'{stat}'], ".", color = 'b')
        
        # add error bars
        yerr = np.transpose(np.array(full_df3[['90_CI']]))
        if incl_CI90 == True: 
            ax.errorbar(full_df3[f'{interval}'].astype(str),full_df3['Price'][f'{stat}'], yerr=yerr, alpha = 0.5)

        # plot lines
        ax.plot(full_df3[f'{interval}'].astype(str),full_df3['Price'][f'{stat}'], color = 'b')
        

    # formatting
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: '£{:,}'.format(int(x), ',')))
    ax.yaxis.set_tick_params(which='major', labelcolor='black',labelleft=True)

    plt.ylabel(f'{stat} price')
    plt.xlabel(f'{interval}')
    plt.ylim([min(full_df3['Price'][f'{stat}'])- np.amax(yerr), max(full_df3['Price'][f'{stat}'])+np.amax(yerr)])
    
    if save_fig == True:
        plt.savefig(f'{location}/charts/{today}_{interval}_{stat}.png')

# Possible intervals: 'Date', 'Year', 'Month', 'MonthYear', 'WeekNo', 'Fortnight'
plot(interval = "Date", stat = "median", incl_CI90 = False, save_fig = True)

plot(interval = "Date", stat = "median", incl_CI90 = False, save_fig = False)


# Works: 'Date', Year, Month, WeekNo, MonthYear,
# Doesn't: 'Fortnight'


