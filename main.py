from scraper import Scraper

def main()->None:
    scraper = Scraper()
    result  = scraper.scrape_page1()
    scraper.write_to_csv(result)
    
if __name__ == "__main__":
    main()