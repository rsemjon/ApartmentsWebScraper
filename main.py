from scraper import Scraper
from scraping_strategies import *

scraper = Scraper()

def main()->None:

    websites = [NehnutelnostiSkStrategy(), RealitySkStrategy(), TopRealitySkStrategy()]

    for website in websites:
        scraper.scrape_page(strategy=website)
    

if __name__ == "__main__":
    main()