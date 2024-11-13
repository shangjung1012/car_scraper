import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", mode='w'),
        # logging.StreamHandler()
    ]
)

# Setup a session with retries
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Fixed User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                  'AppleWebKit/537.36 (KHTML, like Gecko) ' 
                  'Chrome/115.0.0.0 Safari/537.36'
}


class Car:
    def __init__(self, brand, model, price, url):
        self.brand = brand
        self.model = model
        self.price = price
        self.url = url

    def __str__(self):
        return f'{self.brand} {self.model} {self.price} {self.url}'

    def __repr__(self):
        return self.__str__()

def get_car_brands() -> list:
    """
    Fetches the list of car brands from the used cars page.
    """
    url = 'https://autos.yahoo.com.tw/used-cars/'
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch car brands: {e}")
        return []
    
    soup = BeautifulSoup(res.text, 'html.parser')
    brands = soup.find(id='usedcar_make_id')
    
    if not brands:
        logging.error("Could not find the brands dropdown in the HTML.")
        return []
    
    car_brands = [option.get('value') for option in brands.find_all('option') if option.get('value')]
    logging.info(f"Retrieved car brands: {car_brands}")
    return car_brands

def get_cars_of_brand(brand) -> list:
    """
    Fetches the list of cars for a specific brand and returns a list of Car objects.
    """
    cars_list = []
    url = f'https://autos.yahoo.com.tw/new-cars/make/{brand}'

    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch brand page for {brand}: {e}")
        return cars_list

    soup = BeautifulSoup(res.text, 'html.parser')

    # Extract available years for the brand
    year_titles = soup.find_all('div', class_='year-title')
    if not year_titles:
        logging.warning(f"No year titles found for brand {brand}.")
        return cars_list

    years = [year_title.text.strip() for year_title in year_titles]
    logging.info(f"Found years for {brand}: {years}")

    for year in years:
        logging.info(f"Processing year: {year}")
        api_url = f'https://autos.yahoo.com.tw/ajax/api_car_make/{brand}?year={year}'

        try:
            response = session.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            cars_json = response.json()
        except requests.RequestException as e:
            logging.error(f"Request failed for year {year}: {e}")
            continue
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON for year {year}")
            continue

        # Clean and parse each car's HTML
        for car_html in cars_json:
            try:
                car_html_clean = car_html.replace('\\', '')
                car_soup = BeautifulSoup(car_html_clean, 'html.parser')

                # Extract car details
                title_tag = car_soup.find('span', class_='title') or car_soup.find('h2', class_='model-name')
                price_tag = car_soup.find('span', class_='price')
                link_tag = car_soup.find('a', href=True)

                if title_tag and price_tag and link_tag:
                    title = title_tag.text.strip()
                    price = price_tag.text.strip()
                    url = link_tag['href'].strip()

                    # You might need to parse the model more accurately
                    model = title  # Modify this if you can extract model separately

                    # Create a Car object and add it to the list
                    car = Car(brand=brand.capitalize(), model=model, price=price, url=url)
                    cars_list.append(car)

                    logging.info(f"Added car: {car}")
                else:
                    logging.warning("Incomplete car information, skipping.")
            except Exception as e:
                logging.error(f"Error parsing car HTML: {e}")
                continue

        # Delay between requests to avoid rate limiting
        time.sleep(random.uniform(1, 3))

    return cars_list

def main():
    # Example usage: Get all Mazda cars
    brand = 'mazda'
    cars = get_cars_of_brand(brand)

    if not cars:
        logging.info(f"No cars found for brand {brand.capitalize()}.")
    else:
        logging.info(f"\nTotal cars found for {brand.capitalize()}: {len(cars)}")
        for car in cars:
            print(car)

if __name__ == "__main__":
    main()
