#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 13:26:07 2022

@author: Sim
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# Scraping the rightmove search results webpages 
# Collates valid properties' weblinks, price and id

# Input here the area/station codes you're interested in, and the radius of the search in the form {area: radius}
# Area and station codes can be found in the weblink of a rightmove property search
areas = {'STATION%5E7832': 1,'STATION%5E3509': 1, 'STATION%5E9338': 1, 'STATION%5E245': 1, 'STATION%5E6380': 0.5}

def scrape_results_page(min_beds=2,max_beds=2,noPages=2,days_since_added=7):
    all_apartment_links = [] # stores apartment links
    all_price = [] # stores the listing price of apartment
    all_featured = [] # stores 'featured' status of properties
    all_datetime = [] # stores date of scrape
        
    for area_key in areas:
        print(f'scraping {area_key}')
        for i in range(noPages):
            if i==0:
                r= requests.get(f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={area_key}&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius={areas[area_key]}&sortType=6&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=')
            elif i>0 and areas[area_key] <1:  
                break    # usually 0.5 radius searches have only 1 page of properties
            else:
                r = ''
                while r == '':
                    try:
                        r = requests.get(f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={area_key}&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius={areas[area_key]}&sortType=6&index={i*24}&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=')
                        break
                    except:
                        print(f'Connection refused by the server on page {i+1}... sleeping for 3 seconds')
                        time.sleep(3)
                        print("My sleep was lovely, now let me continue...")
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
    
    return r.ok, all_apartment_links, all_datetime, all_price, all_featured



