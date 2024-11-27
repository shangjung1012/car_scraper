# load_data.py

import argparse
from car_scraper.loader import load_brand_data, load_all_data
from car_scraper.car_model import CarModel, CarVariant

def display_car_models(car_models: list):
    """
    Displays information about a list of CarModel objects.

    Args:
        car_models (list): List of CarModel objects.
    """
    for car in car_models:
        print(f"\n{car}")
        for variant in car.variants:
            print(f"  - {variant}")

def main():
    parser = argparse.ArgumentParser(description="Load and display car data.")
    parser.add_argument(
        '--brand',
        type=str,
        help="Specify a car brand to load data for. If not provided, all brands will be loaded."
    )
    args = parser.parse_args()

    if args.brand:
        # Load data for a specific brand
        car_models = load_brand_data(args.brand)
        if car_models:
            print(f"\nCar Models for Brand: {args.brand.capitalize()}")
            display_car_models(car_models)
        else:
            print(f"No data available for brand '{args.brand}'.")
    else:
        # Load data for all brands
        all_data = load_all_data()
        if all_data:
            for brand, car_models in all_data.items():
                print(f"\nCar Models for Brand: {brand}")
                display_car_models(car_models)
        else:
            print("No car data available.")

if __name__ == "__main__":
    main()
