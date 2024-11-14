# car_scraper/car_model.py

class CarVariant:
    def __init__(self, trim_name, price, body_type, engine_cc, horsepower, fuel_type):
        self.trim_name = trim_name
        self.price = price
        self.body_type = body_type
        self.engine_cc = engine_cc
        self.horsepower = horsepower
        self.fuel_type = fuel_type

    def to_dict(self):
        """
        Converts the CarVariant object into a dictionary for JSON serialization.
        """
        return {
            'trim_name': self.trim_name,
            'price': self.price,
            'body_type': self.body_type,
            'engine_cc': self.engine_cc,
            'horsepower': self.horsepower,
            'fuel_type': self.fuel_type
        }

    def __str__(self):
        return f"{self.trim_name} - {self.price} - {self.body_type} - {self.engine_cc}cc - {self.horsepower}hp - {self.fuel_type}"

    def __repr__(self):
        return self.__str__()


class CarModel:
    def __init__(self, brand, model_name, year, price_range, url):
        self.brand = brand
        self.model_name = model_name
        self.year = year
        self.price_range = price_range
        self.url = url
        self.variants = []  # List of CarVariant objects

    def add_variant(self, variant: CarVariant):
        self.variants.append(variant)

    def to_dict(self):
        """
        Converts the CarModel object into a dictionary for JSON serialization.
        """
        return {
            'brand': self.brand,
            'model_name': self.model_name,
            'year': self.year,
            'price_range': self.price_range,
            'url': self.url,
            'variants': [variant.to_dict() for variant in self.variants]
        }

    def __str__(self):
        return f"{self.year} {self.brand} {self.model_name} with {len(self.variants)} variants"

    def __repr__(self):
        return self.__str__()