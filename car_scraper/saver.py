# car_scraper/saver.py

import json
import logging
from pathlib import Path
from .car_model import CarModel

def save_brand_data(brand: str, cars_list: list, base_dir: str = './car_data'):
    """
    Saves the list of Car objects to a JSON file within a brand-specific directory.

    Args:
        brand (str): The car brand identifier.
        cars_list (list): List of Car objects.
        base_dir (str): The base directory where all brand folders are stored.
    """
    if not cars_list:
        logging.warning(f"No car data to save for brand {brand}.")
        return

    # Use pathlib to handle paths
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)  # Ensure the base directory exists

    # Normalize brand name for folder (lowercase, replace spaces with underscores)
    brand_folder = brand.lower().replace(" ", "_")
    brand_dir = base_path / brand_folder
    brand_dir.mkdir(parents=True, exist_ok=True)  # Create brand directory

    # Define the path for the JSON file
    json_path = brand_dir / 'info.json'

    # Convert Car objects to dictionaries
    cars_data = [car.to_dict() for car in cars_list]

    # Write data to JSON file
    with json_path.open('w', encoding='utf-8') as f:
        json.dump(cars_data, f, ensure_ascii=False, indent=4)

    logging.info(f"Saved data for brand {brand} to {json_path}")
