import requests
from bs4 import BeautifulSoup
from dataclasses import asdict
from typing import List
import csv
import os
import scraping_strategies
from models import Apartment



class Scraper:
    def __init__(self)->None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.11 (KHTML, like Gecko) "
            "Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Connection": "keep-alive",
        }


    def scrape_page(self, strategy: scraping_strategies.WebsiteScrapingStrategy)->None:
      
        page_number = 1

        while True:
            try:
                response = requests.get(strategy.get_page_url(page_number=page_number), headers = self.headers).text
                soup = BeautifulSoup(response, 'html.parser')
                apartments = strategy.extract_apartments(soup=soup)

                if not apartments:
                    break
        
                self.write_to_csv(apartments, "./data/all_websites.csv")
            except Exception as e:
                print(f"Problem with writing: {e}")
            page_number += 1
    

    def write_to_csv(self, apartments:List[Apartment], file_name:str)->None:
        isFileCreated = os.path.exists(file_name)
        with open (file_name, "a") as file:
            fieldnames = ["link", "title", "adr", "price","price_for_m2", "total_area" ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not isFileCreated:
                writer.writeheader()
              
            for apartment in apartments:
                writer.writerow(asdict(apartment))
    
        
    