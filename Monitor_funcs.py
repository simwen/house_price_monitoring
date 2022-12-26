#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 13:26:07 2022

@author: Sim
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np
import re
import json
from datetime import datetime, timedelta

# Scraping the rightmove property search results webpages 
# Collates valid properties' weblinks, plus their price and id

def scrape_results_page(min_beds=2,max_beds=2,radius=1,noPages=2,days_since_added=7):
    all_apartment_links = [] # stores apartment links
    all_price = [] # stores the listing price of apartment
    all_featured = []
    all_datetime = []
    stations = ['STATION%5E7832','STATION%5E3509', 'STATION%5E9338', 'STATION%5E245']
    
    ## Main scraper for 1 mile radius stations
    
    for station in stations:
        for i in range(noPages):
            if i==0:
                r= requests.get(f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={station}&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius={radius}&sortType=6&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=')
            else:
                r = ''
                while r == '':
                    try:
                        r = requests.get(f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={station}&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius={radius}&sortType=6&index={i*24}&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=')
                        break
                    except:
                        print(f'Connection refused by the server on page {i+1}... sleeping for 3 seconds')
                        time.sleep(3)
                        print("Was a nice sleep, now let me continue...")
                        continue

            soup = BeautifulSoup(r.text, 'lxml')
            apartments = soup.find_all("div", class_="l-searchResult is-list")
            
            for j in range(len(apartments)):

                # tracks which apartment we are on in the page
                apartment_no = apartments[j]

                # append link
                apartment_info = apartment_no.find("a", class_="propertyCard-link")
                link = "https://www.rightmove.co.uk" + apartment_info.attrs["href"]
                all_apartment_links.append(link)

                # append price
                price = (
                    apartment_no.find("div", class_="propertyCard-priceValue")
                    .get_text()
                    .strip()
                )
                all_price.append(int(price.replace(",","").replace("£","")))

                # append featured listing indicator
                featured = (
                    apartment_no.find("div", class_="propertyCard-moreInfoFeaturedTitle")
                    .get_text()
                )
                if len(featured) > 0:
                    featured = 1
                else:
                    featured = 0
                all_featured.append(featured)
                
                # append date
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
                all_datetime.append(dt_string)
 
    
    ## Secondary scraper for 0.5 mile radius station

    r= requests.get(f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=STATION%5E6380&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius=0.5&sortType=6&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=')
    soup = BeautifulSoup(r.text, 'lxml')

    apartments = soup.find_all("div", class_="l-searchResult is-list")

    for j in range(len(apartments)):

        # tracks which apartment we are on in the page
        apartment_no = apartments[j]

        # append link
        apartment_info = apartment_no.find("a", class_="propertyCard-link")
        link = "https://www.rightmove.co.uk" + apartment_info.attrs["href"]
        all_apartment_links.append(link)

        # append price
        price = (
            apartment_no.find("div", class_="propertyCard-priceValue")
            .get_text()
            .strip()
        )
        all_price.append(int(price.replace(",","").replace("£","")))
        
        # append featured listing indicator
        featured = (
            apartment_no.find("div", class_="propertyCard-moreInfoFeaturedTitle")
            .get_text()
        )
        if len(featured) > 0:
            featured = 1
        else:
            featured = 0
        all_featured.append(featured)
        
        # append date
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
        all_datetime.append(dt_string)
    
    #remove_indices = [0,25]
    #all_apartment_links = [i for j, i in enumerate(all_apartment_links) if j not in remove_indices]
    #all_price = [i for j, i in enumerate(all_price) if j not in remove_indices]
    #all_id_no = [i for j, i in enumerate(all_id_no) if j not in remove_indices]
    
    return r.ok, all_apartment_links, all_datetime, all_price, all_featured