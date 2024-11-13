# car_scraper/config.py

from pathlib import Path

BASE_DIR = Path('./cars')
LOG_DIR = Path('./logs')
LOG_FILE = LOG_DIR / 'scraper.log'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                  'AppleWebKit/537.36 (KHTML, like Gecko) ' 
                  'Chrome/115.0.0.0 Safari/537.36'
}
