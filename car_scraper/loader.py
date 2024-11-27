# car_scraper/loader.py

import json
import logging
from pathlib import Path
from typing import List, Dict
from .car_model import CarModel, CarVariant
from .config import LOG_DIR, LOG_FILE_LOADER

# Configure logging for the loader
def setup_logging():
    """
    Configures logging for the loader module.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_LOADER, mode='w', encoding='utf-8'),
            # logging.StreamHandler()  # Enable console logging
        ]
    )



def load_brand_data(brand: str, base_dir: str = './car_data') -> List[CarModel]:
    brand_folder = brand.lower().replace(" ", "_")
    json_path = Path(base_dir) / brand_folder / 'info.json'
    
    if not json_path.exists():
        logging.error(f"No data found for brand '{brand}' at {json_path}")
        return []
    
    try:
        with json_path.open('r', encoding='utf-8') as f:
            cars_data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON for brand '{brand}': {e}")
        return []
    
    car_models = []
    for car_dict in cars_data:
        car_model = CarModel.from_dict(car_dict)
        car_models.append(car_model)
    
    logging.info(f"Loaded {len(car_models)} car models for brand '{brand}'")
    return car_models

def load_all_data(base_dir: str = './car_data') -> Dict[str, List[CarModel]]:
    base_path = Path(base_dir)
    if not base_path.exists():
        logging.error(f"Base directory '{base_dir}' does not exist.")
        return {}
    
    all_data = {}
    for brand_dir in base_path.iterdir():
        if brand_dir.is_dir():
            brand = brand_dir.name.replace("_", " ").title()
            json_path = brand_dir / 'info.json'
            if json_path.exists():
                try:
                    with json_path.open('r', encoding='utf-8') as f:
                        cars_data = json.load(f)
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON for brand '{brand}': {e}")
                    continue
                
                car_models = [CarModel.from_dict(car_dict) for car_dict in cars_data]
                all_data[brand] = car_models
                logging.info(f"Loaded {len(car_models)} car models for brand '{brand}'")
            else:
                logging.warning(f"No 'info.json' found for brand directory '{brand_dir.name}'")
    
    return all_data

setup_logging()