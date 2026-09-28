"""
Script Name: 10-database_task.py
Purpose: Final grand finale application! An interactive OOP Python application 
         that integrates SQLite database persistence, table creation, parameterized queries, 
         duplicate record prevention (Data Quality Gate), and automated CSV analytics.
"""

from datetime import datetime
import os
import re
from collections import Counter
import csv
import json
import xml.etree.ElementTree as ET
import sqlite3

# -------------------------------------------------------------------------
# Path Configuration & Module-Level Constants
# -------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))  # Root of the repo

WEEKS_PER_MONTH = 4
MIN_FREQUENCY = 1
MAX_FREQUENCY = 7

# Files stored locally in 10-database folder
OUTPUT_FILENAME = os.path.join(CURRENT_DIR, "newsfeed.txt")
DATABASE_FILENAME = os.path.join(CURRENT_DIR, "newsfeed.db")
DEFAULT_TXT_FILE = os.path.join(CURRENT_DIR, "records", "default_input.txt")
DEFAULT_JSON_FILE = os.path.join(CURRENT_DIR, "records", "default_input.json")
DEFAULT_XML_FILE = os.path.join(CURRENT_DIR, "records", "default_input.xml")
WORD_COUNT_CSV = os.path.join(CURRENT_DIR, "word_count.csv")
LETTER_COUNT_CSV = os.path.join(CURRENT_DIR, "letter_count.csv")


