"""
Script Name: geo_distance_calculator.py
Purpose: Final Course Project - An interactive Geo-Distance Calculator tool that
         queries an SQLite knowledge base, dynamically learns and stores missing city coordinates,
         and calculates real-world straight-line distance using the Haversine formula.
"""

import sqlite3
import math
import os

# -------------------------------------------------------------------------
# Path Configuration & Constants
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILENAME = os.path.join(CURRENT_DIR, "cities.db")
EARTH_RADIUS_KM = 6371.0


# -------------------------------------------------------------------------
# Database Knowledge Base Handler
# -------------------------------------------------------------------------
class CityDatabaseHandler:
    """Manages SQLite connection, table creation, and coordinate lookups/insertions."""

    def __init__(self, db_path: str = DATABASE_FILENAME):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self) -> None:
        """Creates the cities table if it does not already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT UNIQUE NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL
                )
            """)
            conn.commit()

    def get_city_coordinates(self, city_name: str) -> tuple[float, float] | None:
        """Queries the database for a city's latitude and longitude (case-insensitive)."""
        normalized_name = city_name.strip().title()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT latitude, longitude FROM cities WHERE city_name = ?",
                (normalized_name,)
            )
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
        return None

    def insert_city(self, city_name: str, latitude: float, longitude: float) -> None:
        """Inserts a new city and its coordinates into the SQLite database."""
        normalized_name = city_name.strip().title()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cities (city_name, latitude, longitude) VALUES (?, ?, ?)",
                (normalized_name, latitude, longitude)
            )
            conn.commit()


# -------------------------------------------------------------------------
# Spherical Geometry Calculation (Haversine Formula)
# -------------------------------------------------------------------------
def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points
    on the Earth specified in decimal degrees using the Haversine formula.
    """
    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula computation
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = EARTH_RADIUS_KM * c
    return distance


# -------------------------------------------------------------------------
# Coordinate Input Helper with Validation
# -------------------------------------------------------------------------
def prompt_for_coordinates(city_name: str) -> tuple[float, float]:
    """Interactively prompts the user for valid float latitude and longitude."""
    formatted_city = city_name.strip().title()
    print(f"\n[!] '{formatted_city}' is not in the database. Please provide coordinates:")

    while True:
        try:
            lat_input = input(f"> Enter Latitude for {formatted_city}: ").strip()
            latitude = float(lat_input)
            if not (-90 <= latitude <= 90):
                print("[Error] Latitude must be between -90 and 90 degrees.")
                continue
            break
        except ValueError:
            print("[Error] Invalid input. Please enter a valid decimal number for latitude.")

    while True:
        try:
            lon_input = input(f"> Enter Longitude for {formatted_city}: ").strip()
            longitude = float(lon_input)
            if not (-180 <= longitude <= 180):
                print("[Error] Longitude must be between -180 and 180 degrees.")
                continue
            break
        except ValueError:
            print("[Error] Invalid input. Please enter a valid decimal number for longitude.")

    return latitude, longitude


# -------------------------------------------------------------------------
# Main Application Flow
# -------------------------------------------------------------------------
def main():
    db = CityDatabaseHandler()

    print("========================================")
    print("   WELCOME TO THE GEO-DISTANCE TOOL     ")
    print("========================================")

    while True:
        print("\n----------------------------------------")
        origin_input = input("Enter Origin City (or type 'exit' to quit): ").strip()
        if origin_input.lower() == 'exit':
            print("\nExiting Geo-Distance Calculator. Goodbye!")
            break

        destination_input = input("Enter Destination City: ").strip()
        if destination_input.lower() == 'exit':
            print("\nExiting Geo-Distance Calculator. Goodbye!")
            break

        if not origin_input or not destination_input:
            print("[Error] City names cannot be empty. Please try again.")
            continue

        # --- Check or Learn Origin City ---
        origin_coords = db.get_city_coordinates(origin_input)
        if origin_coords is None:
            lat1, lon1 = prompt_for_coordinates(origin_input)
            db.insert_city(origin_input, lat1, lon1)
            print(f"[+] {origin_input.strip().title()} successfully saved to the database!")
            origin_coords = (lat1, lon1)
        else:
            lat1, lon1 = origin_coords

        # --- Check or Learn Destination City ---
        dest_coords = db.get_city_coordinates(destination_input)
        if dest_coords is None:
            lat2, lon2 = prompt_for_coordinates(destination_input)
            db.insert_city(destination_input, lat2, lon2)
            print(f"[+] {destination_input.strip().title()} successfully saved to the database!")
            dest_coords = (lat2, lon2)
        else:
            lat2, lon2 = dest_coords

        # --- Calculate Distance ---
        distance_km = calculate_haversine_distance(lat1, lon1, lat2, lon2)

        # --- Display Results ---
        print("\n--- Result ---")
        print(f"The distance between {origin_input.strip().title()} and {destination_input.strip().title()} is approximately {distance_km:.1f} kilometers.")
        print("--------------")


if __name__ == "__main__":
    main()