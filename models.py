from dataclasses import dataclass

@dataclass
class Apartment:
    link: str
    title: str   
    adr: str
    price: float
    price_for_m2: float
    total_area: float