# -------------------------------------------------------------------------
# Database Handler Class (New in Module 10)
# -------------------------------------------------------------------------
class DatabaseHandler:
    """Manages SQLite database connection, table creation, deduplication checks, and record insertions."""

    def __init__(self, db_path: str = DATABASE_FILENAME):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self) -> None:
        """Connects to SQLite and creates tables if they do not already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Table for News
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS news
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               text
                               TEXT
                               NOT
                               NULL,
                               city
                               TEXT
                               NOT
                               NULL,
                               publish_date
                               TEXT
                               NOT
                               NULL
                           )
                           """)

            # Table for Private Ads
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS private_ad
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               text
                               TEXT
                               NOT
                               NULL,
                               expiration_date
                               TEXT
                               NOT
                               NULL,
                               days_left
                               INTEGER
                               NOT
                               NULL
                           )
                           """)

            # Table for Unique Record (Sports Frequence)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS sports_frequence
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               text
                               TEXT
                               NOT
                               NULL,
                               frequency_per_week
                               INTEGER
                               NOT
                               NULL,
                               monthly_days
                               INTEGER
                               NOT
                               NULL
                           )
                           """)
            conn.commit()

    def insert_news(self, text: str, city: str, publish_date: str) -> bool:
        """Checks for duplicates and inserts a News record if unique."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # DQE Quality Gate: Check if exact text already exists
            cursor.execute("SELECT * FROM news WHERE text = ?", (text,))
            if cursor.fetchone():
                print(f"[Duplicate Warning] News record already exists in database. Skipping: '{text[:40]}...'")
                return False

            cursor.execute(
                "INSERT INTO news (text, city, publish_date) VALUES (?, ?, ?)",
                (text, city, publish_date)
            )
            conn.commit()
            print("[Database] News record successfully inserted into SQLite.")
            return True

    def insert_private_ad(self, text: str, expiration_date: str, days_left: int) -> bool:
        """Checks for duplicates and inserts a Private Ad record if unique."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Quality Gate: Check if exact text and expiration date match
            cursor.execute("SELECT * FROM private_ad WHERE text = ? AND expiration_date = ?", (text, expiration_date))
            if cursor.fetchone():
                print(f"[Duplicate Warning] Private Ad already exists in database. Skipping: '{text[:40]}...'")
                return False

            cursor.execute(
                "INSERT INTO private_ad (text, expiration_date, days_left) VALUES (?, ?, ?)",
                (text, expiration_date, days_left)
            )
            conn.commit()
            print("[Database] Private Ad successfully inserted into SQLite.")
            return True

    def insert_sports_frequence(self, text: str, frequency_per_week: int, monthly_days: int) -> bool:
        """Checks for duplicates and inserts a Sports Frequence record if unique."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Quality Gate: Check if exact sport text and frequency match
            cursor.execute("SELECT * FROM sports_frequence WHERE text = ? AND frequency_per_week = ?",
                           (text, frequency_per_week))
            if cursor.fetchone():
                print(f"[Duplicate Warning] Sports record already exists in database. Skipping: '{text[:40]}...'")
                return False

            cursor.execute(
                "INSERT INTO sports_frequence (text, frequency_per_week, monthly_days) VALUES (?, ?, ?)",
                (text, frequency_per_week, monthly_days)
            )
            conn.commit()
            print("[Database] Sports Frequence record successfully inserted into SQLite.")
            return True


# -------------------------------------------------------------------------
# CSV Report Generator Class (Analytics Module)
# -------------------------------------------------------------------------
class CsvReportGenerator:
    """Handles parsing newsfeed.txt and generating word_count.csv and letter_count.csv reports."""

    def __init__(self, newsfeed_path: str = OUTPUT_FILENAME):
        self.newsfeed_path = newsfeed_path

    def generate_reports(self) -> None:
        """Reads newsfeed.txt, computes analytics, and exports word_count.csv and letter_count.csv."""
        if not os.path.exists(self.newsfeed_path):
            return

        try:
            with open(self.newsfeed_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
                return

            # --- Part 1: Word Count Report ---
            words = re.findall(r'\b\w+\b', text.lower())
            word_counts = Counter(words)

            with open(WORD_COUNT_CSV, 'w', encoding='utf-8') as csvfile:
                for word, count in word_counts.items():
                    csvfile.write(f"{word}-{count}\n")

            # --- Part 2: Letter Analytics Report ---
            total_letters = 0
            letter_all_counts = Counter()
            letter_upper_counts = Counter()

            for char in text:
                if char.isalpha():
                    total_letters += 1
                    lower_char = char.lower()
                    letter_all_counts[lower_char] += 1
                    if char.isupper():
                        letter_upper_counts[lower_char] += 1

            with open(LETTER_COUNT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['letter', 'count_all', 'count_uppercase', 'percentage']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for char_code in range(ord('a'), ord('z') + 1):
                    letter = chr(char_code)
                    count_all = letter_all_counts[letter]
                    count_uppercase = letter_upper_counts[letter]

                    percentage = (count_all / total_letters * 100) if total_letters > 0 else 0.0
                    percentage_str = f"{percentage:.1f}%"

                    writer.writerow({
                        'letter': letter,
                        'count_all': count_all,
                        'count_uppercase': count_uppercase,
                        'percentage': percentage_str
                    })

            print(f"[Analytics] Successfully updated CSV reports in '{CURRENT_DIR}'!")

        except Exception as e:
            print(f"[Error] Failed to generate analytics reports: {e}")


# -------------------------------------------------------------------------
# Base Class (Parent)
# -------------------------------------------------------------------------
class Publication:
    """Base class for all publication types, handling shared file appending and database integration."""

    def __init__(self, text: str):
        self.text = text
        self.db_handler = DatabaseHandler()

    def generate_body(self) -> str:
        """To be overridden by child classes."""
        raise NotImplementedError("Subclasses must implement generate_body()")

    def save_to_database(self) -> bool:
        """To be overridden by child classes to perform database insertion."""
        raise NotImplementedError("Subclasses must implement save_to_database()")

    def publish(self, filename: str = OUTPUT_FILENAME) -> None:
        """Runs the Data Quality Gate (inserts into DB if unique), appends to text file, and triggers CSV reports."""
        # 1. Attempt database storage & deduplication check
        inserted = self.save_to_database()
        if not inserted:
            print("[Notice] Record was blocked by the Data Quality Gate (Duplicate). Not added to text feed.")
            return

        # 2. Append to text log if unique
        content = self.generate_body()
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(content + "\n")
        print(f"[Success] Record successfully published to newsfeed.txt!")

        # 3. Trigger CSV analytics update
        reporter = CsvReportGenerator(filename)
        reporter.generate_reports()


# -------------------------------------------------------------------------
# Child Classes
# -------------------------------------------------------------------------
class News(Publication):
    """Represents a news article with city and publication timestamp."""

    def __init__(self, text: str, city: str):
        super().__init__(text)
        self.city = city
        self.publish_time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    def generate_body(self) -> str:
        display_time = datetime.strptime(self.publish_time_str, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
        return (
            "News -------------------------\n"
            f"{self.text}\n"
            f"{self.city}, {display_time}\n"
            "------------------------------"
        )

    def save_to_database(self) -> bool:
        return self.db_handler.insert_news(self.text, self.city, self.publish_time_str)


class PrivateAd(Publication):
    """Represents a private advertisement with expiration date and days-left calculation."""

    def __init__(self, text: str, expiration_date_str: str):
        super().__init__(text)
        self.expiration_date_str = expiration_date_str
        self.exp_date = self.parse_date(expiration_date_str)

    @staticmethod
    def calculate_days_left(exp_date: datetime) -> int:
        delta = exp_date - datetime.now()
        return max(0, delta.days)

    @staticmethod
    def parse_date(date_str: str) -> datetime:
        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError("Invalid date format. Expected YYYY-MM-DD or DD/MM/YYYY.")

    def generate_body(self) -> str:
        days_left = self.calculate_days_left(self.exp_date)
        formatted_exp_date = self.exp_date.strftime("%d/%m/%Y")
        return (
            "Private Ad -------------------\n"
            f"{self.text}\n"
            f"Actual until: {formatted_exp_date}, {days_left} days left\n"
            "------------------------------"
        )

    def save_to_database(self) -> bool:
        days_left = self.calculate_days_left(self.exp_date)
        return self.db_handler.insert_private_ad(self.text, self.exp_date.strftime("%Y-%m-%d"), days_left)


class SportsFrequence(Publication):
    """Represents sports activity frequency, calculating monthly practice days."""

    def __init__(self, text: str, frequency_per_week: int):
        super().__init__(text)
        self.frequency_per_week = frequency_per_week
        self.monthly_days = frequency_per_week * WEEKS_PER_MONTH

    def generate_body(self) -> str:
        return (
            "Sports Frequence -------------\n"
            f"Sport / Activity: {self.text}\n"
            f"Practice frequency: {self.frequency_per_week} days/week\n"
            f"Estimated monthly practice: {self.monthly_days} days/month (approx. {WEEKS_PER_MONTH} weeks)\n"
            "------------------------------"
        )

    def save_to_database(self) -> bool:
        return self.db_handler.insert_sports_frequence(self.text, self.frequency_per_week, self.monthly_days)


# -------------------------------------------------------------------------
# Batch File Readers (TXT, JSON, XML)
# -------------------------------------------------------------------------
class TxtFileReader:
    """Handles batch reading of text files."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path.strip() if file_path else DEFAULT_TXT_FILE

    def process_file(self) -> None:
        if not os.path.exists(self.file_path):
            print(f"\n[Error] File not found at '{self.file_path}'.")
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            raw_records = content.split('---')
            success_count = 0
            for record_text in raw_records:
                lines = [line.strip() for line in record_text.strip().splitlines() if line.strip()]
                if not lines:
                    continue
                rec_type = lines[0].lower()
                if "news" in rec_type and len(lines) >= 3:
                    News(lines[1], lines[2]).publish()
                    success_count += 1
                elif "private ad" in rec_type and len(lines) >= 3:
                    PrivateAd(lines[1], lines[2]).publish()
                    success_count += 1
                elif "sports" in rec_type and len(lines) >= 3 and lines[2].isdigit():
                    SportsFrequence(lines[1], int(lines[2])).publish()
                    success_count += 1
            if success_count > 0:
                os.remove(self.file_path)
                print(f"\n[Success] Processed {success_count} record(s) and deleted input file.")
        except Exception as e:
            print(f"\n[Error] {e}")


