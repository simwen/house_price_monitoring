# house_price_monitoring

## Summary
This project involves building a tool to monitor local property prices on UK property portal RightMove (https://www.rightmove.co.uk). The tool monitors prices on a weekly basis by scraping the RightMove website and charting prices however the user desires. One can calibrate the tool to monitor prices in any area of the UK, examples currently focus on two areas relevant to me (North Central London and a suburb of Sheffield).

## Motivation
News outlets reporting on house prices and the state of the property market suffers from 2 problems:
- **Timing:** House price changes are often reported annually, quarterly or monthly. This means they can be outdated by the time house prices reach the national press.
- **Non-Specificity:** Reporting on property market is usually at national or regional level and for all property types. However, the housing market can be far more heterogenoeous with different areas within regions or different property types seeing much smaller or larger price changes.
This tool aims to solve both these issues by allowing users to monitor house price changes near real-time on a weekly basis for only areas and property types relevant to them.

## Files & Folders
- **Monitor_funcs.py:** Contains the functions which scrape RightMove using BeautifulSoup.
- **Price_monitor_scrape.py:** Contains the code which calls the scraping functions, wrangles/saves the data, and produces the visualisation.
- **Areas of Ldn monitored.png:** Contains image of the areas of London the original monitor focuses on scraping. Areas chosen due to their relevance to current property search.
- **data (folder):** Contains all historic weekly data in summarised (containing summary stats) and detailed (containing individual properties) form.
- **charts (folder):** Contains all historic weekly charts of median prices.

## Usage
First run `Monitor_funcs.py`, then `Price_monitor_scrape.py`. Users will have to change the directory (`location` variable) and the `last_version` variable to load the right data.

Users can change the areas monitored, type of properties, and other variables in the monitor functions. Currently the programme specifically monitors 2 bedroom houses/flats/apartments that have been posted in last 7 days in the following 5 non-overlapping areas (defined by a distance from a tube station): 
- Kentish Town (1 mile)
- Royal Oak (1 mile)
- Finchley Road (1 mile)
- Angel (1 mile)
- Mornington Crescent (0.5 miles)

It is advisable to run the program on a Sunday since the scraper is set up to extract properties uploaded in the last 7 days and virtually no estate agents upload to RightMove. Thus the tool can be complemented with crontab code to schedule the scraping and analysis to a time that suits the user on a Sundday. For instance `00 12 * * SUN` for Sunday midday.

NB. There are two scrapers in `Monitor_funcs.py`. The first scraper loops through the 4 stations with 1mile radii. Due to the much lower number of properties in 0.5 miles around Mornington Crescent, results rarely go onto a second page meaning I simply created a specific scraping code for it.
