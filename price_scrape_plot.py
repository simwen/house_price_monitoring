#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RightMove price scraping script: price_scrape_plot.py
(Created on Sun Nov 6 2022)

This script allows the user to monitor property market prices in specific locations
by scraping RightMove, storing the price data, then plotting the prices.


This script requires that `pandas`, `numpy`, `matplotlib`, `requests` and `bs4` 
to be installed within the Python environment you are running this script in.

This script uses the following functions:

    * scrape_results_page (from monitor_funcs.py): Returns the links, dates, prices, 
    and featured status of scraped Rightmove properties based on user inputs.
    * plot: Returns a property price plot using the scraped data based on the user-defined 
    inputs.

"""

## 1. Set up ------------------------------------------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import lines
import math
from pathlib import Path
from monitor_funcs import scrape_results_page # scraping function

# file naming variables
today = date.today()
last_version = today - timedelta(days=7)

# Load last week's data (full data and summary stats)
try:
    summary_df = pd.read_csv(Path("./data", f"summary_df_{last_version}.csv"))
    full_df = pd.read_csv(Path("./data", f"full_df_{last_version}.csv"))
except FileNotFoundError:
    raise FileNotFoundError(f"The csv files full_df_{last_version} and summary_df_{last_version} don't exist. Either you have incorrectly specified last_version or there is no data yet (perhaps this is the first run?). If the latter, create blank dataframes to be populated.")


## 2. Scraping ----------------------------------------------------------------
"""
The scraper is currently set to the following default settings:
Scraping 2 bed properties posted in the last 7 days (to ensure they don't appear 
in last week's scrape) in the user-defined areas.

See function scrape_results_page in monitor_funcs.py fpr more info on the scraper 
and to change the default settings.
"""

# call the scraping func
_, links, date_time, prices, featured = scrape_results_page()

## 3. Data wrangling ----------------------------------------------------------
# create date_time vars for the df
date_time = pd.to_datetime(date_time, dayfirst=True, format="%d/%m/%Y %H:%M")
dates = date_time.date

# convert to dataframe
data = {
    "Links": links,
    "DateTimeScraped": date_time,
    "DateScraped": dates,
    "Price": prices,
    "Featured": featured,
}

full_df_new = pd.DataFrame.from_dict(data)

# Remove featured properties
full_df_new = full_df_new[full_df_new.Featured != 1]
#print(len(full_df_new))

# Sampling 120 rows
full_df_new = full_df_new.sample(n=min(120, len(full_df_new)))
latest_scrape_sample = len(full_df_new)

# Adding time variables
full_df_new["Date"] = pd.to_datetime(full_df_new["DateScraped"])
full_df_new["Year"] = full_df_new["Date"].dt.strftime("%Y")
full_df_new["MonthYear"] = full_df_new["Date"].dt.strftime("%Y-%m")
full_df_new["WeekNo"] = full_df_new["Date"].dt.strftime("%U")
full_df_new["Fortnight"] = (full_df_new["WeekNo"].astype(int) + 1) // 2

full_df_new["Date"] = full_df_new.Date.dt.strftime("%Y-%m-%d")

# Combine this week's data with past weeks' full data
full_df = pd.concat([full_df, full_df_new]).reset_index(drop=True)

# Save full scrape to csv
full_df.to_csv(Path("./data", f"full_df_{today}.csv"), index=False)

## 4. Summary stats -----------------------------------------------------------
# For summary stats df, first create empty dataframe for new data
summary_df2 = pd.DataFrame(
    {"Date": [],
    "Average Price": [],
    "Median Price": [],
    "10th Percentile": [],
    "90th Percentile": [],
    "Std dev": [],
    "Sample Size": []}
    )

# Summary stats: Next get the new summary stats from scrape
date = datetime.strptime(
    str(full_df_new.iloc[len(full_df_new) - 1, 2]), "%Y-%m-%d"
    ).strftime("%d/%m/%Y")  # extracts date (col no. 2) from last row of new df
    
avg_price, n = round(np.mean(full_df_new["Price"]), 2), latest_scrape_sample
median_price, ten = round(np.median(full_df_new["Price"]), 2), round(np.percentile(full_df_new["Price"], 10), 2)
ninety, st_dev = round(np.percentile(full_df_new["Price"], 90), 2), round(np.std(full_df_new["Price"]), 3)

# Combine and save new summary stats data
summary_df2.loc[len(summary_df2)] = [
    date,
    avg_price,
    median_price,
    ten,
    ninety,
    st_dev,
    n,
]

# Combine this week's data with past weeks'
summary_df2 = pd.concat([summary_df, summary_df2]).reset_index(drop=True)  
# Save summary df to csv
summary_df2.to_csv(Path("./data", f"summary_df_{today}.csv"), index=False)

## 5. Creating charts ---------------------------------------------------------
# Plotting function
def plot(interval="Date", stat="median", incl_trend=True, incl_CI90=False,
         start="2022-11-06", end="2024-11-06", save_fig=False):
    """
    Returns a property price plot using the scraped data based on the user-defined 
    inputs.

        Parameters:
            interval (str): The time interval to use when plotting (e.g. Date, MonthYear etc.)
            stat (str): The price stat to plot (e.g. mean, median)
            incl_trend (bool): Whether to include a quadratic trend line
            incl_CI90 (bool): Whether to include 90% confidence interval bars on each point
            start (str): The starting date to consider
            end (str): The final date to consider
            save_fig (bool): Whether to locally save the plot
                    
        Returns:
            Matplotlib plot of the user's desired plot
    """
    
    full_df3 = full_df[(full_df["Date"] >= start) & (full_df["Date"] <= end)]
    full_df3 = full_df3.groupby(f"{interval}").agg({"Price": ["mean", "median", "std", "count"]})
    full_df3 = full_df3.reset_index()

    full_df3["90_CI"] = 1.645 * (full_df3["Price"]["std"] / full_df3["Price"]["count"] ** 0.5)
    
    fig, ax = plt.subplots()

    # plot points
    if interval == "Date":
        
        # plot points
        full_df3[f"{interval}"] = pd.to_datetime(full_df3[f"{interval}"])
        ax.plot(
            full_df3[f"{interval}"].apply(lambda x: x.strftime("%d/%m")),
            full_df3["Price"][f"{stat}"],
            ".",
            color="red",
            alpha=0.25,
        )
        ax.set_xticks(ax.get_xticks()[:: math.ceil(len(full_df3) / 10)])

        # add error bars
        yerr = np.transpose(np.array(full_df3[["90_CI"]]))
        if incl_CI90:
            ax.errorbar(
                full_df3[f"{interval}"].apply(lambda x: x.strftime("%d/%m")),
                full_df3["Price"][f"{stat}"],
                yerr=yerr,
                alpha=0.5,
            )

        # plot lines
        if not incl_trend:
            ax.plot(
                full_df3[f"{interval}"].apply(lambda x: x.strftime("%d/%m")),
                full_df3["Price"][f"{stat}"],
                color="red",
            )

    else:
        
        # plot points
        ax.plot(
            full_df3[f"{interval}"].astype(str),
            full_df3["Price"][f"{stat}"],
            ".",
            color="red",
            alpha=0.5
        )

        # add error bars
        yerr = np.transpose(np.array(full_df3[["90_CI"]]))
        if incl_CI90:
            ax.errorbar(
                full_df3[f"{interval}"].astype(str),
                full_df3["Price"][f"{stat}"],
                yerr=yerr,
                alpha=0.5,
            )

        # plot lines 
        if not incl_trend:
            ax.plot(
                full_df3[f"{interval}"].astype(str),
                full_df3["Price"][f"{stat}"],
                color="red",
            )

    # trend line
    if incl_trend:
        xaxis = list(range(len(full_df3)))
        yaxis = list(full_df3["Price"][f"{stat}"])
        model = np.poly1d(np.polyfit(xaxis, yaxis, 3))
        polyline = np.linspace(0, len(full_df3) - 1, 100)
        ax.plot(polyline, model(polyline), color = "red")

    # formatting
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: "£{}k".format(str(int(x))[:-3]) ))  
    
    ax.yaxis.set_tick_params(which="major", labelcolor="black", labelleft=True)
    ax.yaxis.set_ticks_position('none') 
    
    plt.ylabel(f"{stat} Price".capitalize(), size = 12)
    plt.xlabel(f"{interval}", size = 12)
    plt.grid(axis = "y", color = 'grey', alpha = 0.6)
    plt.box(False)
    plt.rcParams["font.family"] = "Arial"

    xmin, xmax = ax.get_xaxis().get_view_interval()   
    if interval == "Date":
        ymin = min(full_df3["Price"][f"{stat}"]) - np.amax(yerr) + 60000
        ymax = max(full_df3["Price"][f"{stat}"]) + np.amax(yerr) - 60000
        plt.ylim([ymin, ymax])
    else:
        ymin = min(full_df3["Price"][f"{stat}"]) - np.amax(yerr)
        ymax = max(full_df3["Price"][f"{stat}"]) + np.amax(yerr)
        plt.ylim([ymin,ymax])
    
    ax.add_artist(lines.Line2D((xmin, xmax), (ymin+1000, ymin+1000), color='grey', linewidth=1))

    if save_fig:
        plt.savefig(Path("./charts", f"{interval}", f"{today}_{stat}_trend_{incl_trend}.png"))


# Plot the data
# Possible intervals: 'Date', 'Year', 'MonthYear', 'Fortnight' (doesn't work)

plot(interval="Date", stat="median", incl_trend=True, incl_CI90=False, save_fig=False)

plot(interval="Date", stat="median", incl_trend=True, incl_CI90=False, save_fig=True)
plot(interval="MonthYear", stat="median", incl_trend=False, incl_CI90=False, save_fig=True)

# Works: Date, Year, MonthYear
# Not working: Fortnight
plot(interval="WeekNo", stat="median", incl_trend=False, incl_CI90=False, save_fig=False)



