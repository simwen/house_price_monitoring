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

# Input here the area/station codes you're interested in, and the radius of the search in the form {area: radius}
# Area and station codes can be found in the weblink of a rightmove property search
areas = {
    "STATION%5E7832": 1,
    "STATION%5E3509": 1,
    "STATION%5E9338": 1,
    "STATION%5E245": 1,
    "STATION%5E6380": 0.5,
}


def scrape_results_page(min_beds=2, max_beds=2, noPages=2, days_since_added=7):
    """
    Returns the links, dates, prices, and featured status of scraped Rightmove 
    properties based on user inputs.

        Parameters:
            min_beds (int): The min number of beds to consider (excludes properties with less)
            max_beds (int): The max number of beds to consider (excludes properties with more)
            noPages (int): The number of Rightmove pages to scrape per area (usually 25 properties per page)
            days_since_added (int): The maximum number of days since listing to consider (excludes properties from longer ago)
                    
        Returns:
            apartment_links (str): weblink to property
            datetime_listing (str): date of scraping (today's date)
            prices (int): listing price of property
            featured_listing: whether the property appears as a 'featured property' on RightMove
    """
    
    apartment_links = []  
    prices = []  
    featured_listing = []  
    datetime_listing = []  

    for area_key in areas:
        print(f"scraping {area_key}")
        for i in range(noPages):
            if i == 0:
                url1 = ("https://www.rightmove.co.uk/property-for-sale/find.html?"
                        f"locationIdentifier={area_key}&maxBedrooms={max_beds}&minBedrooms={min_beds}"
                        f"&radius={areas[area_key]}&sortType=6&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced"
                        f"&maxDaysSinceAdded={days_since_added}&includeSSTC=false"
                        f"&mustHave=&dontShow=&furnishTypes=&keywords="
                        )
                r = requests.get(
                    url1
                    #f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={area_key}&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius={areas[area_key]}&sortType=6&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="
                )
            elif i > 0 and areas[area_key] < 1:
                break  # usually 0.5 radius searches have only 1 page of properties
            else:
                r = ""
                max_retry = 8
                for retry in range(max_retry): # loop 8 times: break out loop if trying normal requests.get works, if error from too many requests then induce 8 increasingly lengthy sleeps until goes through, or fails
                    try:
                        url2 = ("https://www.rightmove.co.uk/property-for-sale/find.html?"
                                f"locationIdentifier={area_key}&maxBedrooms={max_beds}&minBedrooms={min_beds}"
                                f"&radius={areas[area_key]}&sortType=6&index={i*24}"
                                f"&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}"
                                "&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=")
                        r = requests.get(
                            url2
                            #f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={area_key}&maxBedrooms={max_beds}&minBedrooms={min_beds}&radius={areas[area_key]}&sortType=6&index={i*24}&propertyTypes=detached%2Cflat%2Csemi-detached%2Cterraced&maxDaysSinceAdded={days_since_added}&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="
                        )
                        break
                    except requests.exceptions.ConnectionError:
                        sleep_length = (retry+1)*2
                        print(f"Too many requests meaning connection refused by server on page {i+1}... sleeping for {sleep_length} seconds")
                        time.sleep(sleep_length)
                        print("Sleep {retry} over, scrape restarting...")
                        continue

            soup = BeautifulSoup(r.text, "lxml")
            apartments = soup.find_all("div", class_="l-searchResult is-list")

            for apartment in apartments:

                # append link
                apartment_info = apartment.find("a", class_="propertyCard-link")
                link = "https://www.rightmove.co.uk" + apartment_info.attrs["href"]
                apartment_links.append(link)

                # append price
                price = (
                    apartment.find("div", class_="propertyCard-priceValue")
                    .get_text()
                    .strip()
                )
                
                prices.append(int(price.replace(",", "").replace("£", "")))

                # append featured listing indicator
                try:
                    featured = apartment.find(
                    "div", class_="propertyCard-moreInfoFeaturedTitle"
                    ).get_text()
                except AttributeError:
                    print("No featured info - assumed not featured")
                    featured = ""
                if len(featured) > 0:
                    featured = 1
                else:
                    featured = 0
                featured_listing.append(featured)

                # append date
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M")
                datetime_listing.append(dt_string)

    return r.ok, apartment_links, datetime_listing, prices, featured_listing
