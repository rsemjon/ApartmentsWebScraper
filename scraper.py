import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List
import csv
import os
import re

@dataclass
class Apartment:
    link: str
    name: str   
    adr: str
    price: float
    price_for_m2: float
    total_area: float


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


    def scrape_page1(self):
      
        id = 1

        while True:
            try:
                response = requests.get(f"https://www.nehnutelnosti.sk/bratislava/byty/predaj/?p[page]={id}", headers = self.headers).text
                soup = BeautifulSoup(response, 'html.parser')
                apartments = self.extract_page1(soup)

                if not apartments:
                    break
                
                self.write_to_csv(apartments, "./data/work_data/data.csv")
            except Exception as e:
                print(f"Problem with printing: {e}")
            id += 1
        
    def scrape_page2(self):
      
        id = 1

        while True:
            try:
                response = requests.get(f"https://www.reality.sk/byty/bratislava/predaj/?page={id}", headers = self.headers).text
                soup = BeautifulSoup(response, 'html.parser')
                apartments = self.extract_page2(soup)

                if not apartments:
                    break
        
                self.write_to_csv(apartments, "./data/work_data/data.csv")
            except Exception as e:
                print(f"Problem with writing: {e}")
            id += 1
        

    def scrape_page3(self):
      
        id = 1

        while True:
            try:
                if id == 1:
                    response = requests.get(f"https://www.topreality.sk/vyhladavanie-nehnutelnosti.html?form=1&type%5B%5D=101&type%5B%5D=108&type%5B%5D=102&type%5B%5D=103&type%5B%5D=104&type%5B%5D=105&type%5B%5D=106&type%5B%5D=109&type%5B%5D=110&type%5B%5D=107&type%5B%5D=113&obec=1000000&searchType=string&distance=&q=&cena_od=&cena_do=&vymera_od=0&vymera_do=0&n_search=search&page=estate&gpsPolygon=", headers = self.headers).text
                else:
                    response = requests.get(f" https://www.topreality.sk/vyhladavanie-nehnutelnosti-{id}.html?type%5B0%5D=101&type%5B1%5D=108&type%5B2%5D=102&type%5B3%5D=103&type%5B4%5D=104&type%5B5%5D=105&type%5B6%5D=106&type%5B7%5D=109&type%5B8%5D=110&type%5B9%5D=107&type%5B10%5D=113&form=1&obec=1000000&n_search=search&gpsPolygon=&searchType=string", headers = self.headers).text
                
                soup = BeautifulSoup(response, 'html.parser')
                apartments = self.extract_page3(soup)

                if not apartments:
                    break
        
                self.write_to_csv(apartments, "./data/work_data/data.csv")
            except Exception as e:
                print(f"Problem with writing: {e}")
            id += 1
        
    

    def extract_page1(self, soup:BeautifulSoup)->List[Apartment]: #page1 is nehnutelnosti.sk
        offers = soup.find("div", id="inzeraty")
        apartments_in_offers = offers.findAll("div", class_="advertisement-item")
        list_of_apartments = []

        for apartment in apartments_in_offers:
            try:

                adr  = apartment.find("div", class_="advertisement-item--content__info").get_text().strip()
                price = apartment.find("div", class_="advertisement-item--content__price").get("data-adv-price").replace(",", ".")
                price_for_m2 = apartment.find("span", class_="advertisement-item--content__price-unit").get_text().strip().replace(",", ".")
                total_area = apartment.findAll("div", class_="advertisement-item--content__info")[1].find("span").get_text().strip().replace(",", ".").replace("m2", "")
               
                link = apartment.find("a").get("href")
                name = apartment.find("h2").get_text().strip()
                adr = self.modify_adr(adr)
                price = float(re.sub(r'[^0-9.]', '', price))
                price_for_m2 = float(re.sub(r'[^0-9.]', '', price_for_m2))
                total_area = float(re.sub(r'[^0-9.]', '', total_area))
        

                list_of_apartments.append(Apartment(link=link, name=name, adr=adr, price=price, price_for_m2=price_for_m2, total_area=total_area))
            except Exception as e:
                print(f"Problem with extracting informations: {e}")
        
        return list_of_apartments
    

    def extract_page2(self, soup:BeautifulSoup)->List[Apartment]: #page2 is reality.sk
        offers = soup.find("div", class_="offer_list")
        apartments_in_offers = offers.findAll("div", class_="offer")
        list_of_apartments = []

        for apartment in apartments_in_offers:
            try:

                params = apartment.find("p", class_="offer-params").findAll()
                temp_price = apartment.find("p", class_="offer-price").get_text().strip()
                adr  = params[1].get_text().strip().replace("|", "") + apartment.find("a", class_="offer-location").get_text().strip().replace("Reality", "")
                total_area =  params[2].get_text().strip().replace("|", "").replace(",", ".").replace("m2", "")
                price_for_m2 = apartment.find("p", class_="offer-price").find("small").get_text().strip().replace(",", ".")
                price = self.modify_price(temp_price).replace(",", ".")

                link = "https://www.reality.sk" + "/" + apartment.find("div", class_="offer-body").find("a").get("href")
                name = apartment.find("h2", class_="offer-title").get("title").strip()
                adr = self.modify_adr(adr)
                price = float(re.sub(r'[^0-9.]', '', price))
                price_for_m2 = float(re.sub(r'[^0-9.]', '', price_for_m2))
                total_area = float(re.sub(r'[^0-9.]', '', total_area))
        
            
              
                list_of_apartments.append(Apartment(link=link, name=name, adr=adr, price=price, price_for_m2=price_for_m2, total_area=total_area ))
            except Exception as e:
                print(f"Problem with extracting informations: {e}")
            
        return list_of_apartments
    
    
    def extract_page3(self, soup:BeautifulSoup)->List[Apartment]: #page3 is topreality.sk
        offers = soup.find("div", class_="listing-items")
        apartments_in_offers = offers.findAll("div", {"data-ga4-container-event" : "view_item_list"})
        list_of_apartments = []

        for apartment in apartments_in_offers:
            try:
                adr  = apartment.find("div", class_ = "location").get_text().strip()
                price = apartment.find("strong", class_="price").get_text().strip().replace(",", ".")
                price_for_m2 = apartment.find("span", class_="priceArea").get_text().strip().replace(",", ".")
                total_area = apartment.find("span", class_="value").get_text().strip().replace(",", ".").replace("m2", "")

                link = apartment.find("a").get("href")
                name = apartment.find("h2").get_text().strip()
                adr = self.modify_adr(adr)
                price = float(re.sub(r'[^0-9.]', '', price))
                price_for_m2 = float(re.sub(r'[^0-9.]', '', price_for_m2))
                total_area = float(re.sub(r'[^0-9.]', '', total_area))
        
               

                list_of_apartments.append(Apartment(link=link, name=name, adr=adr, price=price, price_for_m2=price_for_m2, total_area=total_area))
            except Exception as e:
                print(f"Problem with extracting informations: {e}")
              
        
        return list_of_apartments

    def write_to_csv(self, apartments:List[Apartment], file_name:str)->None:
        isFileCreated = os.path.exists(file_name)
        with open (file_name, "a") as file:
            fieldnames = ["link", "name", "adr", "price","price_for_m2", "total_area" ]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not isFileCreated:
                writer.writeheader()
              
            for apartment in apartments:
                writer.writerow(asdict(apartment))


    def find_index(self, char:str, string:str)->int:
        for i in range(len(string)):
            if string[i] == char:
                break
        return i
    

    def modify_price(self, price:str)->str:
        if "€" in price:
            return price[:self.find_index("€", price)]
        
    def modify_adr(self, adr:str)->str:
        replacements = ["Bratislava", "okres", " I ", " II ", " III ", " IV ", " V ", "-", " ", ",", "(I)", "(II)", "(III)", "(IV)", "(V)"]

        new_adr = adr
        for replacement in replacements:
            new_adr = new_adr.replace(replacement, "")

        return new_adr.lower()
