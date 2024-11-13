# car_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import json
import logging
from pathlib import Path
import time
import random
from .car import Car

def setup_session():
    """
    Sets up a requests session with retry strategy.
    """
    session = requests.Session()
    retry_strategy = requests.packages.urllib3.util.retry.Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_car_brands(session, headers) -> list:
    """
    Fetches the list of car brands from the used cars page.

    Args:
        session (requests.Session): The requests session object.
        headers (dict): HTTP headers to use for the request.

    Returns:
        list: A list of car brand identifiers.
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


# not implemented
def get_car_details(session, headers, car_url: str) -> dict:
    """
    Fetches detailed information of a car from its detail page.

    Args:
        session (requests.Session): The requests session object.
        headers (dict): HTTP headers to use for the request.
        car_url (str): The URL of the car's detail page.

    Returns:
        dict: A dictionary containing detailed car information.
    """
    try:
        res = session.get(car_url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch car details from {car_url}: {e}")
        return {}

    soup = BeautifulSoup(res.text, 'html.parser')

    # Extract detailed information based on the actual HTML structure
    # The following selectors are placeholders and should be adjusted to match the website's HTML
    try:
        model = soup.find('h1', class_='car-model').text.strip()
        year = int(soup.find('span', class_='car-year').text.strip())
        engine_type = soup.find('span', class_='engine-type').text.strip()
        fuel_efficiency = soup.find('span', class_='fuel-efficiency').text.strip()
        horsepower = int(soup.find('span', class_='horsepower').text.strip())
        torque = int(soup.find('span', class_='torque').text.strip())
        acceleration = float(soup.find('span', class_='acceleration').text.strip())
        top_speed = int(soup.find('span', class_='top-speed').text.strip())
        crash_test_rating = soup.find('span', class_='crash-test-rating').text.strip()
        airbag_count = int(soup.find('span', class_='airbag-count').text.strip())
        seating_capacity = int(soup.find('span', class_='seating-capacity').text.strip())
        infotainment = soup.find('span', class_='infotainment').text.strip()
        upholstery = soup.find('span', class_='upholstery').text.strip()
        lighting = soup.find('span', class_='lighting').text.strip()

        return {
            'model': model,
            'year': year,
            'engine_type': engine_type,
            'fuel_efficiency': fuel_efficiency,
            'horsepower': horsepower,
            'torque': torque,
            'acceleration': acceleration,
            'top_speed': top_speed,
            'crash_test_rating': crash_test_rating,
            'airbag_count': airbag_count,
            'seating_capacity': seating_capacity,
            'infotainment': infotainment,
            'upholstery': upholstery,
            'lighting': lighting
        }
    except AttributeError as e:
        logging.error(f"Failed to parse car details from {car_url}: {e}")
        return {}
    except ValueError as e:
        logging.error(f"Invalid data format in car details from {car_url}: {e}")
        return {}

def get_cars_of_brand(session, headers, brand: str) -> list:
    """
    Fetches the list of cars for a specific brand and returns a list of Car objects.

    Args:
        session (requests.Session): The requests session object.
        headers (dict): HTTP headers to use for the request.
        brand (str): The car brand identifier.

    Returns:
        list: A list of Car objects for the specified brand.
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
                # title_tag = car_soup.find('span', class_='title') or car_soup.find('h2', class_='model-name')
                title_tag = car_soup.find('span', class_='title')
                price_tag = car_soup.find('span', class_='price')
                link_tag = car_soup.find('a', href=True)

                if title_tag and price_tag and link_tag:
                    title = title_tag.text.strip()
                    price = price_tag.text.strip()
                    url = link_tag['href'].strip()

                    '''
                    # Fetch detailed car information from the detail page
                    car_detail = get_car_details(session, headers, url)
                    if not car_detail:
                        logging.warning(f"Failed to get details for car: {title}")
                        continue
                    '''


                    # Create a Car object and add it to the list
                    car = Car(
                        brand=brand.capitalize(),
                        # model=car_detail['model'],
                        model=title,
                        price=price,  # You can choose to use 'year' or other details as needed
                        url=url
                    )
                    cars_list.append(car)

                    logging.info(f"Added car: {car}")
                else:
                    logging.warning("Incomplete car information, skipping.")
            except Exception as e:
                logging.error(f"Error parsing car HTML: {e}")
                continue

        # Delay between requests to avoid rate limiting
        time.sleep(random.uniform(0, 1))

    return cars_list
