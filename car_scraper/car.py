# car_scraper/car.py

class Car:
    def __init__(self, brand, model, price, url):
        self.brand = brand
        self.model = model
        self.price = price
        self.url = url

    def to_dict(self):
        """
        Converts the Car object into a dictionary for JSON serialization.
        """
        return {
            'brand': self.brand,
            'model': self.model,
            'price': self.price,
            'url': self.url
        }

    def __str__(self):
        return f"{self.brand} {self.model} - {self.price} - {self.url}"

    def __repr__(self):
        return self.__str__()
