# car_scraper/config.py

from pathlib import Path
from datetime import datetime

CAR_DATA_DIR = Path('./car_data')
LOG_DIR = Path('./logs')

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

LOG_FILE_SCRAPER = LOG_DIR / f'scraper_{get_timestamp()}.log'
LOG_FILE_LOADER = LOG_DIR / f'loader_{get_timestamp()}.log'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                  'AppleWebKit/537.36 (KHTML, like Gecko) ' 
                  'Chrome/115.0.0.0 Safari/537.36'
}

