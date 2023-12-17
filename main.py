from scraper import Scraper

def main()->None:
    scraper = Scraper()
    scraper.scrape_page1()
    scraper.scrape_page2()
    scraper.scrape_page3()
    

if __name__ == "__main__":
    main()