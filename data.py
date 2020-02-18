import re

class Airport:
    id = 0
    code = ""
    name = ""
    city = ""
    country = ""
    latitude = 0.0
    longtitude = 0.0

    def __init__(self,
                 id: int,
                 code: str,
                 name: str,
                 city: str,
                 country: str,
                 latitude: float,
                 longtitude: float):
        self.id = id
        self.code = code
        self.name = name
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longtitude = longtitude

    def __str__(self) -> str:
        return f"{self.id}. \"{self.name}\" (code {self.code}) in {self.city}, {self.country} ({self.longtitude}, {self.latitude})"

