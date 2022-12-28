# house_price_monitoring

## Summary
This repo contains the a project which monitors the property prices on UK property portal RightMove (https://www.rightmove.co.uk). Currently the project monitors property prices in 5 areas of London on a weekly basis by scraping the RightMove website and charting the weekly average prices.

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

NB. There are two scrapers in `Monitor_funcs.py`. The first scraper loops through the 4 stations with 1mile radii. Due to the much lower number of properties in 0.5 miles around Mornington Crescent, results rarely go onto a second page meaning I simply created a specific scraping code for it.
