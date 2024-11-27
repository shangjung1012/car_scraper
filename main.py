# main.py

import logging
import time
import random
from pathlib import Path
from car_scraper.scraper import setup_session, get_car_brands, get_cars_of_brand
from car_scraper.saver import save_brand_data
from car_scraper.config import HEADERS, LOG_DIR, LOG_FILE_SCRAPER

def setup_logging():
    """
    Configures the logging settings.
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_SCRAPER, mode='w', encoding='utf-8'),
            logging.StreamHandler()  # Enable console logging
        ]
    )

def main():
    """
    Main function to orchestrate the scraping and saving process.
    """
    setup_logging()
    logging.info("Starting the car scraper.")

    # Setup session with retries
    session = setup_session()

    # Fetch car brands
    brands = get_car_brands(session, HEADERS)
    if not brands:
        logging.critical("No car brands found. Exiting.")
        return

    for brand in brands:
        logging.info(f"Starting scraping for brand: {brand.capitalize()}")
        cars = get_cars_of_brand(session, HEADERS, brand)

        if not cars:
            logging.info(f"No cars found for brand {brand.capitalize()}.")
        else:
            logging.info(f"Total cars found for {brand.capitalize()}: {len(cars)}")
            # Save the brand's data to a local JSON file
            save_brand_data(brand, cars)
        
        # Optional: Delay between brands to avoid overwhelming the server
        time.sleep(random.uniform(0, 2))

    logging.info("Scraping and saving to files completed successfully.")

if __name__ == "__main__":
    main()
