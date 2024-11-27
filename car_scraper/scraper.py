# car_scraper/scraper.py

import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import random
from pathlib import Path
from .car_model import CarModel, CarVariant


def setup_session():
    """
    Sets up a requests session with a retry strategy.
    """
    session = requests.Session()
    retry_strategy = requests.packages.urllib3.util.retry.Retry(
        total=5,                                     # Total number of retries
        backoff_factor=1,                           # Wait time multiplier between retries
        status_forcelist=[429, 500, 502, 503, 504], # HTTP status codes to retry on
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # HTTP methods to retry
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


def parse_price(price_str: str) -> float:
    """
    Parses the price string and converts it to a float representing the price in 萬.

    Args:
        price_str (str): Price string (e.g., "93.8 萬").

    Returns:
        float: Price in 万.
    """
    try:
        # Remove any commas and currency symbols
        price = price_str.replace(',', '').replace('萬', '').strip()
        return float(price)
    except (ValueError, AttributeError):
        logging.warning(f"Unable to parse price from string: '{price_str}'")
        return 0.0


def get_car_variants(session, headers, car_url: str) -> list:
    """
    Fetches detailed information of a car from its detail page, handling multiple variants.

    Args:
        session (requests.Session): The requests session object.
        headers (dict): HTTP headers to use for the request.
        car_url (str): The URL of the car's detail page.

    Returns:
        list: A list of CarVariant objects containing detailed car variant information.
    """
    try:
        res = session.get(car_url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch car details from {car_url}: {e}")
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    specifications = soup.find_all('li', class_='model-sub')

    variants = []
    for spec in specifications:
        try:
            trim = spec.find('div', class_='model-title').text.strip()
            details = spec.find('ul').find_all('li')

           
            # fuel car
            if len(details) == 7:
                body_type = details[0].text.strip()
                price = spec.find_all('span')[1].text.strip() if len(spec.find_all('span')) > 1 else 'Unknown Price'
                engine_cc = details[2].text.strip()
                horsepower = details[4].text.strip()
                fuel_type = details[6].text.strip()
                
            # electric car(for tesla)
            elif len(details) == 5:
                body_type = details[0].text.strip()
                price = spec.find_all('span')[1].text.strip() if len(spec.find_all('span')) > 1 else 'Unknown Price'
                engine_cc = details[2].text.strip()
                horsepower = 'Unknown Horsepower'
                fuel_type = details[4].text.strip()

            else:
                # Ensure there are enough details
                logging.warning(f"Insufficient details for variant '{trim}' in URL: {car_url}")
                continue

           
            variant = CarVariant(
                trim_name=trim,
                price=price,
                body_type=body_type,
                # engine_cc=int(engine_cc) if engine_cc.isdigit() else 0,
                engine_cc=engine_cc,
                # horsepower=int(horsepower) if horsepower.isdigit() else 0,
                horsepower=horsepower,
                fuel_type=fuel_type
            )

            variants.append(variant)
        except AttributeError as e:
            logging.error(f"Failed to parse variant details from {car_url}: {e}")
            continue
        except ValueError as e:
            logging.error(f"Invalid data format in variant details from {car_url}: {e}")
            continue

    return variants


def get_cars_of_brand(session, headers, brand: str) -> list:
    """
    Fetches the list of cars for a specific brand and returns a list of CarModel objects.

    Args:
        session (requests.Session): The requests session object.
        headers (dict): HTTP headers to use for the request.
        brand (str): The car brand identifier.

    Returns:
        list: A list of CarModel objects for the specified brand.
    """
    car_models = []
    url = f'https://autos.yahoo.com.tw/new-cars/make/{brand.replace(" ", "-")}'

    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch brand page for {brand}: {e}")
        return car_models

    soup = BeautifulSoup(res.text, 'html.parser')

    # Extract available years for the brand
    year_titles = soup.find_all('div', class_='year-title')
    if not year_titles:
        logging.warning(f"No year titles found for brand {brand}.")
        return car_models

    years = [year_title.text.strip() for year_title in year_titles]
    logging.info(f"Found years for {brand}: {years}")

    for year in years:
        logging.info(f"Processing year: {year}")
        api_url = f'https://autos.yahoo.com.tw/ajax/api_car_make/{brand.replace(" ", "-")}?year={year}'

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

                # Extract car model details
                title_tag = car_soup.find('span', class_='title')
                price_range_tag = car_soup.find('span', class_='price')
                link_tag = car_soup.find('a', href=True)

                if title_tag and price_range_tag and link_tag:
                    title = title_tag.text.strip()
                    price_range = price_range_tag.text.strip()
                    url = link_tag['href'].strip()

                    # Extract year and model name from the title
                    # Example: "2024 Audi A3 Sportback"
                    try:
                        year_in_title, model_name = title.split(' ', 1)
                        year_in_title = int(year_in_title)
                    except ValueError:
                        year_in_title = year  # Fallback to the year from the loop
                        model_name = title

                    # Fetch detailed car variants from the detail page
                    car_variants = get_car_variants(session, headers, url)
                    if not car_variants:
                        logging.warning(f"No variants found for car: {title} ({url})")
                        continue

                    # Create a CarModel object
                    car_model = CarModel(
                        brand=brand.capitalize(),
                        model_name=model_name,
                        year=year_in_title,
                        price_range=price_range,
                        url=url
                    )

                    # Add all variants to the CarModel
                    for variant in car_variants:
                        car_model.add_variant(variant)
                        logging.info(f"Added variant: {variant} to model: {car_model}")

                    car_models.append(car_model)
                else:
                    logging.warning("Incomplete car information, skipping.")
            except Exception as e:
                logging.error(f"Error parsing car HTML: {e}")
                continue

        # Delay between requests to avoid rate limiting
        time.sleep(random.uniform(1, 3))

    return car_models
