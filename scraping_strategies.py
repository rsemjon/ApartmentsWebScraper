from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from models import Apartment
import re

class WebsiteScrapingStrategy(ABC):

    @abstractmethod
    def get_page_url(self, page_number: int) -> str:
        pass

    @abstractmethod
    def extract_apartments(self, soup: BeautifulSoup) -> list[Apartment]:
        pass

    def modify_adr(self, adr:str)->str:
        replacements = ["Bratislava", "okres", " I ", " II ", " III ", " IV ", " V ", "-", " ", ",", "(I)", "(II)", "(III)", "(IV)", "(V)"]

        new_adr = adr
        for replacement in replacements:
            new_adr = new_adr.replace(replacement, "")

        return new_adr.lower()
    

    def add_provision(self, price:str)->float:
        if "+" in price:
            prices = price.split("+")
            apartment_price = float(re.sub(r'[^0-9.]', '', prices[0].replace(",", ".").strip()))
            provision = float(re.sub(r'[^0-9.]', '', prices[1].replace(",", ".").strip()))
            return apartment_price + provision
        
        return float(re.sub(r'[^0-9.]', '', price.replace(",", ".").strip()))




class NehnutelnostiSkStrategy(WebsiteScrapingStrategy):

    def get_page_url(self, page_number: int) -> str:
        return f"https://www.nehnutelnosti.sk/bratislava/byty/predaj/?p[page]={page_number}"

    def extract_apartments(self, soup: BeautifulSoup) -> list[Apartment]:
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
                title = apartment.find("h2").get_text().strip()
                adr = self.modify_adr(adr)
                price = round(float(re.sub(r'[^0-9.]', '', price)), 2)
                price_for_m2 = float(re.sub(r'[^0-9.]', '', price_for_m2))
                total_area = round(float(re.sub(r'[^0-9.]', '', total_area)))

                list_of_apartments.append(Apartment(link=link, title=title, adr=adr, price=price, price_for_m2=price_for_m2, total_area=total_area))
            except Exception as e:
                print(f"Missing apartment information")
        
        return list_of_apartments


class RealitySkStrategy(WebsiteScrapingStrategy):

    def get_page_url(self, page_number: int) -> str:
        return f"https://www.reality.sk/byty/bratislava/predaj/?page={page_number}"

    def extract_apartments(self, soup: BeautifulSoup) -> list[Apartment]:
        offers = soup.find("div", class_="offer_list")
        apartments_in_offers = offers.findAll("div", class_="offer")
        list_of_apartments = []

        for apartment in apartments_in_offers:
            try:

                params = apartment.find("p", class_="offer-params").findAll()
                price = apartment.find("p", class_="offer-price").get_text().replace(apartment.find("p", class_="offer-price").find("small").get_text(), "").replace(",", ".").strip()
                adr  = params[1].get_text().strip().replace("|", "") + apartment.find("a", class_="offer-location").get_text().strip().replace("Reality", "")
                total_area =  params[2].get_text().strip().replace("|", "").replace(",", ".").replace("m2", "")
                price_for_m2 = apartment.find("p", class_="offer-price").find("small").get_text().strip().replace(",", ".")
                
                link = "https://www.reality.sk" + "/" + apartment.find("div", class_="offer-body").find("a").get("href")
                title = apartment.find("h2", class_="offer-title").get("title").strip()
                adr = self.modify_adr(adr)
                price = round(float(re.sub(r'[^0-9.]', '', price)), 2)
                price_for_m2 = float(re.sub(r'[^0-9.]', '', price_for_m2))
                total_area = round(float(re.sub(r'[^0-9.]', '', total_area)))
        
                list_of_apartments.append(Apartment(link=link, title=title, adr=adr, price=price, price_for_m2=price_for_m2, total_area=total_area ))
            except Exception as e:
                print(f"Missing apartment information")
            
        return list_of_apartments


class TopRealitySkStrategy(WebsiteScrapingStrategy):

    def get_page_url(self, page_number: int) -> str:
        return f"https://www.topreality.sk/vyhladavanie-nehnutelnosti-{page_number}.html?type%5B0%5D=101&type%5B1%5D=108&type%5B2%5D=102&type%5B3%5D=103&type%5B4%5D=104&type%5B5%5D=105&type%5B6%5D=106&type%5B7%5D=109&type%5B8%5D=110&type%5B9%5D=107&type%5B10%5D=113&form=1&obec=1000000"


    def extract_apartments(self, soup: BeautifulSoup) -> list[Apartment]:
        offers = soup.find("div", class_="listing-items")
        apartments_in_offers = offers.findAll("div", {"data-ga4-container-event" : "view_item_list"})
        list_of_apartments = []

        for apartment in apartments_in_offers:
            try:
                adr  = apartment.find("div", class_ = "location").get_text().strip()
                price_plus_provision = apartment.find("strong", class_="price").get_text().strip()
                price_for_m2 = apartment.find("span", class_="priceArea").get_text().strip().replace(",", ".")
                total_area = apartment.find("span", class_="value").get_text().strip().replace(",", ".").replace("m2", "")

                link = apartment.find("a").get("href")
                title = apartment.find("h2").get_text().strip()
                adr = self.modify_adr(adr)
                price = round(self.add_provision(price_plus_provision), 2)
                price_for_m2 = float(re.sub(r'[^0-9.]', '', price_for_m2))
                total_area = round(float(re.sub(r'[^0-9.]', '', total_area)))
        
                list_of_apartments.append(Apartment(link=link, title=title, adr=adr, price=price, price_for_m2=price_for_m2, total_area=total_area))
            except Exception as e:
                print(f"Missing apartment information")
              
        return list_of_apartments
