#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 13:16:38 2022

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
location = '/Users/Sim/Documents/Other/Programming/Personal Projects/Property Price Monitor'

# Load last week's data
df = pd.read_csv(f'{location}/data/df_{last_version}.csv')
df = df.drop('Unnamed: 0', axis=1)

# create empty dataframe for new data
df2 = pd.DataFrame(
    {"Date": [],
     "Average Price": [],
     "Median Price": [],
     "10th Percentile": [],
     "90th Percentile": [],
     "Std dev": [],
     "Sample Size": []
    })

# import the scraping functions
from Monitor_funcs import scrape_results_page

### Scraper
"""
The scraper Loops through rightmove results pages of 5 London areas extracting link, 
price and featured property status of each property


**What areas?**

5 relevant, non-overlapping areas defined by a 1 mile (or 0.5 mile) radius around the 
following tube stations (also see screenshot below):
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
second page meaning. Therefore I simply created a specific scraping code for it.
"""

# call the scraping func
links = scrape_results_page()[1]
date_time = scrape_results_page()[2]
prices = scrape_results_page()[3]
featured = scrape_results_page()[4]

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
df3 = pd.DataFrame.from_dict(data)

# Remove featured properties
df3 = df3[df3.Featured != 1]

# Sampling 120 rows
df3=df3.sample(n = min(120,len(df3)))

# Save full scrape to csv
df3.to_csv(f'{location}/data/full_df_{today}.csv') 

# Key scrape info
date = datetime.strptime(str(df3.loc[2,'DateScraped']), "%Y-%m-%d").strftime("%d/%m/%Y")
avg_price, n = round(np.mean(df3['Price']),2), len(df3)
median_price, ten  = round(np.median(df3['Price']),2), round(np.percentile(df3['Price'], 10),2)
ninety, st_dev = round(np.percentile(df3['Price'], 90),2), round(np.std(df3['Price']),3)

# Key info df
df2.loc[len(df2)] = [date, avg_price, median_price, ten, ninety, st_dev, n]

# Combine this week's data with past weeks'
df2 = pd.concat([df, df2]).reset_index(drop=True)

# Save aggregate data to csv
df2.to_csv(f'{location}/data/df_{today}.csv')

# Plotting chart
fig, ax = plt.subplots()
ax.plot(df2['Date'],df2['Median Price'])

# Using automatic StrMethodFormatter
ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: '£{:,}'.format(int(x), ',')))
ax.yaxis.set_tick_params(which='major', labelcolor='black',labelleft=True)
ax.plot(df2['Date'],df2['Median Price'], ".", color = 'b')

# Formatting axis
plt.ylabel('Median Price')
plt.xlabel('Date')
plt.ylim([min(df2['Median Price'])-40000, max(df2['Median Price'])+40000])

# Save to .png
plt.savefig(f'{location}/charts/{today}_medians.png')
#plt.show()