class JsonFileReader:
    """Handles batch reading of JSON files."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path.strip() if file_path else DEFAULT_JSON_FILE

    def process_file(self) -> None:
        if not os.path.exists(self.file_path):
            print(f"\n[Error] File not found at '{self.file_path}'.")
            return
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            success_count = 0
            for record in records:
                rec_type = record.get("type", "").strip().lower()
                if rec_type == "news":
                    News(record.get("text", ""), record.get("city", "")).publish()
                    success_count += 1
                elif rec_type in ["private ad", "privatead", "ad"]:
                    PrivateAd(record.get("text", ""), record.get("expiration_date", "")).publish()
                    success_count += 1
                elif rec_type in ["sports frequence", "sports", "sport"]:
                    SportsFrequence(record.get("text", ""), record.get("frequency_per_week", 0)).publish()
                    success_count += 1
            if success_count > 0:
                os.remove(self.file_path)
                print(f"\n[Success] JSON batch complete! Processed {success_count} record(s) and deleted input file.")
        except json.JSONDecodeError as jde:
            print(f"\n[Error] JSON Syntax Error: {jde}")
        except Exception as e:
            print(f"\n[Error] {e}")


class XmlFileReader:
    """Handles batch reading of XML files."""

    def __init__(self, file_path: str = ""):
        self.file_path = file_path.strip() if file_path else DEFAULT_XML_FILE

    def process_file(self) -> None:
        if not os.path.exists(self.file_path):
            print(f"\n[Error] File not found at '{self.file_path}'.")
            return
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            success_count = 0
            for record in root:
                rec_type = record.attrib.get("type", "").strip().lower()
                if not rec_type:
                    rec_type = record.tag.strip().lower()
                text_elem = record.find("text")
                text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

                if "news" in rec_type:
                    city_elem = record.find("city")
                    city = city_elem.text.strip() if city_elem is not None and city_elem.text else ""
                    News(text, city).publish()
                    success_count += 1
                elif "private" in rec_type or "ad" in rec_type:
                    exp_date = record.attrib.get("expiration_date", "")
                    if not exp_date:
                        exp_elem = record.find("expiration_date")
                        if exp_elem is not None and exp_elem.text:
                            exp_date = exp_elem.text.strip()
                    PrivateAd(text, exp_date).publish()
                    success_count += 1
                elif "sport" in rec_type:
                    freq_val = record.attrib.get("frequency_per_week", "")
                    if not freq_val:
                        freq_elem = record.find("frequency_per_week")
                        if freq_elem is not None and freq_elem.text:
                            freq_val = freq_elem.text.strip()
                    SportsFrequence(text, int(freq_val)).publish()
                    success_count += 1
            if success_count > 0:
                os.remove(self.file_path)
                print(f"\n[Success] XML batch complete! Processed {success_count} record(s) and deleted input file.")
        except ET.ParseError as pe:
            print(f"\n[Error] XML Syntax Error: {pe}")
        except Exception as e:
            print(f"\n[Error] {e}")


# -------------------------------------------------------------------------
# Interactive Terminal Menu
# -------------------------------------------------------------------------
def main():
    print("========================================")
    print(" NEWS FEED & ENTERPRISE DATABASE API  ")
    print("========================================")

    while True:
        print("\nSelect an option:")
        print("1 - Add News (Interactive)")
        print("2 - Add Private Ad (Interactive)")
        print("3 - Add Sports Frequence (Interactive)")
        print("4 - Process records from TXT file")
        print("5 - Process records from JSON file")
        print("6 - Process records from XML file")
        print("7 - Force Regenerate CSV Reports")
        print("0 - Exit")

        choice = input("Enter your choice (0-7): ").strip()

        if choice == '0':
            print("\nExiting. Have a great day!")
            break
        elif choice == '1':
            text = input("Enter news text: ").strip()
            city = input("Enter city: ").strip()
            if text and city:
                News(text, city).publish()
            else:
                print("[Error] Fields cannot be empty.")
        elif choice == '2':
            text = input("Enter ad description: ").strip()
            exp_date = input("Enter expiration date (YYYY-MM-DD or DD/MM/YYYY): ").strip()
            if text and exp_date:
                try:
                    PrivateAd(text, exp_date).publish()
                except ValueError as e:
                    print(f"[Error] {e}")
            else:
                print("[Error] Fields cannot be empty.")
        elif choice == '3':
            text = input("Enter sport name/details: ").strip()
            freq_input = input(f"Enter frequency ({MIN_FREQUENCY}-{MAX_FREQUENCY} days/week): ").strip()
            if text and freq_input.isdigit():
                SportsFrequence(text, int(freq_input)).publish()
            else:
                print("[Error] Invalid input.")
        elif choice == '4':
            path_input = input(f"Enter TXT batch path (Press Enter for default): ").strip()
            TxtFileReader(path_input).process_file()
        elif choice == '5':
            path_input = input(f"Enter JSON batch path (Press Enter for default): ").strip()
            JsonFileReader(path_input).process_file()
        elif choice == '6':
            path_input = input(f"Enter XML batch path (Press Enter for default): ").strip()
            XmlFileReader(path_input).process_file()
        elif choice == '7':
            print("\n[Processing] Forcing regeneration of CSV analytics reports...")
            CsvReportGenerator().generate_reports()
        else:
            print("[Error] Invalid choice!")


if __name__ == "__main__":
    main()