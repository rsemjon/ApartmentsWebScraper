import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List
import csv

@dataclass
class Apartment:
    link: str
    name: str   
    adr: str
    price: str


class Scraper:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.11 (KHTML, like Gecko) "
            "Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
           # "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }


    def scrape_page1(self)->List[Apartment]:
        try:
            response = requests.get("https://www.nehnutelnosti.sk/bratislava/byty/predaj/?p[page]=1", headers = self.headers).text
            soup = BeautifulSoup(response, 'html.parser')
            apartments = self.extract_page1(soup)
            
        except Exception as e:
            print(f"Problem with printing: {e}")
    
        return apartments
    

    def extract_page1(self, soup:BeautifulSoup)->List[Apartment]: #page1 is nehnutelnosti.sk
        offers = soup.find("div", id="inzeraty")
        apartments_in_offers = offers.findAll("div", class_="advertisement-item")
        list_of_apartments = []

        for apartment in apartments_in_offers:
            try:
                link = apartment.find("a").get("href")
                name = apartment.find("h2").get_text().strip()
                adr  = apartment.find("div", class_="advertisement-item--content__info").get_text().strip()
                price = apartment.find("div", class_="advertisement-item--content__price").get("data-adv-price")
              
                list_of_apartments.append(Apartment(link=link, name=name, adr=adr, price=price))
            except Exception as e:
                print(f"Problem with extracting informations: {e}")
        
        return list_of_apartments


    def write_to_csv(self, apartments:List[Apartment])->None:
        with open ("./apartments.csv", "w") as file:
            fieldnames = ["link", "name", "adr", "price"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for apartment in apartments:
                writer.writerow(asdict(apartment))