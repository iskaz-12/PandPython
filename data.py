import re

class City:
    name = ""
    country = ""
    latitude = 0.0
    longtitude = 0.0

    pop = 1.0
    sus = 1.0
    inf = 0.0
    rec = 0.0
    old_sus = 1.0
    old_inf = 0.0
    old_rec = 0.0

    def __init__(self,
                 name: str,
                 country: str,
                 latitude: float,
                 longtitude: float):
        self.id = id
        self.name = name
        self.country = country
        self.latitude = latitude
        self.longtitude = longtitude
        self.airports = []
        self.pop = 1.0
        self.sus = 1.0
        self.inf = 0.0
        self.rec = 0.0
        self.old_sus = 1.0
        self.old_inf = 0.0
        self.old_rec = 0.0

    def __str__(self) -> str:
        return f"City {self.name} of {self.country} ({self.longtitude}, {self.latitude}) with {len(self.airports)} airport(s)"

