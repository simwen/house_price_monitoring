# house_price_monitoring

## Summary
This project involves building a tool to monitor local property prices on UK property portal RightMove (https://www.rightmove.co.uk). The tool monitors prices on a weekly basis by scraping the RightMove website and then building charts to visualise trends/movements. One can calibrate the tool to monitor prices in any area of the UK, with the current default set up monitoring North Central London.

## Motivation
Media reporting on house prices and the state of the property market suffers from 2 problems:
- **Timing:** House price changes are often reported annually, quarterly, or monthly. This means they can be outdated by the time house prices reach the national press.
- **Non-Specificity/Heterogeneity:** Reporting on property market is usually at national or regional level and for all property types. However, the housing market can be far more heterogenoeous with different areas within regions or different property types seeing much smaller or larger price changes.
This tool aims to solve both these issues by allowing users to monitor house price changes near real-time on a weekly basis for only areas and property types relevant to them.

## Files & Folders
- **monitor_funcs.py:** Contains the function which scrape RightMove using BeautifulSoup.
- **price_scrape_plot.py:** Contains the code which calls the scraping functions, manages the data, and produces the visualisations.
- **Areas of Ldn monitored.png:** An image of the areas of London the original monitor focuses on scraping. 
- **data (folder):** Where the data is saved.
- **charts (folder):** Contains all past price charts.

## Usage
Users can change the areas monitored, type of properties, and other variables in the monitor functions. Areas can be specified in `monitor_funcs.py` by inputting the RightMove area/station code (found in RightMove search weblink) and the radius around that area/station. Users can also tailor their search by other parameters (e.g. no. bedrooms) in the `scrape_results_page` function. Currently the programme is set up to monitor 2 bedroom houses/flats/apartments that have been posted in last 7 days in the following 5 non-overlapping areas (defined by a distance from a tube station): 
- Kentish Town (1 mile)
- Royal Oak (1 mile)
- Finchley Road (1 mile)
- Angel (1 mile)
- Mornington Crescent (0.5 miles)

It is advisable to run the program on a Sunday since the scraper is set up to extract properties uploaded in the last 7 days and virtually no estate agents upload to RightMove. Thus the tool can be complemented with crontab code to schedule the scraping and analysis to a time that suits the user on a Sundday. For instance `00 12 * * SUN` for Sunday midday.